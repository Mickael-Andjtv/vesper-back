from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .services import HuggingFaceError, VesperLLM


app = FastAPI(title="Vesper API")
llm_service =  VesperLLM()

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4_000)
    max_new_tokens: int = Field(default=100, ge=1, le=500)


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        result =llm_service.generate(request.prompt, request.max_new_tokens)
        return {"text": result}
    except HuggingFaceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
