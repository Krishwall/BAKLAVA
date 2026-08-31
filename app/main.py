from fastapi import FastAPI

app = FastAPI(
    title="BAKLAVA",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to BAKLAVA API"}
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "BAKLAVA",
    }