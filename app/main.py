from fastapi import FastAPI

app = FastAPI()

@app.get("/demands")
async def demands():
    return "hello world :-)"