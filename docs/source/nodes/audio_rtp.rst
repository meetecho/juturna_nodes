.. _node-audio-rtp:

``AudioRtp``
============

:bdg-primary:`source` :bdg-secondary-line:`extra: av`

Receive an RTP audio stream with PyAV, resample it, and transmit it in
fixed-length chunks of ``block_size`` seconds.

:Node type: ``AudioRtp``
:Input: --
:Output: ``AudioPayload``
:Extra: ``av``, plus the FFmpeg libraries on the system

.. code-block:: console

    $ pip install "juturna-nodes[av]"

How it works
------------

On warmup the node writes an SDP file, ``_session_in.sdp``, in its pipeline
folder, describing a stream on ``host:port`` with ``payload_type`` and
``encoding_clock_chan``. On start, a worker opens that SDP with PyAV and
listens for RTP packets on the port. Start the pipeline first, then the
sender: packets sent before the node listens are lost, without any error.

The decoded audio is resampled to ``out_rate``, ``out_channels`` and
``resampler_format``, and cut into chunks of ``block_size`` seconds.

The input is opened and read with a timeout of
``JUTURNA_THREAD_JOIN_TIMEOUT`` seconds, 2 s by default (the times below
assume the default). When no packet arrives for 2 s (the sender stopped, or
never started), the node closes the input and opens it again: without traffic
this happens about every 4 s, and only shows up in the log at ``DEBUG`` level
(``demux terminate while reading False``). When the input is closed, the
samples still pending are transmitted as a last chunk, padded with zeros to
``block_size`` when ``flush_partial_on_error`` is true, and dropped otherwise.
If the input cannot be opened at all, for example because another process
uses the port, the node logs ``source unavailable (...), retrying...`` at
``ERROR`` level and tries again every 2 s, until it succeeds or the node
stops.

The UDP receive buffer is 64 KB, so short bursts of packets are not dropped.
``stop()`` returns within a few seconds (up to 3 s in our tests).

Configuration
-------------

Default node arguments, as defined in the node ``config.toml`` file. Any of
them can be overridden in the node ``configuration`` of a pipeline.

.. literalinclude:: ../../../src/juturna/nodes/_audio_rtp/config.toml
    :language: toml

.. list-table::
    :header-rows: 1
    :widths: 25 15 60

    * - Argument
      - Type
      - Description
    * - ``host``
      - ``str``
      - Address the stream is received on
    * - ``port``
      - ``int``
      - UDP port of the stream; ``0`` picks a free port when the node is
        configured
    * - ``payload_type``
      - ``int``
      - RTP payload type of the stream
    * - ``encoding_clock_chan``
      - ``str``
      - Encoding name, clock rate and channels, as in an SDP ``rtpmap`` line
    * - ``out_rate``
      - ``int``
      - Sampling rate of the transmitted audio, in Hz
    * - ``out_channels``
      - ``int``
      - Channels of the transmitted audio
    * - ``resampler_format``
      - ``str``
      - Sample format of the transmitted audio, as named by PyAV: one of
        ``flt``, ``fltp`` (``float32``), ``dbl``, ``dblp`` (``float64``),
        ``s16``, ``s16p``, ``s32``, ``s32p``, ``u8``, ``u8p``
    * - ``block_size``
      - ``int``
      - Length of each chunk, in seconds
    * - ``flush_partial_on_error``
      - ``bool``
      - Transmit the pending samples, padded with zeros, when the input is
        closed

For G.711 µ-law at 8 kHz, as sent by
``ffmpeg ... -ac 1 -ar 8000 -c:a pcm_mulaw -f rtp rtp://127.0.0.1:5004``, use
``payload_type: 0`` and ``encoding_clock_chan: "PCMU/8000"``.

Input message
-------------

The node has no input: it reads the RTP stream.

Output message
--------------

.. list-table::
    :header-rows: 1
    :widths: 30 70

    * - Field
      - Content
    * - ``payload.audio``
      - ``out_rate * block_size`` samples, with the dtype of
        ``resampler_format`` (but see the limits for integer formats); with
        ``out_channels: 2`` the samples are interleaved
    * - ``payload.sampling_rate``
      - ``out_rate``
    * - ``payload.channels``
      - ``out_channels``
    * - ``payload.audio_format``
      - ``resampler_format``
    * - ``payload.start``, ``payload.end``
      - Seconds from the time the input was opened. They start again from
        ``0.0`` every time the input is opened again, so after every pause of
        more than 2 s
    * - ``version``
      - Number of chunks transmitted by the node, from ``0``

``meta`` is empty, and the message has no timers.

Limits
------

- The end of a stream is not propagated downstream: the node only stops
  transmitting. A downstream node waiting for silence, such as
  ``TranscriberSherpa``, keeps its sentence open until more audio comes or the
  pipeline stops.
- With ``out_channels: 2``, ``block_size``, ``start`` and ``end`` count the
  interleaved samples as if they were mono: each chunk holds
  ``block_size / 2`` seconds of audio. Use ``out_channels: 1``.
- With ``out_channels: 1`` and an integer ``resampler_format`` (``s16``,
  ``s32``, ``u8`` and their planar forms), the audio is converted to
  ``float64`` while ``payload.audio_format`` still names the integer format.
  Use ``flt`` or ``dblp``.

Pipeline usage
--------------

.. code-block:: json

    {
      "name": "question",
      "type": "AudioRtp",
      "configuration": {
        "port": 5004,
        "payload_type": 0,
        "encoding_clock_chan": "PCMU/8000",
        "resampler_format": "flt",
        "block_size": 1
      }
    }

Reference
---------

.. autoclass:: juturna.nodes._audio_rtp.audio_rtp.AudioRtp
    :no-index:
