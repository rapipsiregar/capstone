from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    timestamp: str = Field(..., json_schema_extra={"example": "2026-09-15T08:00:00Z"})
    service: str = Field(..., json_schema_extra={"example": "Halal Cosmetics NLP & XAI API"})


@router.get("", response_model=HealthResponse)
def check_health():
    """Returns system operational health status, API version, and timestamp."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service="Halal Cosmetics NLP & XAI API"
    )
