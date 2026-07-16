from pydantic import BaseModel


class QueryClient(BaseModel):
    prompt: str
