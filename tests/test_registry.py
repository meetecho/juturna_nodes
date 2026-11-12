import importlib.util
import inspect
import pathlib
import tomllib

import pytest

import juturna.nodes

from juturna.components import Node
from juturna.nodes import _AVAILABLE_PLUGINS


# third-party modules provided by optional extras: a node that fails to import
# one of them is skipped, any other import failure is an error
_OPTIONAL_MODULES = {
    'av',
    'faster_whisper',
    'grpc',
    'silero_vad',
    'torch',
    'ultralytics',
}

_NODE_NAMES = sorted(_AVAILABLE_PLUGINS)


def _node_folder(name: str) -> pathlib.Path:
    spec = importlib.util.find_spec(
        _AVAILABLE_PLUGINS[name], package=juturna.nodes.__name__
    )

    return pathlib.Path(spec.origin).parent


def _node_config(name: str) -> dict:
    with open(_node_folder(name) / 'config.toml', 'rb') as f:
        return tomllib.load(f)


def _node_class(name: str) -> type:
    try:
        return getattr(juturna.nodes, name)
    except ModuleNotFoundError as e:
        if e.name and e.name.split('.')[0] in _OPTIONAL_MODULES:
            pytest.skip(f'{name} needs the optional module {e.name}')

        raise


def test_all_matches_the_registry():
    assert sorted(juturna.nodes.__all__) == _NODE_NAMES
    assert set(_NODE_NAMES) <= set(dir(juturna.nodes))


def test_unknown_node_raises_attribute_error():
    with pytest.raises(AttributeError):
        juturna.nodes.NotANode  # noqa: B018


@pytest.mark.parametrize('name', _NODE_NAMES)
def test_module_path_is_relative_and_private(name):
    path = _AVAILABLE_PLUGINS[name]
    folder, module = path.removeprefix('.').split('.')

    assert path.startswith('._')
    assert folder == f'_{module}'


@pytest.mark.parametrize('name', _NODE_NAMES)
def test_config_has_arguments_and_meta(name):
    config = _node_config(name)

    assert isinstance(config.get('arguments'), dict)
    assert isinstance(config.get('meta'), dict)


@pytest.mark.parametrize('name', _NODE_NAMES)
def test_node_has_a_readme(name):
    readme = _node_folder(name) / 'README.md'

    assert readme.is_file()
    assert readme.read_text().strip()


@pytest.mark.parametrize('name', _NODE_NAMES)
def test_class_matches_the_registry_key(name):
    node_class = _node_class(name)

    assert node_class.__name__ == name
    assert issubclass(node_class, Node)


@pytest.mark.parametrize('name', _NODE_NAMES)
def test_config_arguments_match_the_constructor(name):
    node_class = _node_class(name)
    declared = set(_node_config(name)['arguments'])

    # a node without its own constructor takes no arguments
    if node_class.__init__ is Node.__init__:
        assert not declared

        return

    parameters = [
        p
        for p in inspect.signature(node_class.__init__).parameters.values()
        if p.name != 'self'
    ]
    accepted = {p.name for p in parameters if p.kind is not p.VAR_KEYWORD}

    # the superclass arguments must be forwarded
    assert any(p.kind is p.VAR_KEYWORD for p in parameters)
    # arguments missing from config.toml are silently dropped by the builder,
    # so they can never be set from a pipeline
    assert accepted <= declared, f'not in config.toml: {accepted - declared}'
    # unknown arguments would reach the superclass and fail the build
    assert declared <= accepted, f'not in __init__: {declared - accepted}'
