import pandas as pd
from metrics.demographic_parity import calc_demographic_parity
from metrics.equalized_odds import calc_equalized_odds
from utils.validators import validate_fairness_input

class FairnessEvaluator:
    """
    Unified service for calculating fairness metrics and assessing risk.
    """
    
    def evaluate(self, df: pd.DataFrame) -> dict:
        """
        Evaluates fairness metrics for the given dataset.
        
        Args:
            df: Pandas DataFrame containing 'gender' and 'approved' columns.
            
        Returns:
            A dictionary containing metrics and risk assessments.
        """
        # 1. Secure Input Validation
        validate_fairness_input(df)
        
        # 2. Calculate Metrics using existing logic
        dp_diff = float(calc_demographic_parity(df))
        eo_diff = float(calc_equalized_odds(df))
        
        # 3. Calculate Risk Levels
        dp_risk = self._calculate_risk(dp_diff)
        eo_risk = self._calculate_risk(eo_diff)
        
        # 4. Construct Output
        return {
            "metrics": {
                "demographic_parity_difference": dp_diff,
                "equalized_odds_difference": eo_diff
            },
            "risk_analysis": {
                "demographic_parity_risk": dp_risk,
                "equalized_odds_risk": eo_risk,
                "overall_risk": self._determine_overall_risk([dp_risk, eo_risk])
            }
        }
    
    def _calculate_risk(self, value: float) -> str:
        """
        Maps a metric difference value to a risk level.
        Abs(value):
          0.0 - 0.2 -> LOW
          0.2 - 0.5 -> MEDIUM
          0.5 +     -> HIGH
        """
        abs_val = abs(value)
        if abs_val < 0.2:
            return "LOW"
        elif abs_val < 0.5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _determine_overall_risk(self, risks: list[str]) -> str:
        """
        Determines overall risk based on the highest individual risk.
        """
        if "HIGH" in risks:
            return "HIGH"
        elif "MEDIUM" in risks:
            return "MEDIUM"
        return "LOW"
