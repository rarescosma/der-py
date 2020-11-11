"""Dead-simple DI registry.

This is used to isolate real side effecting clients (talking to network
services, reading from disk, etc.) from functions that perform some
business logic as well.
"""

import re
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, Pattern, Type, TypeVar

__REGISTRY = {}

Client = TypeVar("Client")

ReturnType = TypeVar("ReturnType")
ToDecorate = Callable[..., ReturnType]
Decorated = Callable[..., ReturnType]
Decorator = Callable[[ToDecorate], Decorated]


def _key(client_class: Type[Client]) -> str:
    return _camel_to_snake(client_class.__name__)


def register(client_class: Type[Client], instance: Client) -> None:
    """Register an instantiated client."""
    __REGISTRY[_key(client_class)] = instance


def deregister(client_class: Type[Client]) -> None:
    """De-register a client."""
    if _key(client_class) not in __REGISTRY:
        raise ValueError(f"Uknown dependency: {client_class}")
    del __REGISTRY[_key(client_class)]


def _default_close(_: Client) -> None:
    pass


def inject(*client_classes: Type[Client]) -> Decorator:
    """Decorate receiving function to inject their dependencies.

    At runtime, the function will receive a single instance
    via the 'client' keyword argument, or, if multiple types are supplied,
    via arguments named after the CamelCase -> snake_case transformations.

    Example:
        >>> from der_py.fun.registry import register, inject
        >>> class SomeDep:
        >>>     side_effect_called = False
        >>>     def side_effect(self) -> None:
        >>>         self.side_effect_called = True
        >>>
        >>> register(SomeDep, SomeDep())
        >>>
        >>> @inject(SomeDep)
        >>> def will_effect(**kwargs) -> bool:
        >>>     assert "client" in kwargs
        >>>     kwargs["client"].side_effect()
        >>>     return kwargs["client"].side_effect_called
        >>>
        >>> will_effect()
        True
    """

    def wrapper(fn: ToDecorate) -> Decorated:
        if not client_classes:
            return fn

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> ReturnType:
            if len(client_classes) == 1:
                _cname = _key(client_classes[0])
                clients_kwargs = (
                    {"client": __REGISTRY[_cname]}
                    if _cname in __REGISTRY
                    else {}
                )
            else:
                clients_kwargs = {
                    _key(_): __REGISTRY[_key(_)]
                    for _ in client_classes
                    if _key(_) in __REGISTRY
                }

            return fn(*args, **{**clients_kwargs, **kwargs})

        return wrapped

    return wrapper


@contextmanager
def client(
    instance_class: Type[Client],
    instance: Client,
    on_close: Callable[[Client], None] = _default_close,
) -> Generator[Client, None, None]:
    """Inject the given dependency using a context manager.

    Can be useful while writing tests to make sure Mocks get injected
    instead of real dependencies.
    """
    register(instance_class, instance)
    yield instance
    on_close(instance)
    deregister(instance_class)


CTS: Pattern = re.compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake(text: str) -> str:
    return CTS.sub("_", text).lower()
