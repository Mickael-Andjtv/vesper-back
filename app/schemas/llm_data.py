from enum import Enum
import json
import re
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
    "showcode": ActionEnum.SHOW_CODE.value,
    "music": ActionEnum.PLAY_MUSIC.value,
    "playmusic": ActionEnum.PLAY_MUSIC.value,
    "timer": ActionEnum.START_TIMER.value,
    "starttimer": ActionEnum.START_TIMER.value,
    "weather": ActionEnum.GET_WEATHER.value,
    "getweather": ActionEnum.GET_WEATHER.value,
    "search": ActionEnum.WEB_SEARCH.value,
    "websearch": ActionEnum.WEB_SEARCH.value,
    "meteo": ActionEnum.GET_WEATHER.value,
    "minuteur": ActionEnum.START_TIMER.value,
    "musique": ActionEnum.PLAY_MUSIC.value,
    "recherche": ActionEnum.WEB_SEARCH.value,
    "no_action": ActionEnum.NONE.value,
    "nothing": ActionEnum.NONE.value,
}


def normalize_label(value: str) -> str:
    """Normalise getWeather, get-weather et get weather vers get_weather."""
    value = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", value)
    return re.sub(r"[\s-]+", "_", value.strip().lower())


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
            action = normalize_label(action)
            response["action"] = ACTION_ALIASES.get(action, action)
            if response["action"] not in ActionEnum._value2member_map_:
                response["action"] = ActionEnum.NONE.value

        action_data = response.get("action_data")
        if action_data is None:
            response["action_data"] = ""
        elif isinstance(action_data, (dict, list)):
            response["action_data"] = json.dumps(action_data, ensure_ascii=False)
        elif not isinstance(action_data, str):
            response["action_data"] = str(action_data)

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
