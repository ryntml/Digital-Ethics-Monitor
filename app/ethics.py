def evaluate_ethics(decision_label: str, score: float, sensitive_attribute: str | None):
    if sensitive_attribute and score < 0.5:
        return "BIASED", "Sensitive attribute detected with low confidence score"

    if score < 0.6:
        return "RISKY", "Low confidence decision"

    return "FAIR", "Decision passed basic ethical checks"
