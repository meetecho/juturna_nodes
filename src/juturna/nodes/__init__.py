# noqa: D104
from juturna.components._node_builder._utils import _lazy_node_loaders


_AVAILABLE_PLUGINS: dict[str, str] = {
    # source nodes
    'AudioRtp': '._audio_rtp.audio_rtp',
    'VideoRtp': '._video_rtp.video_rtp',
    'VideoCapture': '._video_capture.video_capture',
    'AudioFile': '._audio_file.audio_file',
    'FileWatcher': '._file_watcher.file_watcher',
    'JsonHTTP': '._json_http.json_http',
    'JsonWebsocket': '._json_websocket.json_websocket',
    'BrowserInput': '._browser_input.browser_input',
    'MicSource': '._mic_source.mic_source',
    # processing nodes
    'VadSilero': '._vad_silero.vad_silero',
    'TranscriberWhisper': '._transcriber_whisper.transcriber_whisper',
    'TranscriberKroko': '._transcriber_kroko.transcriber_kroko',
    'TranscriberSherpa': '._transcriber_sherpa.transcriber_sherpa',
    'PrompterOllama': '._prompter_ollama.prompter_ollama',
    'SynthesizerSherpa': '._synthesizer_sherpa.synthesizer_sherpa',
    'DetectorYolo': '._detector_yolo.detector_yolo',
    'DetectorYolox': '._detector_yolox.detector_yolox',
    'DetectionEvents': '._detection_events.detection_events',
    'PassthroughIdentity': '._passthrough_identity.passthrough_identity',
    'Warp': '._warp.warp',
    # sink nodes
    'NotifierMongo': '._notifier_mongo.notifier_mongo',
    'NotifierHTTP': '._notifier_http.notifier_http',
    'NotifierUDP': '._notifier_udp.notifier_udp',
    'NotifierConsole': '._notifier_console.notifier_console',
    'BrowserOutput': '._browser_output.browser_output',
    'AudioWriter': '._audio_writer.audio_writer',
    'SpeakerSink': '._speaker_sink.speaker_sink',
}


__getattr__, __dir__ = _lazy_node_loaders(__name__, _AVAILABLE_PLUGINS)
__all__ = list(_AVAILABLE_PLUGINS.keys())
