from fastapi import FastAPI, HTTPException
from .services import HuggingFaceError, VesperLLM
from .services.action_service import execute_vesper_action
from .schemas import GenerateRequest


app = FastAPI(title="Vesper API")
llm_service = VesperLLM()


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        result = llm_service.generate(request.prompt, request.max_new_tokens)
        action_status = execute_vesper_action(result.action.value, result.action_data)

        return {
            **result.model_dump(mode="json"),
            "action_status": action_status,
        }

    except HuggingFaceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
