# video_rtp_av

## Node type: source

## Node class name: VideoRtpAv

## Node name: video_rtp_av

## License

- **Code:** this node is part of juturna-nodes, MIT (its `LICENSE` file).
- **PyAV:** BSD-3-Clause (the `License-Expression` of av on PyPI).
- **FFmpeg:** effectively GPL. The PyAV wheels on PyPI bundle their own
  FFmpeg: av 19.0.2 ships FFmpeg 9.0.2 from the
  [pyav-ffmpeg 9.0.2-4 build](https://github.com/PyAV-Org/pyav-ffmpeg/releases/tag/9.0.2-4),
  which links x264 and x265 (GPL-2.0-or-later). The FFmpeg
  [legal page](https://ffmpeg.org/legal.html) says that when its GPL parts
  are used, "the GPL applies to all of FFmpeg". The libraries still report
  "LGPL version 3 or later" only because a pyav-ffmpeg patch to FFmpeg's
  `configure` moves x264 and x265 out of the libraries that need
  `--enable-gpl`. A PyAV built from source against an LGPL build of FFmpeg
  (without x264, x265 or other GPL parts) avoids the GPL. (Checked on
  2026-11-18 on av 19.0.2.)
