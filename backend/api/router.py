from fastapi import APIRouter
from backend.api.v1.health import router as health_router
from backend.api.v1.predict import router as predict_router
from backend.api.v1.explain import router as explain_router
from backend.api.v1.history import router as history_router
from backend.api.v1.brand_analytics import router as brand_analytics_router
from backend.api.v1.dataset_ingest import router as dataset_ingest_router
from backend.api.v1.export_summary import router as export_summary_router
from backend.api.v1.reviews_feed import router as reviews_feed_router
from backend.api.v1.catalog import router as catalog_router
from backend.api.v1.model_metrics import router as model_metrics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(predict_router)
api_router.include_router(explain_router)
api_router.include_router(history_router)
api_router.include_router(brand_analytics_router)
api_router.include_router(dataset_ingest_router)
api_router.include_router(export_summary_router)
api_router.include_router(reviews_feed_router)
api_router.include_router(catalog_router)
api_router.include_router(model_metrics_router)



