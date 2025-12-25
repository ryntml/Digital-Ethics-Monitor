from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class ModelTrainer:
    """
    Trains a baseline model (Logistic Regression) on non-sensitive features
    to demonstrate explainability (LIME).
    """

    def train(self, df: pd.DataFrame, target_col: str, drop_cols: list) -> tuple:
        """
        Trains a logistic regression model.

        Args:
            df: The full dataset.
            target_col: Name of the target column (e.g. 'approved').
            drop_cols: List of columns to exclude from features (e.g. ['gender', 'approved']).

        Returns:
            (trained_model, feature_names, X_train_original)
        """
        # Prepare features (X) and target (y)
        X = df.drop(columns=drop_cols, errors='ignore')
        y = df[target_col]

        feature_names = X.columns.tolist()

        # Simple split (using all for training in this demo context to maximize stability)
        # But good practice:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features (LogReg needs this for better convergence usually, but LIME needs interpretable input)
        # Note: LIME Tabular works best on raw data if we want 'income > 50000'. 
        # Scikit-learn LogReg might need scaling. 
        # Compromise: We won't scale explicitly for this simple demo so LIME output is raw "income" values.
        # LogReg is robust enough for this toy data.

        model = LogisticRegression(random_state=42, solver='liblinear')
        model.fit(X_train, y_train)

        return model, feature_names, X_train
