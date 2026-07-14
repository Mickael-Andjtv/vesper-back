from huggingface_hub import InferenceClient
from ..core import config
from ..schemas import VesperResponse, ActionEnum, EmotionEnum

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

Tu dois impérativement répondre au format JSON en respectant le schéma demandé.
N'utilise jamais 'thinking' comme valeur de action : 'thinking' est une émotion.
Réponds toujours avec les quatre clés reply, emotion, action et action_data.
Exemple : {"reply":"Je réfléchis.","emotion":"thinking","action":"none","action_data":""}
"""


class HuggingFaceError(RuntimeError): ...


class VesperLLM:
    def __init__(self) -> None:
        token = config.HUGGING_FACE_API

        if not token:
            raise HuggingFaceError("token miss")

        self.model = config.HF_MODEL
        self.client = InferenceClient(model=self.model, token=token, provider="auto")

    def generate(self, prompt: str, max_new_tokens: int = 500) -> VesperResponse:
        try:
            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_new_tokens,
                temperature=0.7,
                response_format={
                    "type": "json_object",
                    "value": VesperResponse.model_json_schema(),
                },
            )

            raw_json = response.choices[0].message.content or "{}"

            return VesperResponse.model_validate_json(raw_json)

        except Exception as error:
            print(f"[ERROR HF] Échec de la génération ou du parsing : {error}")
            return VesperResponse(
                reply="Désolé Mickael, mon cerveau a eu un court-circuit. Tu as dit quoi ?",
                emotion=EmotionEnum.SURPRISED,
                action=ActionEnum.NONE,
                action_data="",
            )
