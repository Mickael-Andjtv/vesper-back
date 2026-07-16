from fastapi import FastAPI, Depends
from .schemas import QueryClient
from .services import LlmService, PlayMusic
from .core import Settings, get_settings
from typing import Annotated
from collections.abc import  Iterable
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.post("/generate")
async def generate(
    query: QueryClient, settings: Annotated[Settings, Depends(get_settings)]
):
    return await LlmService(query, settings).get_response()

@app.post("/stream/music", response_class=StreamingResponse)
async def streaming_music(query:str)->Iterable[bytes]:
    return PlayMusic(query).stream()
