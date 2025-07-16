from typing import Callable, Dict, Type, Any
class Container:
    def __init__(self):
        self._providers: Dict[str, Callable[[], Any]] = {}

    def register(self, name: str, provider: Callable[[], Any]):
        self._providers[name] = provider

    def resolve(self, name: str) -> Any:
        provider = self._providers.get(name)
        if not provider:
            raise ValueError(f"No provider registered for '{name}'")
        return provider()

def get_container() -> Container:
    if not hasattr(get_container, "_instance"):
        get_container._instance = Container()
    return get_container._instance


def register_auth_adapter(provider: Callable[[], Any]):
    get_container().register("auth_adapter", provider)

def get_auth_adapter() -> Any:
    return get_container().resolve("auth_adapter")


def register_auth_service(provider=None):
    get_container().register("auth_service", provider)

def get_auth_service():
    return get_container().resolve("auth_service") 