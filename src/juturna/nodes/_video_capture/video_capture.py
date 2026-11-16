"""
VideoCapture

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Read video from a file or a V4L2 webcam, one RGB frame per message.
"""

import pathlib
import time

import av

from juturna.components import Message
from juturna.components import Node
from juturna.meta import JUTURNA_THREAD_JOIN_TIMEOUT
from juturna.names import PixelFormat
from juturna.payloads import ImagePayload


class VideoCapture(Node[ImagePayload, ImagePayload]):
    """Transmit the frames of a video file or of a webcam"""

    def __init__(self, source: str, loop: bool, fps: float, **kwargs):
        """
        Parameters
        ----------
        source : str
            Path of a video file, or a webcam: ``/dev/videoN`` or ``N``.
        loop : bool
            For files only: start again from the beginning at the end of the
            file, instead of stopping.
        fps : float
            Maximum frames per second to transmit, dropping the others. With
            ``0`` every frame is transmitted.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        source = str(source)

        self._path = f'/dev/video{source}' if source.isdigit() else source
        self._camera = self._path.startswith('/dev/video')
        self._loop = loop
        self._fps = fps

        self._container = None
        self._frames = None
        self._origin = 0.0  # monotonic time of pts 0 in the current pass
        self._offset = 0.0  # pts of the start of the current pass
        self._last_pts = 0.0
        self._frame_time = 0.0
        self._next_pts = 0.0  # pts of the next frame to keep, with fps
        self._start = 0.0  # pts of the first frame of the file
        self._opened_at = 0  # frames sent when the source was opened
        self._sent = 0
        self._reader = None  # the source thread, which owns the container

    def warmup(self):
        """Check the source and set the source function"""
        if not self._camera and not pathlib.Path(self._path).is_file():
            raise FileNotFoundError(f'video file not found: {self._path!r}')

        self.set_source(self._next_frame, by=0)

    def update(self, message: Message[ImagePayload], **kwargs):
        """Transmit the frame read by the source function"""
        self.transmit(message)

    def start(self):
        """Start the node, keeping a handle on its source thread"""
        super().start()

        # stop() forgets the thread even when kill() leaves it behind
        self._reader = self._source_thread

    def destroy(self):
        """Close the source, unless a read left behind by kill() still runs"""
        # closing the container under a running read can crash the process:
        # the reader closes it itself when the read returns (_next_frame)
        if self._reader is not None and self._reader.is_alive():
            self.logger.warning('a read is still running, it closes the source')

            return

        self._close()

    def _open(self):
        self._container = av.open(
            self._path,
            format='v4l2' if self._camera else None,
            timeout=JUTURNA_THREAD_JOIN_TIMEOUT,
        )
        stream = self._container.streams.video[0]
        stream.thread_type = 'AUTO'
        rate = stream.average_rate or stream.guessed_rate

        # files may start at any pts (MPEG-TS at 1.4 s, recordings at hours):
        # count from the first one; a camera keeps its device clock
        if self._camera or stream.start_time is None:
            self._start = 0.0
        else:
            self._start = float(stream.start_time * stream.time_base)

        self._frames = self._decoded(stream)
        self._frame_time = float(1 / rate) if rate else 0.0
        self._origin = time.monotonic()
        self._next_pts = 0.0
        self._opened_at = self._sent

        self.logger.info(f'opened {self._path}')

    def _decoded(self, stream):
        # decoded packet by packet, so that a corrupt one does not end the
        # generator, and with it the file
        for packet in self._container.demux(stream):
            # a V4L2 device opened again in the same process starts with an
            # empty packet, which the decoder rejects (EINVAL). In a file the
            # empty packet is the last one, and drains the decoder
            if self._camera and packet.size == 0:
                continue

            try:
                yield from packet.decode()
            except av.error.InvalidDataError:
                self.logger.warning('skipping a corrupt packet')

    def _close(self):
        if self._container is not None:
            self._container.close()

        self._container = None
        self._frames = None

    def _next_frame(self) -> Message[ImagePayload] | None:
        while True:
            try:
                if self._container is None:
                    self._open()

                frame = next(self._frames, None)
            except Exception:
                # the source loop of the node logs it, counts it in health
                # and calls again after a backoff, which reopens the source
                self._close()

                raise

            # stopped during the read: destroy() may have skipped the close
            if self._stop_source_event.is_set():
                self._close()

                return None

            if frame is None:
                if self._camera:
                    self._close()

                    raise OSError(f'{self._path}: the stream ended')

                if not self._end_of_file():
                    return None

                continue

            pts = (frame.time if frame.time is not None else 0.0) - self._start

            # the tolerance keeps frames that fall right on the fps boundary
            if pts < self._next_pts - 1e-3:
                continue

            if self._fps:
                self._next_pts = pts + 1 / self._fps

            self._last_pts = pts

            # a camera is paced by the device, a file by its timestamps
            if not self._camera:
                delay = self._origin + pts - time.monotonic()

                if delay > 0 and self._stop_source_event.wait(delay):
                    return None

            return self._message(frame, self._offset + pts)

    def _end_of_file(self) -> bool:
        """Close the file, and tell whether to read it again"""
        self._close()

        if not self._loop:
            self.logger.info('end of file, stopping the source')
            self._stop_source_event.set()

            return False

        # looping on a file without frames would spin: fail instead, and let
        # the source loop of the node back off
        if self._sent == self._opened_at:
            raise OSError(f'{self._path}: no frames to loop on')

        self._offset += self._last_pts + self._frame_time

        return True

    def _message(self, frame: av.VideoFrame, pts: float) -> Message:
        image = frame.to_ndarray(format=PixelFormat.RGB24)
        message = Message[ImagePayload](
            creator=self.name,
            version=self._sent,
            payload=ImagePayload(
                image=image,
                width=image.shape[1],
                height=image.shape[0],
                depth=image.shape[2],
                pixel_format=PixelFormat.RGB24,
                timestamp=time.time(),
            ),
        )
        message.meta['pts'] = pts
        self._sent += 1

        return message
