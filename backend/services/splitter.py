"""
Dataset Splitter Service for Halal Cosmetics NLP.
Implements Stratified Train (80%), Validation (10%), and Test (10%) dataset splitting
preserving aspect & trust label distributions without data leakage.
"""

import os
import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split

def split_dataset_stratified(
    df: pd.DataFrame, 
    train_ratio: float = 0.8, 
    val_ratio: float = 0.1, 
    test_ratio: float = 0.1, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits a DataFrame into stratified train, validation, and test sets.
    """
    if not abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5:
        raise ValueError("Ratios must sum up to 1.0")
        
    df = df.copy()
    
    # Create composite stratify key from aspect & trust labels
    if "label_aspek" in df.columns and "label_kepercayaan" in df.columns:
        stratify_key = df["label_aspek"].astype(str) + "_" + df["label_kepercayaan"].astype(str)
    elif "label_kepercayaan" in df.columns:
        stratify_key = df["label_kepercayaan"].astype(str)
    else:
        stratify_key = None
        
    # First split: Train vs Temp (Val + Test)
    temp_ratio = val_ratio + test_ratio
    df_train, df_temp = train_test_split(
        df, 
        test_size=temp_ratio, 
        random_state=random_state, 
        stratify=stratify_key
    )
    
    # Second split: Val vs Test
    val_test_ratio = test_ratio / temp_ratio
    if stratify_key is not None:
        temp_stratify = stratify_key.loc[df_temp.index]
    else:
        temp_stratify = None
        
    df_val, df_test = train_test_split(
        df_temp, 
        test_size=val_test_ratio, 
        random_state=random_state, 
        stratify=temp_stratify
    )
    
    return df_train.reset_index(drop=True), df_val.reset_index(drop=True), df_test.reset_index(drop=True)


def process_and_save_splits(
    annotated_csv_path: str = "data/annotated/female_daily_skincare_annotated.csv",
    output_dir: str = "data/annotated"
) -> Tuple[str, str, str]:
    """
    Reads annotated dataset, performs 80/10/10 stratified split, and saves train.csv, val.csv, test.csv.
    """
    if not os.path.exists(annotated_csv_path):
        raise FileNotFoundError(f"Annotated dataset not found at {annotated_csv_path}")
        
    df_annotated = pd.read_csv(annotated_csv_path)
    df_train, df_val, df_test = split_dataset_stratified(df_annotated)
    
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.abspath(os.path.join(output_dir, "train.csv"))
    val_path = os.path.abspath(os.path.join(output_dir, "val.csv"))
    test_path = os.path.abspath(os.path.join(output_dir, "test.csv"))
    
    df_train.to_csv(train_path, index=False, encoding="utf-8-sig")
    df_val.to_csv(val_path, index=False, encoding="utf-8-sig")
    df_test.to_csv(test_path, index=False, encoding="utf-8-sig")
    
    return train_path, val_path, test_path


if __name__ == "__main__":
    tr, va, te = process_and_save_splits()
    print(f"[Splitter Success]\nTrain: {tr}\nVal: {va}\nTest: {te}")
