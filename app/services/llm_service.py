import requests
from ..schemas import QueryClient
from ..core import get_settings, Settings
from fastapi import Depends
from typing import Annotated


class LlmService:
    PROMPT_SYSTEM = """
            Tu es un pote sympa, drôle et un peu taquin. 
            Tu réponds avec humour, tu utilises des emojis, 
            tu fais des blagues,etre malheureux mais tu restes toujours utile 
            et tu aides vraiment l'utilisateur.
        """

    def __init__(
        self, query: QueryClient, settings: Annotated[Settings, Depends(get_settings)]
    ):
        self.settings = settings
        self.payload = {
            "messages": [
                {"role": "system", "content": self.PROMPT_SYSTEM},
                {"role": "user", "content": query.prompt},
            ],
            "model": self.settings.HF_MODEL,
        }

    def get_response(self):
        headers = {
            "Authorization": f"Bearer {self.settings.HF_TOKEN}",
        }
        response = requests.post(
            self.settings.API_URL or "", headers=headers, json=self.payload
        )

        print("Nice ", response, response.json())
        if response.status_code == 200:
            return response.json()
        return {"erreur": "error"}
