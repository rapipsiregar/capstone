from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router


app = FastAPI(
    title="Kosmetik Halal NLP & Explainable AI API",
    description="REST API Backend untuk Analisis Kepercayaan Publik terhadap Komunikasi UMKM Kosmetik Halal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Web Dashboard frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming API consumers and pointing to interactive Swagger documentation."""
    return {
        "service": "Kosmetik Halal NLP & Explainable AI REST API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
