"""Small provider registry with NVIDIA as the application default."""

from collections.abc import Callable

from app.providers.base import ChatProvider
from app.providers.nvidia import NVIDIAProvider

ProviderFactory = Callable[[], ChatProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}
        self._default_name: str | None = None

    @property
    def default_name(self) -> str:
        if self._default_name is None:
            raise LookupError("No default provider is registered")
        return self._default_name

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._factories)

    def register(
        self, name: str, factory: ProviderFactory, *, default: bool = False
    ) -> None:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("Provider name must not be blank")
        if normalized_name in self._factories:
            raise ValueError(f"Provider '{normalized_name}' is already registered")
        self._factories[normalized_name] = factory
        if default or self._default_name is None:
            self._default_name = normalized_name

    def create(self, name: str | None = None) -> ChatProvider:
        selected_name = self.default_name if name is None else name.strip().lower()
        try:
            factory = self._factories[selected_name]
        except KeyError as exc:
            raise LookupError(f"Unknown provider '{selected_name}'") from exc
        return factory()


def build_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register("nvidia", NVIDIAProvider, default=True)
    return registry


provider_registry = build_provider_registry()
