"""
Model Evaluation Metrics REST API Endpoint.
Serves authentic evaluation results of the fine-tuned IndoBERT models on test.csv (837 samples)
directly to the Thesis Metrics UI dashboard, eliminating all hardcoded frontend numbers.
"""

import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/model", tags=["Model Evaluation & Metrics"])

EVALUATION_JSON_PATH = os.path.join("models", "indobert_evaluation_results.json")


def load_model_evaluation_metrics() -> Dict[str, Any]:
    """Reads authentic model evaluation metrics JSON produced by indobert_evaluator."""
    if not os.path.exists(EVALUATION_JSON_PATH):
        raise FileNotFoundError(f"Model evaluation results not found at {EVALUATION_JSON_PATH}")

    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/metrics")
def get_model_evaluation_metrics() -> Dict[str, Any]:
    """
    Returns authentic empirical evaluation metrics for IndoBERT Trust & Aspect classifiers
    evaluated on the 837 test dataset partition (test.csv).
    """
    try:
        metrics = load_model_evaluation_metrics()
        return metrics
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load evaluation metrics: {str(e)}")
