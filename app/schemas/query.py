from pydantic import BaseModel, model_validator
from .llm_data import EmotionEnum, ActionEnum
import json


class QueryClient(BaseModel):
    prompt: str


class QueryResponse(BaseModel):
    reply: str
    emotion: EmotionEnum
    action: ActionEnum
    action_data: str

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_response(cls, values: dict) -> dict:
        response_loads: dict = json.loads(
            values.get("choices", [])[0].get("message", {}).get("content", "")
        )

        response = response_loads.copy()

        if response["emotion"] not in EmotionEnum._value2member_map_:
            response["emotion"] = EmotionEnum.NEUTRAL.value

        if response["action"] not in ActionEnum._value2member_map_:
            response["action"] = ActionEnum.NONE.value

        if not response.get("action_data"):
            response["action_data"] = ""
        return response
