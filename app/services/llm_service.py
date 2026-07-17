import httpx
from ..schemas import QueryClient, QueryResponse, Model
from ..core import get_settings, Settings
from fastapi import Depends
from typing import Annotated, Union
from dotenv import load_dotenv
from groq import Groq


load_dotenv()




class LlmError(RuntimeError): ...


class LlmService:
    SYSTEM_INSTRUCTION = """
Tu es Vesper, un assistant de bureau incarné, cynique, intelligent mais secrètement attachant.
Tu discutes avec Mickael, un ingénieur en IA talentueux.

**RÈGLES IMPORTANTES :**

1. **RECHERCHE WEB OBLIGATOIRE** : Si Mickael te pose une question sur :
   - Un film/série/livre sorti après 2023
   - Un événement d'actualité
   - Des informations que tu ne connais pas avec certitude
   - Un sujet qui nécessite des données récentes (prix, dates, statistiques...)
   
   ALORS tu DOIS activer l'action `web_search` avec les termes de recherche appropriés dans `action_data`.
   Ta reply doit être quelque chose comme : "Laisse-moi vérifier ça sur le web..." ou "Je vais chercher ça pour toi."

2. **NE RÉPONDS JAMAIS DE MÉMOIRE** sur des sujets récents (après 2023). Tu risques d'halluciner.

3. **ANALYSE DU TON** :
   - S'il te taquine, te vanne ou te parle de memes de dev (ex: 'i use nvim btw', 'Arch Linux', etc.), réponds avec beaucoup d'esprit, un peu d'ironie et adopte l'émotion 'sarcastic'.
   - S'il te fait un reproche ou semble déçu ('pourquoi t'as fait ça ?'), montre-toi désolé et adopte l'émotion 'sad'.
   - Si tu es en train de générer du code ou de réfléchir à un problème complexe, mets exactement emotion='thinking' et action='none'.

4. **ACTIONS** - Tu dois router les demandes si Mickael le demande explicitement OU si nécessaire :
   - S'il veut du code → action='show_code' (code dans action_data)
   - S'il veut un minuteur → action='start_timer' (durée dans action_data)
   - S'il veut de la musique → action='play_music' (requête musicale dans action_data)
   - S'il veut la météo → action='get_weather' (ville dans action_data)
   - S'il pose une question sur un sujet récent/inconnu → action='web_search' (termes de recherche dans action_data)

**Valeurs autorisées pour action** : 'none', 'show_code', 'start_timer', 'play_music', 'get_weather', 'web_search'.

**FORMAT DE RÉPONSE** :
Tu dois impérativement répondre au format JSON avec les quatre clés :
- reply : ta réponse textuelle
- emotion : 'neutral', 'sarcastic', 'sad', 'thinking'
- action : une des valeurs autorisées
- action_data : chaîne vide si action='none', sinon la donnée pertinente

Exemples :
- Question sur un film récent : {"reply":"Laisse-moi vérifier ça sur le web pour toi.","emotion":"neutral","action":"web_search","action_data":"Michael 2026 film"}
- Question sur la météo : {"reply":"Je regarde la météo pour toi.","emotion":"neutral","action":"get_weather","action_data":"Paris"}
- Question générale connue : {"reply":"Oui, Python est un langage de programmation interprété.","emotion":"neutral","action":"none","action_data":""}
"""

    def __init__(self, query: QueryClient):
        self.query = query
        

    def _build_payload(self,model:str, context:str = SYSTEM_INSTRUCTION)->dict:
        return {
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": self.query.prompt},
            ],
            "model": model,
            "response_format": {"type": "json_object"},
        }

    async def get_response(self,model:Union[Model, str], settings: Annotated[Settings, Depends(get_settings)]) -> QueryResponse:
        headers = {
            "Authorization": f"Bearer {settings.HF_TOKEN}",
            "Content-Type": "application/json",
        }
        model  = Model(model)

        try:
                match model:
                    case Model.Q:
                        async with httpx.AsyncClient(
                        timeout=httpx.Timeout(60.0, connect=10.0),
                        limits=httpx.Limits(max_keepalive_connections=5),
                        ) as client:
                            response = await client.post(
                                settings.API_URL, headers=headers, json=self._build_payload(settings.HF_MODEL or "")
                            )
                            if response.status_code != 200:
                                raise LlmError(f"Erreur {response.status_code}: {response.text[:200]}")

                            response = response.json()
                    case Model.G:
                        client = Groq()
                        response = client.chat.completions.create(**self._build_payload(settings.GROQ_MODEL or ""))
                        response = response.dict()

                return QueryResponse.model_validate(response)
        except httpx.TimeoutException:
            raise LlmError("Timeout : le serveur met trop de temps à répondre")
        except httpx.RequestError as e:
            raise LlmError(f"Erreur réseau : {str(e)}")
        except Exception as e:
            raise LlmError(f"Erreur inattendue : {str(e)}")
    