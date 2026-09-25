"""Supported NVIDIA NIM chat models and display metadata."""

from dataclasses import dataclass
from typing import Literal

ModelCategory = Literal["fast", "deep"]


@dataclass(frozen=True, slots=True)
class ChatModel:
    id: str
    name: str
    category: ModelCategory


CHAT_MODELS = (
    ChatModel("z-ai/glm-5-3-flash", "GLM-5.3 Flash", "fast"),
    ChatModel(
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        "Nemotron 3.5 Lightning",
        "fast",
    ),
    ChatModel("z-ai/glm-5-3", "GLM-5.3", "deep"),
    ChatModel(
        "nvidia/nemotron-3-ultra-550b-a55b",
        "Nemotron 3 Ultra",
        "deep",
    ),
)

DEFAULT_MODEL_ID = "z-ai/glm-5-3-flash"
SUPPORTED_MODEL_IDS = frozenset(model.id for model in CHAT_MODELS)
MODEL_BY_ID = {model.id: model for model in CHAT_MODELS}
