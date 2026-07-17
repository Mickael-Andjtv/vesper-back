from fastapi import FastAPI, Depends, HTTPException, Query
from .schemas import QueryClient
from .services import LlmService, PlayMusic, AudioExtractionError, VesperAction
from .core import Settings, get_settings
from typing import Annotated
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.post("/generate")
async def generate(
    query: QueryClient, settings: Annotated[Settings, Depends(get_settings)]
):
    res = await LlmService(query).get_response("g", settings)
    first_reply = res.reply
    action_reply = await VesperAction(
        res.action, res.action_data, settings, query
    ).execute_action()
    res.reply = first_reply if not action_reply else action_reply
    return res


@app.get("/music/stream", name="stream_music")
def stream_music(query: str = Query(min_length=1, max_length=500)):
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
