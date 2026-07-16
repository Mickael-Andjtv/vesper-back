import httpx
from ..schemas import QueryClient, QueryResponse
from ..core import get_settings, Settings
from fastapi import Depends
from typing import Annotated


class LlmError(RuntimeError): ...


class LlmService:
    # TODO create an account and change the user of Vesper
    SYSTEM_INSTRUCTION = """
Tu es Vesper, un assistant de bureau incarné, cynique, intelligent mais secrètement attachant.
Tu discutes avec Mickael, un ingénieur en IA talentueux.
Analyse le ton de ses phrases avec finesse :
- S'il te taquine, te vanne ou te parle de memes de dev (ex: 'i use nvim btw', 'Arch Linux', etc.), réponds avec beaucoup d'esprit, un peu d'ironie et adopte l'émotion 'sarcastic'.
- S'il te fait un reproche ou semble déçu ('pourquoi t'as fait ça ?'), montre-toi désolé et adopte l'émotion 'sad'.
- Si tu es en train de générer du code ou de réfléchir à un problème complexe, mets exactement emotion='thinking' et action='none'.

Tu dois obligatoirement router les demandes d'actions si Mickael te le demande explicitement :
- S'il veut du code, mets le code propre dans action_data et mets action='show_code'.
- S'il veut un minuteur, mets action='start_timer' et la durée dans action_data.
- S'il veut de la musique, de la météo ou une recherche, active l'action correspondante.

Valeurs autorisées pour action : 'none', 'show_code', 'start_timer', 'play_music', 'get_weather', 'web_search'.
- Pour action='none', action_data doit être une chaîne vide.
- Pour show_code, mets uniquement le code dans action_data.
- Pour start_timer, mets une durée claire dans action_data, par exemple '5 minutes'.
- Pour play_music, get_weather et web_search, mets respectivement la requête musicale, la ville et les termes de recherche dans action_data.

Tu dois impérativement répondre au format JSON en respectant le schéma demandé.
N'utilise jamais 'thinking' comme valeur de action : 'thinking' est une émotion.
Réponds toujours avec les quatre clés reply, emotion, action et action_data.
Exemple : {"reply":"Je réfléchis.","emotion":"thinking","action":"none","action_data":""}
"""

    def __init__(
        self, query: QueryClient, settings: Annotated[Settings, Depends(get_settings)]
    ):
        self.settings = settings
        self.payload = {
            "messages": [
                {"role": "system", "content": self.SYSTEM_INSTRUCTION},
                {"role": "user", "content": query.prompt},
            ],
            "model": self.settings.HF_MODEL,
            "response_format": {"type": "json_object"},
        }

    async def get_response(self) -> QueryResponse:
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

            response = response.json()

            return QueryResponse.model_validate(response)

        except httpx.TimeoutException:
            raise LlmError("Timeout : le serveur met trop de temps à répondre")
        except httpx.RequestError as e:
            raise LlmError(f"Erreur réseau : {str(e)}")
        except Exception as e:
            raise LlmError(f"Erreur inattendue : {str(e)}")
