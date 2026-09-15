from fastapi import FastAPI

app = FastAPI(
    title="AI Intrusion Detection System API",
    description="Backend API for the AI-Powered Intrusion Detection System.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Intrusion Detection System Backend",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "AI-IDS Backend",
    }