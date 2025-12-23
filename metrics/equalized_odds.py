from fairlearn.metrics import equalized_odds_difference

def calc_equalized_odds(df):
    y_true = df["approved"]
    y_pred = df["approved"]
    sensitive = df["gender"]

    eo = equalized_odds_difference(
        y_true,
        y_pred,
        sensitive_features=sensitive
    )
    return eo
