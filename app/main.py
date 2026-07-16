from fastapi import FastAPI, Depends
from .schemas import QueryClient
from .services import LlmService
from .core import Settings, get_settings
from typing import Annotated

app = FastAPI()


@app.post("/generate")
async def generate(
    query: QueryClient, settings: Annotated[Settings, Depends(get_settings)]
):
    print(settings)
    return LlmService(query, settings).get_response()
