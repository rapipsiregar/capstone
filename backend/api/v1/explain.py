import time
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.services.indobert_explainer import explain_text_with_shap


router = APIRouter(prefix="/explain", tags=["Explainable AI (XAI)"])


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=3, json_schema_extra={"example": "Sertifikat halal jelas dari BPOM dan kandungannya aman tanpa alkohol."})
    model_choice: Optional[str] = Field("indobert", json_schema_extra={"example": "indobert"})


class TokenAttributionItem(BaseModel):
    token: str = Field(..., json_schema_extra={"example": "halal"})
    score: float = Field(..., json_schema_extra={"example": 0.342})
    impact: str = Field(..., json_schema_extra={"example": "High_Trust"})
    highlight_color: str = Field(..., json_schema_extra={"example": "#28a745"})


class ExplainResponse(BaseModel):
    raw_text: str
    cleaned_text: str
    predicted_aspect: str
    predicted_trust: str
    trust_confidence: float
    tokens: List[str]
    attributions: List[TokenAttributionItem]
    base_value: float
    explanation_summary: str
    execution_time_ms: float


@router.post("", response_model=ExplainResponse)
def explain_review_shap(request: ExplainRequest):
    """
    Returns Explainable AI (SHAP) word-level attributions and UI color highlights 
    for public trust sentiment analysis computed via authentic SHAP explainer.
    """
    try:
        explanation = explain_text_with_shap(text=request.text)

        return ExplainResponse(
            raw_text=explanation["raw_text"],
            cleaned_text=explanation["cleaned_text"],
            predicted_aspect=explanation["predicted_aspect"],
            predicted_trust=explanation["predicted_trust"],
            trust_confidence=explanation["trust_confidence"],
            tokens=explanation["tokens"],
            attributions=explanation["attributions"],
            base_value=explanation["base_value"],
            explanation_summary=explanation["explanation_summary"],
            execution_time_ms=explanation["execution_time_ms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XAI calculation error: {str(e)}")
