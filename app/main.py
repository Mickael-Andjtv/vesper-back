from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from .services import HuggingFaceError, VesperLLM
from .services.action_service import execute_vesper_action
from .services.audio_service import AudioExtractionError, PlayMusic
from .schemas import GenerateRequest


app = FastAPI(title="Vesper API")
llm_service = VesperLLM()


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        result = llm_service.generate(request.prompt, request.max_new_tokens)
        action_status = execute_vesper_action(result.action.value, result.action_data)

        if isinstance(action_status, PlayMusic):
            try:
                action_status.prepare()
            except (AudioExtractionError, ValueError) as error:
                raise HTTPException(status_code=502, detail=str(error)) from error

            return StreamingResponse(
                action_status.stream(),
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=vesper.mp3"},
            )

        return {
            **result.model_dump(mode="json"),
            "action_status": action_status,
        }

    except HuggingFaceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
