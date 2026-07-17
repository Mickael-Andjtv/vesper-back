from ..schemas import ActionEnum
from .weather_service import Weather
from .llm_service import LlmService



class VesperAction:
    def __init__(self, action: ActionEnum, action_data: str) -> None:
        self.action = action
        self.action_data = action_data

    def execute_action(self):
        if self.action == "get_weather":
            data = self._weather_action()
            return (
                f"Actuellement à {self.action_data}, il fait {data['temp_C']}°C, "
                f"{data['lang_fr'][0]['value'].lower()}. "
                f"L'humidité est de {data['humidity']}% et le vent souffle à "
                f"{data['windspeedKmph']} km/h."
            )
        elif self.action == "web_search":
            return ""
        return ""

    def _weather_action(self):
        data = Weather().get_weather(self.action_data)
        return data

    def _search_action(self):
        pass
