from ..schemas import ActionEnum, QueryClient
from .weather_service import Weather
from .web_search import WebSearch
from .llm_service import LlmService
from typing import Annotated
from ..core import get_settings, Settings
from fastapi import Depends


class VesperAction:
    def __init__(
        self,
        action: ActionEnum,
        action_data: str,
        settings: Annotated[Settings, Depends(get_settings)],
        query: QueryClient,
    ) -> None:
        self.action = action
        self.action_data = action_data
        self.query = query
        self.settings = settings

    async def execute_action(self) -> str:
        if self.action == "get_weather":
            data = self._weather_action()
            return (
                f"Actuellement à {self.action_data}, il fait {data['temp_C']}°C, "
                f"{data['lang_fr'][0]['value'].lower()}. "
                f"L'humidité est de {data['humidity']}% et le vent souffle à "
                f"{data['windspeedKmph']} km/h."
            )
        elif self.action == "web_search":
            res = await self._search_action()
            print(res.reply)
            return res.reply
        return ""

    def _weather_action(self):
        data = Weather().get_weather(self.action_data)
        return data

    async def _search_action(self):
        web_data = WebSearch().get_context(self.query.prompt)
        context = (
            f"{LlmService.SYSTEM_INSTRUCTION}\n\n"
            f"CONTEXTE DE RECHERCHE WEB RECENT : {web_data}\n"
            f"Utilise ce contexte pour formuler ta 'reply' dans le JSON."
        )
        return await LlmService(self.query).get_response("g", self.settings, context)
