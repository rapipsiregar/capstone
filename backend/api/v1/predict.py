import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.services.indobert_predictor import predict_indobert_authentic
from backend.services.database import save_review_log


router = APIRouter(prefix="/predict", tags=["Inference & Prediction"])


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=3, json_schema_extra={"example": "Sertifikat halal jelas dari BPOM dan aman."})
    model_choice: Optional[str] = Field("indobert", json_schema_extra={"example": "indobert"})


class PredictResponse(BaseModel):
    raw_text: str
    cleaned_text: str
    predicted_aspect: str
    aspect_confidence: float
    predicted_trust: str
    trust_confidence: float
    model_type: str
    execution_time_ms: float


@router.post("", response_model=PredictResponse)
def predict_sentiment_and_aspect(request: PredictRequest):
    """
    Performs NLP dual-target inference predicting Aspect category and Public Trust sentiment
    using the fine-tuned IndoBERT Transformer model.
    """
    try:
        prediction = predict_indobert_authentic(request.text)

        result_payload = {
            "raw_text": prediction["raw_text"],
            "cleaned_text": prediction["cleaned_text"],
            "predicted_aspect": prediction["predicted_aspect"],
            "aspect_confidence": prediction["aspect_confidence"],
            "predicted_trust": prediction["predicted_trust"],
            "trust_confidence": prediction["trust_confidence"],
            "model_type": prediction["model_type"],
            "execution_time_ms": prediction["execution_time_ms"]
        }

        # Log inference to SQLite history database
        try:
            save_review_log(result_payload)
        except Exception:
            pass  # Non-blocking log save

        return PredictResponse(**result_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

