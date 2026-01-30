from fastapi import FastAPI
from app.api.verify import router as verify_router
from app.api.bot import router as bot_router

app = FastAPI(
    title="TrustLens Backend",
    description="Image & Video Authenticity Verification API",
    version="1.0.0"
)

app.include_router(verify_router, prefix="/api")
app.include_router(bot_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "Backend is running"}
