from fastapi import FastAPI
import uvicorn

from core.config import settings
from api import main_router

app = FastAPI(title="Auth-Service")
app.include_router(main_router)


if __name__=="__main__":
    uvicorn.run(
        "main:app",
        host = settings.runtime.host, 
        port = settings.runtime.port,
        reload = settings.runtime.reload,
    )
