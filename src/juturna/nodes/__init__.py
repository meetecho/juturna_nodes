# noqa: D104
from juturna.components._node_builder._utils import _lazy_node_loaders


_AVAILABLE_PLUGINS: dict[str, str] = {
    # source nodes
    'AudioRtp': '._audio_rtp.audio_rtp',
    'VideoRtp': '._video_rtp.video_rtp',
    'AudioFile': '._audio_file.audio_file',
    'FileWatcher': '._file_watcher.file_watcher',
    'JsonHTTP': '._json_http.json_http',
    'JsonWebsocket': '._json_websocket.json_websocket',
    'BrowserInput': '._browser_input.browser_input',
    # processing nodes
    'VadSilero': '._vad_silero.vad_silero',
    'TranscriberWhisper': '._transcriber_whisper.transcriber_whisper',
    'TranscriberKroko': '._transcriber_kroko.transcriber_kroko',
    'DetectorYolo': '._detector_yolo.detector_yolo',
    'PassthroughIdentity': '._passthrough_identity.passthrough_identity',
    'Warp': '._warp.warp',
    # sink nodes
    'NotifierMongo': '._notifier_mongo.notifier_mongo',
    'NotifierHTTP': '._notifier_http.notifier_http',
    'NotifierUDP': '._notifier_udp.notifier_udp',
    'BrowserOutput': '._browser_output.browser_output',
}


__getattr__, __dir__ = _lazy_node_loaders(__name__, _AVAILABLE_PLUGINS)
__all__ = list(_AVAILABLE_PLUGINS.keys())
