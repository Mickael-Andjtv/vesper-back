from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator


class EmotionEnum(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    THINKING = "thinking"
    SARCASTIC = "sarcastic"
    SURPRISED = "surprised"


class ActionEnum(str, Enum):
    NONE = "none"
    SHOW_CODE = "show_code"
    START_TIMER = "start_timer"
    PLAY_MUSIC = "play_music"
    GET_WEATHER = "get_weather"
    WEB_SEARCH = "web_search"


EMOTION_ALIASES = {
    "curious": EmotionEnum.THINKING.value,
}

ACTION_ALIASES = {
    "code": ActionEnum.SHOW_CODE.value,
    "music": ActionEnum.PLAY_MUSIC.value,
    "timer": ActionEnum.START_TIMER.value,
    "weather": ActionEnum.GET_WEATHER.value,
    "search": ActionEnum.WEB_SEARCH.value,
}


class VesperResponse(BaseModel):
    reply: str
    emotion: EmotionEnum
    action: ActionEnum
    action_data: str

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_response(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        response = value.copy()

        if response.get("action") == EmotionEnum.THINKING.value:
            response["action"] = ActionEnum.NONE.value
            response.setdefault("emotion", EmotionEnum.THINKING.value)

        emotion = response.get("emotion")
        if isinstance(emotion, str):
            emotion = emotion.strip().lower()
            response["emotion"] = EMOTION_ALIASES.get(emotion, emotion)
            if response["emotion"] not in EmotionEnum._value2member_map_:
                response["emotion"] = EmotionEnum.NEUTRAL.value

        action = response.get("action")
        if isinstance(action, str):
            action = action.strip().lower()
            response["action"] = ACTION_ALIASES.get(action, action)
            if response["action"] not in ActionEnum._value2member_map_:
                response["action"] = ActionEnum.NONE.value

        response.setdefault(
            "reply",
            response.get("explanation")
            or response.get("content")
            or "Je réfléchis à ta demande.",
        )
        response.setdefault("emotion", EmotionEnum.NEUTRAL.value)
        response.setdefault("action", ActionEnum.NONE.value)
        response.setdefault("action_data", "")
        return response
