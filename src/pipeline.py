from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from src.config import PROCESSED_PARQUET_DIR, TARGET_COLUMN_CANDIDATES, ensure_directories


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")


def infer_target_column(df: pd.DataFrame) -> str:
    for col in TARGET_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError("Target column not found. Update TARGET_COLUMN_CANDIDATES in src/config.py.")


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = (
        cleaned.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )
    return cleaned


def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_column_names(df)

    for col in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Replace obvious null-like strings with proper NaN.
    cleaned = cleaned.replace({"": np.nan, "NA": np.nan, "N/A": np.nan, "None": np.nan})

    return cleaned


def feature_engineering(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    engineered = df.copy()

    # Remove identifier-like columns from the modeling feature set.
    id_like_columns = [
        col
        for col in engineered.columns
        if col != target_col and col.lower().replace("_", "") in {"customerid", "customer_id", "id"}
    ]
    if id_like_columns:
        engineered = engineered.drop(columns=id_like_columns)

    num_cols = engineered.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = engineered.select_dtypes(exclude=["number"]).columns.tolist()

    if target_col in cat_cols:
        cat_cols.remove(target_col)

    if num_cols:
        engineered["numeric_feature_count"] = engineered[num_cols].notna().sum(axis=1)

    if cat_cols:
        engineered["categorical_feature_count"] = engineered[cat_cols].notna().sum(axis=1)

    features = engineered.drop(columns=[target_col])
    target = engineered[[target_col]]

    return features, target


def export_parquet_assets(df_clean: pd.DataFrame, features: pd.DataFrame, target: pd.DataFrame) -> None:
    ensure_directories()

    (PROCESSED_PARQUET_DIR / "dim_customers.parquet").parent.mkdir(parents=True, exist_ok=True)

    df_clean.to_parquet(PROCESSED_PARQUET_DIR / "fact_churn_base.parquet", index=False)
    features.to_parquet(PROCESSED_PARQUET_DIR / "model_features.parquet", index=False)
    target.to_parquet(PROCESSED_PARQUET_DIR / "model_target.parquet", index=False)


def build_powerbi_ready_tables(df: pd.DataFrame, target_col: str) -> dict[str, pd.DataFrame]:
    out = {}

    customers = df.copy()
    if "customerID" in customers.columns:
        customers = customers.rename(columns={"customerID": "customer_id"})

    out["fact_churn"] = customers

    if "Contract" in df.columns:
        dim_contract = (
            df[["Contract"]]
            .drop_duplicates()
            .reset_index(drop=True)
            .rename(columns={"Contract": "contract_type"})
        )
        dim_contract["contract_key"] = dim_contract.index + 1
        out["dim_contract"] = dim_contract

    if "PaymentMethod" in df.columns:
        dim_payment = (
            df[["PaymentMethod"]]
            .drop_duplicates()
            .reset_index(drop=True)
            .rename(columns={"PaymentMethod": "payment_method"})
        )
        dim_payment["payment_key"] = dim_payment.index + 1
        out["dim_payment"] = dim_payment

    if target_col in df.columns:
        churn_map = (
            df[[target_col]]
            .drop_duplicates()
            .reset_index(drop=True)
            .rename(columns={target_col: "churn_label"})
        )
        churn_map["churn_key"] = churn_map.index + 1
        out["dim_churn"] = churn_map

    return out


def export_powerbi_model_tables(tables: dict[str, pd.DataFrame]) -> None:
    ensure_directories()
    for table_name, table_df in tables.items():
        table_df.to_parquet(PROCESSED_PARQUET_DIR / f"{table_name}.parquet", index=False)
