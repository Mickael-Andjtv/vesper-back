import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class HuggingFaceError(RuntimeError):
    """Erreur levée lorsqu'un appel au modèle Hugging Face échoue."""


class VesperLLM:
    def __init__(self) -> None:
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_API")
        if not token:
            raise HuggingFaceError(
                "HF_TOKEN est manquant. Ajoute-le dans le fichier .env."
            )

        self.model = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.client = InferenceClient(model=self.model, token=token, provider="auto")

    def generate(self, prompt: str, max_new_tokens: int = 100) -> str:
        try:
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_new_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""
        except Exception as error:
            raise HuggingFaceError(str(error)) from error
