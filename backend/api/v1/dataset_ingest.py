"""
Female Daily Dataset Ingestion & Pipeline Execution REST API Endpoint.
Triggers cleaning, entity annotation, and stratified dataset splitting pipelines via HTTP POST request.
"""

import os
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.services.ingest_female_daily import ingest_female_daily_pipeline
from backend.services.brand_annotator import annotate_female_daily_dataset
from backend.services.female_daily_splitter import split_female_daily_dataset

router = APIRouter(tags=["Dataset"])

RAW_CSV_PATH = os.path.join("data", "raw", "female_daily_skincare_reviews_raw.csv")
CLEANED_CSV_PATH = os.path.join("data", "cleaned", "female_daily_skincare_cleaned.csv")
ANNOTATED_CSV_PATH = os.path.join("data", "annotated", "female_daily_skincare_annotated.csv")


@router.post("/dataset/ingest", response_model=Dict[str, Any])
async def trigger_dataset_ingest_pipeline(
    cleaned_path: str = None,
    annotated_path: str = None,
    split_dir: str = None
) -> Dict[str, Any]:
    """
    POST /api/v1/dataset/ingest
    Executes full ingestion, text cleaning, entity annotation, and stratified dataset splitting pipelines.
    """
    if not os.path.exists(RAW_CSV_PATH):
        raise HTTPException(status_code=404, detail="Raw dataset file not found at " + RAW_CSV_PATH)
    target_raw = RAW_CSV_PATH
    target_cleaned = cleaned_path or CLEANED_CSV_PATH
    target_annotated = annotated_path or ANNOTATED_CSV_PATH
    target_split_dir = split_dir or os.path.dirname(target_annotated)

    try:
        # 1. Ingestion & Text Cleaning
        cleaned_res, record_count = ingest_female_daily_pipeline(raw_csv_path=target_raw, output_csv_path=target_cleaned)
        
        # 2. Entity & Aspect Annotation
        annotated_res, _ = annotate_female_daily_dataset(cleaned_csv_path=cleaned_res, output_csv_path=target_annotated)
        
        # 3. Stratified Dataset Splitting (Train/Val/Test)
        split_summary = split_female_daily_dataset(annotated_csv_path=annotated_res, output_dir=target_split_dir)
        
        return {
            "status": "success",
            "message": "Dataset ingestion, annotation, and stratified splitting pipeline executed successfully.",
            "processed_records": record_count,
            "cleaned_csv_path": cleaned_res,
            "annotated_csv_path": annotated_res,
            "split_summary": split_summary,
            "timestamp": int(time.time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
