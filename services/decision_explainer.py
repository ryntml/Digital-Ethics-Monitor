import lime
import lime.lime_tabular
import numpy as np
import pandas as pd

class DecisionExplainer:
    """
    Service for generating local explanations using LIME (Local Interpretable Model-agnostic Explanations).
    """

    def explain_decision(self, model, feature_names, instance_row: pd.Series, training_data: pd.DataFrame) -> dict:
        """
        Generates a LIME explanation for a single prediction.

        Args:
            model: Trained scikit-learn model (must have predict_proba).
            feature_names: List of feature names used by the model.
            instance_row: Single row (Series) from the dataframe to explain.
            training_data: The training dataset (X_train) used to initialize LIME.

        Returns:
            Dictionary containing prediction, confidence, and top features.
        """
        # Initialize LIME Explainer
        # We pass training_data.values to fit the local discretizer
        explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data.values,
            feature_names=feature_names,
            class_names=['REJECTED', 'APPROVED'],
            mode='classification',
            random_state=42
        )

        # Convert instance to numpy array
        # Ensure we only select the relevant features from the instance row
        instance_values = instance_row[feature_names].values.astype(float)

        # Generate explanation
        exp = explainer.explain_instance(
            instance_values,
            model.predict_proba,
            num_features=3
        )

        # Extract details
        pred_probs = model.predict_proba([instance_values])[0]
        predicted_class_idx = np.argmax(pred_probs)
        predicted_label = "APPROVED" if predicted_class_idx == 1 else "REJECTED"
        confidence = float(pred_probs[predicted_class_idx])

        # Extract top features
        # exp.as_list() returns tuples like ('income > 50000', 0.25)
        lime_list = exp.as_list()
        
        # Format top features for JSON output
        top_features = []
        feature_names_only = []
        for feature_cond, weight in lime_list:
            sign = "+" if weight > 0 else "-"
            # Simplify string for readability
            formatted = f"{feature_cond} ({sign}{abs(weight):.2f})"
            top_features.append(formatted)
            
            # Extract basic feature name for summary text (heuristic)
            for fname in feature_names:
                if fname in feature_cond:
                    feature_names_only.append(fname)

        # Remove duplicates
        feature_names_only = list(set(feature_names_only))
        
        # Construct summary text
        features_text = " and ".join(feature_names_only) if feature_names_only else "specific factors"
        explanation_text = f"The decision was mainly influenced by {features_text}."

        return {
            "prediction": predicted_label,
            "confidence": round(confidence, 2),
            "top_features": top_features,
            "explanation_text": explanation_text
        }
