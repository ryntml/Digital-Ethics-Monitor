import pandas as pd
from typing import List

def validate_fairness_input(df: pd.DataFrame, required_columns: List[str] = None) -> bool:
    """
    Validates that the input DataFrame contains the necessary columns and data types
    for fairness evaluation.
    
    Args:
        df: The pandas DataFrame to validate.
        required_columns: List of column names that must be present. 
                          Defaults to ["gender", "approved"].
    
    Returns:
        True if validation passes.
    
    Raises:
        ValueError: If validation fails.
    """
    if required_columns is None:
        required_columns = ["gender", "approved"]
        
    # Check if df is a DataFrame
    if not isinstance(df, pd.DataFrame):
         raise ValueError("Input data must be a pandas DataFrame.")

    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Input dataset is missing required columns: {filter_sensitive_names(missing_cols)}")

    # Check 'approved' column (target) - should be numeric (0/1) or boolean
    if "approved" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["approved"]) and not pd.api.types.is_bool_dtype(df["approved"]):
             raise ValueError("Column 'approved' must be numeric or boolean.")

    # Check 'gender' column (sensitive) - mostly just existence, but we could check for empty
    if "gender" in df.columns:
        if df["gender"].isnull().any():
             raise ValueError("Column 'gender' contains null values, which are not allowed for fairness evaluation.")

    return True

def filter_sensitive_names(cols: List[str]) -> List[str]:
    """
    Helper to avoid logging highly sensitive column names if we had any arbitrary ones.
    For this project, 'gender' and 'approved' are standard schema, but good practice.
    """
    # In a real scenario, we might redact unknown column names. 
    # Here we just pass them through as they are schema keys.
    return cols
