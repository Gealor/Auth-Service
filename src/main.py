from fastapi import FastAPI
import uvicorn

from core.config import settings

app = FastAPI(title="Auth-Service")

@app.get("/hello")
async def hello():
    return {
        "msg": "Hello from FastAPI",
    }

if __name__=="__main__":
    uvicorn.run("main:app", host = settings.runtime.host, port = settings.runtime.port)
