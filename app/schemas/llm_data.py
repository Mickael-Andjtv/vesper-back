from enum import Enum


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


class Model(str, Enum):
    Q = "q"
    G = "g"
