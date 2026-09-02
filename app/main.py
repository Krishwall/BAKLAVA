from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.agents.router import router as agent_router

app = FastAPI(
    title="BAKLAVA",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(app)

app.include_router(agent_router)

@app.get("/")
async def root():
    return {"message": "Welcome to BAKLAVA API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "baklava",
    }