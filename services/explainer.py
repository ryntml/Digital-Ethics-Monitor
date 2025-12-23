class FairnessExplainer:
    """
    Service for generating human-readable explanations of fairness metrics.
    """
    
    def generate_explanation(self, evaluation_result: dict, dataset_name: str = "dataset") -> str:
        """
        Generates a summary string based on metrics and risk.
        
        Args:
            evaluation_result: The dictionary returned by FairnessEvaluator.evaluate()
            dataset_name: Optional label for the dataset (e.g., 'Balanced', 'Biased')
            
        Returns:
            A descriptive string processing the findings.
        """
        risks = evaluation_result.get("risk_analysis", {})
        overall = risks.get("overall_risk", "UNKNOWN")
        
        explanation = [f"Fairness Report for {dataset_name}:"]
        
        # Overall assessment
        if overall == "HIGH":
            explanation.append(f"CRITICAL: The system detected HIGH bias risks in this {dataset_name}. Immediate attention is required.")
        elif overall == "MEDIUM":
            explanation.append(f"WARNING: Moderate bias detected in this {dataset_name}. Monitoring is recommended.")
        else:
            explanation.append(f"SUCCESS: The {dataset_name} appears to be fair with LOW risk levels.")
            
        # Detailed breakdown
        dp_risk = risks.get("demographic_parity_risk")
        if dp_risk == "HIGH":
            explanation.append("- Demographic Parity is HIGH risk: Approval rates differ significantly between gender groups.")
        elif dp_risk == "MEDIUM":
            explanation.append("- Demographic Parity is MEDIUM risk: There is a noticeable difference in approval rates between groups.")
            
        eo_risk = risks.get("equalized_odds_risk")
        if eo_risk == "HIGH":
            explanation.append("- Equalized Odds is HIGH risk: Error rates (false positives/negatives) are unequal across groups.")
        elif eo_risk == "MEDIUM":
            explanation.append("- Equalized Odds is MEDIUM risk: Some disparity in error rates was observed.")
            
        return " ".join(explanation)

    def scrub_sensitive_data(self, text: str) -> str:
        """
        Helper to ensure no specific sensitive attribute values (if we were logging them) 
        leak into the explanation accidentally. 
        For now, our templates are safe, but this is a placeholder for future sanitization.
        """
        return text
