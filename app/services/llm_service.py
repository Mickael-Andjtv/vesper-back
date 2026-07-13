from huggingface_hub import InferenceClient
from ..core import config


class HuggingFaceError(RuntimeError): ...


class VesperLLM:
    def __init__(self) -> None:
        token = config.HUGGING_FACE_API

        if not token:
            raise HuggingFaceError("token miss")

        self.model = config.HF_MODEL
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
