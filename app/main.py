from fastapi import FastAPI, HTTPException
from .services import HuggingFaceError, VesperLLM
from .schemas import GenerateRequest


app = FastAPI(title="Vesper API")
llm_service = VesperLLM()


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        result = llm_service.generate(request.prompt, request.max_new_tokens)
        return {"text": result}
    except HuggingFaceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
