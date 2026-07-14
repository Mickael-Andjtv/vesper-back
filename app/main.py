from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from .services import HuggingFaceError, VesperLLM
from .services.action_service import execute_vesper_action
from .services.audio_service import AudioExtractionError, PlayMusic
from .schemas import GenerateRequest


app = FastAPI(title="Vesper API")
llm_service = VesperLLM()


@app.get("/music/stream", name="stream_music")
def stream_music(query: str = Query(min_length=1, max_length=500)):
    """Transcode and stream a requested track as MP3."""
    try:
        music = PlayMusic(query)
        music.prepare()
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except AudioExtractionError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return StreamingResponse(
        music.stream(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=vesper.mp3"},
    )


@app.post("/generate")
async def generate_text(request: GenerateRequest, http_request: Request):
    try:
        result = llm_service.generate(request.prompt, request.max_new_tokens)
        action_status = execute_vesper_action(result.action.value, result.action_data)

        if isinstance(action_status, PlayMusic):
            stream_url = http_request.url_for("stream_music")
            stream_url = f"{stream_url}?{urlencode({'query': action_status.query})}"
            return {
                **result.model_dump(mode="json"),
                "action_status": f"Flux musical prêt pour : {action_status.query}",
                "audio_stream_url": stream_url,
            }

        return {
            **result.model_dump(mode="json"),
            "action_status": action_status,
        }

    except HuggingFaceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
