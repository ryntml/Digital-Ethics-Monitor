from fairlearn.metrics import demographic_parity_difference

def calc_demographic_parity(df):
    y_true = df["approved"]
    y_pred = df["approved"]
    sensitive = df["gender"]

    try:
        # Eski imza (senin sürümün)
        dp = demographic_parity_difference(
            y_true,
            y_pred,
            sensitive_features=sensitive
        )
    except TypeError:
        # Yeni imza (yalnızca y_true + sensitive_features)
        dp = demographic_parity_difference(
            y_true,
            sensitive_features=sensitive
        )
    return dp
