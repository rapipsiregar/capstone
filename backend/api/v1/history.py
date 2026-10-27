from typing import List, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.services.database import get_recent_logs, get_analytics_summary, get_total_logs_count


router = APIRouter(tags=["History & Analytics"])


class HistoryResponse(BaseModel):
    count: int
    total: int = 0
    page: int = 1
    total_pages: int = 1
    limit: int = 25
    logs: List[Dict[str, Any]]


class AnalyticsResponse(BaseModel):
    total_reviews: int
    aspect_counts: Dict[str, int]
    trust_counts: Dict[str, int]
    avg_execution_time_ms: float


@router.get("/history", response_model=HistoryResponse)
def get_review_history(
    limit: int = Query(25, ge=1, le=500),
    page: int = Query(1, ge=1)
):
    """Retrieves recent review inference history logs with pagination support."""
    offset = (page - 1) * limit
    logs = get_recent_logs(limit=limit, offset=offset)
    total_count = get_total_logs_count()
    total_pages = max(1, (total_count + limit - 1) // limit)
    return HistoryResponse(
        count=len(logs),
        total=total_count,
        page=page,
        total_pages=total_pages,
        limit=limit,
        logs=logs
    )


@router.get("/analytics", response_model=AnalyticsResponse)
def get_review_analytics():
    """Retrieves analytics aggregate statistics (aspect distribution and trust sentiment distribution)."""
    summary = get_analytics_summary()
    return AnalyticsResponse(
        total_reviews=summary["total_reviews"],
        aspect_counts=summary["aspect_counts"],
        trust_counts=summary["trust_counts"],
        avg_execution_time_ms=summary["avg_execution_time_ms"]
    )
