from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4_000)
    max_new_tokens: int = Field(default=100, ge=1, le=500)
