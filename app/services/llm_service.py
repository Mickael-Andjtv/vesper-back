import httpx
from ..schemas import QueryClient
from ..core import get_settings, Settings
from fastapi import Depends
from typing import Annotated


class LlmError(RuntimeError): ...


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

    async def get_response(self):
        headers = {
            "Authorization": f"Bearer {self.settings.HF_TOKEN}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5),
            ) as client:
                response = await client.post(
                    self.settings.API_URL, headers=headers, json=self.payload
                )

            if response.status_code != 200:
                raise LlmError(f"Erreur {response.status_code}: {response.text[:200]}")

            return response.json()

        except httpx.TimeoutException:
            raise LlmError("Timeout : le serveur met trop de temps à répondre")
        except httpx.RequestError as e:
            raise LlmError(f"Erreur réseau : {str(e)}")
        except Exception as e:
            raise LlmError(f"Erreur inattendue : {str(e)}")
