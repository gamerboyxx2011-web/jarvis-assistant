"""Normalized internal response events."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class ResponseStarted:
    type: Literal["response.started"] = "response.started"


@dataclass(frozen=True, slots=True)
class ResponseDelta:
    content: str
    type: Literal["response.delta"] = "response.delta"


@dataclass(frozen=True, slots=True)
class ResponseCompleted:
    usage: Usage | None = None
    type: Literal["response.completed"] = "response.completed"


@dataclass(frozen=True, slots=True)
class ResponseError:
    message: str
    type: Literal["response.error"] = "response.error"


ResponseEvent = ResponseStarted | ResponseDelta | ResponseCompleted | ResponseError
