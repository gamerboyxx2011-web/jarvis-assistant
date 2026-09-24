from app.providers.base import ChatProvider
from app.providers.models import ProviderChatRequest, ProviderDelta, ProviderInfo


class FakeProvider:
    @property
    def info(self):
        return ProviderInfo(
            name="fake",
            model="fake-model",
            configured=True,
            supported_options=frozenset({"message"}),
            capabilities=frozenset({"streaming"}),
        )

    async def stream_chat(self, request: ProviderChatRequest):
        yield ProviderDelta(content=request.message)


def test_fake_provider_satisfies_runtime_contract():
    provider = FakeProvider()
    assert isinstance(provider, ChatProvider)
    assert provider.info.name == "fake"
