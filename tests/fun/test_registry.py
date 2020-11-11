from dataclasses import dataclass
from typing import Tuple, Type, TypeVar, cast

import pytest

from der_py.fun.registry import (
    client as client_ctx,
    deregister,
    inject,
    register,
)

K = TypeVar("K")


@dataclass(frozen=True)
class _MockClient:
    class_prop: int = 43


@pytest.fixture
def _client_factory():
    def _constructor(self, attr_val):
        self.attr = attr_val

    def _factory(type_name, prop_val) -> Tuple[Type[K], K]:
        _client = cast(
            Type[K],
            type(
                type_name,
                (),
                {
                    "__init__": _constructor,
                },
            ),
        )
        return _client, _client(prop_val)

    return _factory


def test_inject_without_parameters():
    @inject()
    def wrapped():
        return 42

    assert wrapped() == 42


def test_inject_single_client():

    register(_MockClient, _MockClient())

    @inject(_MockClient)
    def wrapped(client):
        return client.class_prop

    assert wrapped() == 43


def test_inject_single_client_key():

    register(_MockClient, _MockClient())

    @inject(_MockClient)
    def wrapped(_, *__, **kwargs):
        return kwargs

    assert "client" in wrapped("foo").keys()
    assert isinstance(wrapped("foo")["client"], _MockClient)


@pytest.mark.parametrize(
    "client_class_names, attr_values, expected_kws",
    [
        (["FooClient"], [12], ["client"]),
        (["FooClient", "BarClient"], [12, 23], ["foo_client", "bar_client"]),
        (
            ["Foo23Client", "Bar12Client", "ALongCamel"],
            [12, 23, 45],
            ["foo23_client", "bar12_client", "a_long_camel"],
        ),
    ],
    ids=["single_client", "two_clients", "weird_classes"],
)
def test_inject_multiple(
    _client_factory, client_class_names, attr_values, expected_kws
):
    _client_types = []
    for _ in zip(client_class_names, attr_values):
        _type, _instance = _client_factory(*_)
        register(_type, _instance)
        _client_types.append(_type)

    @inject(*_client_types)
    def wrapped(**kwargs):
        return kwargs

    ret = wrapped()
    for _kw, _attr_value in zip(expected_kws, attr_values):
        assert _kw in ret.keys()
        assert ret[_kw].attr == _attr_value


def test_deregister_nonexistent():
    with pytest.raises(ValueError):
        deregister(type("Foo"))


def test_context_manager(_client_factory):
    _type, _instance = _client_factory("MockClient", 17)
    with client_ctx(_type, _instance) as _client:
        assert isinstance(_client, _type)
        assert _instance == _client
        assert _instance.attr == 17
