"""
Models

@ Author: Paolo Saviano
@ Email: psaviano@meetecho.com

Download the files of the known models (sherpa-onnx, YOLOX) into a local cache.
"""

import hashlib
import logging
import os
import pathlib
import tempfile

import requests


_HF = 'https://huggingface.co/{}/resolve/{}/{}'
_STT = 'csukuangfj/sherpa-onnx-streaming-zipformer-en-2023-06-26'
_STT_REV = '672fbf1b30579d6585301139bb363f42a0ad4a24'
_STT_SUFFIX = 'epoch-99-avg-1-chunk-16-left-128.int8.onnx'
_KITTEN = 'csukuangfj2/kitten-nano-en-v0_8-int8'
_KITTEN_REV = '90dfe12687f7822a90e5afc5931b536ba6caf22a'
_RELEASES = 'https://github.com/k2-fsa/sherpa-onnx/releases/download'
_YOLOX = (
    'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0'
)

# model name -> {file name: (url, size in bytes, sha256)}
MODELS: dict[str, dict[str, tuple[str, int, str]]] = {
    'sherpa-onnx-streaming-zipformer-en-2023-06-26': {
        'tokens.txt': (
            _HF.format(_STT, _STT_REV, 'tokens.txt'),
            5048,
            '49e3c2646595fd907228b3c6787069658f67b17377c60aeb8619c4551b2316fb',
        ),
        f'encoder-{_STT_SUFFIX}': (
            _HF.format(_STT, _STT_REV, f'encoder-{_STT_SUFFIX}'),
            71083163,
            '563fde436d16cf7607cf408cd6b30909819d03162652ef389c2450ced3f45ac1',
        ),
        f'decoder-{_STT_SUFFIX}': (
            _HF.format(_STT, _STT_REV, f'decoder-{_STT_SUFFIX}'),
            1307236,
            '98da299f471e38bb4e1a8df579b8cc9122d6039576a77e357b3c60f17dd83b02',
        ),
        f'joiner-{_STT_SUFFIX}': (
            _HF.format(_STT, _STT_REV, f'joiner-{_STT_SUFFIX}'),
            259335,
            'd944208d660d67c8d72cd2acaeac971fa5ceb8c80e76c1968148846fedd6e297',
        ),
    },
    'kitten-nano-en-v0_8-int8': {
        'model.int8.onnx': (
            _HF.format(_KITTEN, _KITTEN_REV, 'model.int8.onnx'),
            24370878,
            '0ba1e21eda9c8bcc4a70ada7e0d27fefc9ba775aaa037547248ec71f9a3d9b7d',
        ),
        'voices.bin': (
            _HF.format(_KITTEN, _KITTEN_REV, 'voices.bin'),
            3276800,
            'd520519c4a3519d44fcfcd943ed0b1e3c5da5cee0eea501d922fac1a93cd24dc',
        ),
        'tokens.txt': (
            _HF.format(_KITTEN, _KITTEN_REV, 'tokens.txt'),
            1064,
            '934a4188addc7665dd3410256bb622169242357fbb99d840d9351209b486dabb',
        ),
    },
    'lexicon-en-us': {
        'lexicon-en-us.txt': (
            f'{_RELEASES}/tts-models/lexicon-en-us.txt',
            6305773,
            '8b67ae549a465eee78f92ecb74644ad90c3c58ce65f19c68baf85878a10ef73a',
        ),
    },
    'yolox_nano': {
        'yolox_nano.onnx': (
            f'{_YOLOX}/yolox_nano.onnx',
            3659407,
            'c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d',
        ),
    },
    'yolox_tiny': {
        'yolox_tiny.onnx': (
            f'{_YOLOX}/yolox_tiny.onnx',
            20219662,
            '427cc366d34e27ff7a03e2899b5e3671425c262ea2291f88bb942bc1cc70b0f7',
        ),
    },
    'yolox_s': {
        'yolox_s.onnx': (
            f'{_YOLOX}/yolox_s.onnx',
            35858002,
            'c5c2d13e59ae883e6af3b45daea64af4833a4951c92d116ec270d9ddbe998063',
        ),
    },
}


def cache_dir() -> pathlib.Path:
    """Folder of the downloaded models"""
    base = os.environ.get('XDG_CACHE_HOME') or pathlib.Path.home() / '.cache'

    return pathlib.Path(base, 'juturna', 'models')


def fetch(name: str, logger: logging.Logger) -> pathlib.Path:
    """
    Return the folder of a known model, downloading the missing files.

    Parameters
    ----------
    name : str
        Model name, a key of ``MODELS``.
    logger : logging.Logger
        Logger for the download messages.

    Returns
    -------
    pathlib.Path
        The model folder in the cache.

    """
    if name not in MODELS:
        raise ValueError(f'unknown model {name!r}, known: {sorted(MODELS)}')

    folder = cache_dir() / name
    folder.mkdir(parents=True, exist_ok=True)

    for file_name, (url, size, sha256) in MODELS[name].items():
        path = folder / file_name

        if path.is_file() and path.stat().st_size == size:
            with path.open('rb') as cached:
                # about 0.2 s for the largest file
                digest = hashlib.file_digest(cached, 'sha256').hexdigest()

            if digest == sha256:
                continue

        logger.info(f'downloading {url} ({size / 1e6:.1f} MB)')
        _download(url, path, size, sha256)

    return folder


def _download(url: str, path: pathlib.Path, size: int, sha256: str):
    # written next to the target and renamed, so a broken download never
    # leaves a partial file under the final name.
    # shortcut: a process killed with SIGKILL leaves its hidden temp file
    # behind, clean them up under a lock if it ever matters
    tmp = tempfile.NamedTemporaryFile(  # noqa: SIM115
        dir=path.parent, prefix=f'.{path.name}.', delete=False
    )
    digest = hashlib.sha256()

    try:
        with tmp, requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()

            for block in response.iter_content(chunk_size=1 << 20):
                tmp.write(block)
                digest.update(block)

                if tmp.tell() > size:
                    raise ValueError(
                        f'{url}: more than the expected {size} bytes'
                    )

        written = os.path.getsize(tmp.name)

        if written != size or digest.hexdigest() != sha256:
            raise ValueError(
                f'{url}: got {written} bytes with sha256 '
                f'{digest.hexdigest()}, expected {size} bytes with sha256 '
                f'{sha256}'
            )

        # temp files are created 0600: let other users read a shared cache
        os.chmod(tmp.name, 0o644)
        os.replace(tmp.name, path)
    except BaseException:
        os.unlink(tmp.name)

        raise
