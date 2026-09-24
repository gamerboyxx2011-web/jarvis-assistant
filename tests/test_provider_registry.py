import pytest

from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderInfo
from app.providers.registry import ProviderRegistry, build_provider_registry


class FakeProvider:
    @property
    def info(self):
        return ProviderInfo("fake", "fake-model", True, frozenset(), frozenset())

    async def stream_chat(self, request: ProviderChatRequest):
        yield ProviderDelta(request.message)


def test_application_registry_defaults_to_nvidia():
    registry = build_provider_registry()
    provider = registry.create()
    assert registry.default_name == "nvidia"
    assert provider.info.name == "nvidia"


def test_registry_supports_injected_fake_provider():
    registry = ProviderRegistry()
    registry.register("fake", FakeProvider, default=True)
    assert isinstance(registry.create(), FakeProvider)


def test_registry_rejects_duplicate_and_unknown_providers():
    registry = ProviderRegistry()
    registry.register("fake", FakeProvider)
    with pytest.raises(ValueError, match="already registered"):
        registry.register("FAKE", FakeProvider)
    with pytest.raises(LookupError, match="Unknown provider"):
        registry.create("missing")
