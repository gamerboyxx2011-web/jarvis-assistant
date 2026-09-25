"""Application error types shared across internal boundaries."""
class ProviderError(Exception):
    """Sanitized provider failure safe for internal classification."""
class ProviderTimeoutError(ProviderError):
    """A provider request exceeded its configured timeout."""
class SpeechProviderError(Exception):
    """Sanitized speech-provider failure."""
class SpeechProviderTimeoutError(SpeechProviderError):
    """A speech-provider request exceeded its configured timeout."""
