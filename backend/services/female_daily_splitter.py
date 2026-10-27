"""
Stratified Dataset Splitter & Sampling Engine Service.
Splits annotated Female Daily reviews into train (80%), val (10%), and test (10%)
with balanced stratification on trust sentiment labels and communication aspects.
Ensures deterministic reproducibility via fixed random seed and SHA256 checksum validation.
"""

import os
import hashlib
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split

ANNOTATED_DATA_DIR = os.path.join("data", "annotated")
os.makedirs(ANNOTATED_DATA_DIR, exist_ok=True)


def compute_file_sha256(file_path: str) -> str:
    """Computes SHA256 checksum for a given file path."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def split_female_daily_dataset(
    annotated_csv_path: str = "data/annotated/female_daily_skincare_annotated.csv",
    output_dir: str = "data/annotated",
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Splits annotated dataset into train, validation, and test CSV sets using stratified sampling.
    """
    if not os.path.exists(annotated_csv_path):
        raise FileNotFoundError(f"Annotated dataset file not found at: {annotated_csv_path}")
        
    df = pd.read_csv(annotated_csv_path)
    total_count = len(df)
    
    if total_count == 0:
        raise ValueError("Annotated dataset is empty.")
        
    print(f"\n[Dataset Splitter] Splitting {total_count} annotated records into Train ({train_ratio*100:.0f}%), Val ({val_ratio*100:.0f}%), Test ({test_ratio*100:.0f}%)...")
    
    # Stratification composite key (Trust Sentiment + Aspect Category)
    df["stratify_key"] = df["label_kepercayaan"].astype(str) + "_" + df["aspek_komunikasi"].astype(str)
    
    # 1. First split: Train (80%) vs Temp (20%)
    temp_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_ratio,
        random_state=random_seed,
        stratify=df["stratify_key"]
    )
    
    # 2. Second split: Val (50% of Temp = 10%) vs Test (50% of Temp = 10%)
    val_relative_ratio = val_ratio / temp_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_relative_ratio),
        random_state=random_seed,
        stratify=temp_df["stratify_key"]
    )
    
    # Drop temporary stratification key
    train_df = train_df.drop(columns=["stratify_key"]).reset_index(drop=True)
    val_df = val_df.drop(columns=["stratify_key"]).reset_index(drop=True)
    test_df = test_df.drop(columns=["stratify_key"]).reset_index(drop=True)
    
    # Export paths
    train_path = os.path.join(output_dir, "train.csv")
    val_path = os.path.join(output_dir, "val.csv")
    test_path = os.path.join(output_dir, "test.csv")
    
    os.makedirs(output_dir, exist_ok=True)
    train_df.to_csv(train_path, index=False, encoding="utf-8-sig")
    val_df.to_csv(val_path, index=False, encoding="utf-8-sig")
    test_df.to_csv(test_path, index=False, encoding="utf-8-sig")
    
    summary = {
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "total_rows": total_count,
        "train_path": os.path.abspath(train_path),
        "val_path": os.path.abspath(val_path),
        "test_path": os.path.abspath(test_path),
        "train_sha256": compute_file_sha256(train_path),
        "val_sha256": compute_file_sha256(val_path),
        "test_sha256": compute_file_sha256(test_path),
    }
    
    print(f"  -> Train set saved : {len(train_df)} rows ({len(train_df)/total_count*100:.1f}%) -> {train_path}")
    print(f"  -> Val set saved   : {len(val_df)} rows ({len(val_df)/total_count*100:.1f}%) -> {val_path}")
    print(f"  -> Test set saved  : {len(test_df)} rows ({len(test_df)/total_count*100:.1f}%) -> {test_path}")
    
    return summary


if __name__ == "__main__":
    split_female_daily_dataset()
