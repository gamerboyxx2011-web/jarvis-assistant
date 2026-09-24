"""Application error types shared across internal boundaries."""


class ProviderError(Exception):
    """Sanitized provider failure safe for internal classification."""


class ProviderTimeoutError(ProviderError):
    """A provider request exceeded its configured timeout."""
