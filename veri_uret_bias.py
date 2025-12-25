import pandas as pd
import numpy as np

np.random.seed(42)
size = 300

# Generate features
gender = np.random.choice(["male", "female"], size)
income = np.random.normal(50000, 15000, size).astype(int) 
credit_score = np.random.normal(650, 100, size).astype(int)

df = pd.DataFrame({
    "gender": gender,
    "income": income,
    "credit_score": credit_score
})

# Biased approval logic: Gender-based
# Men: 80% approval, Women: 20% approval
# This preserves the original bias for metric demonstration
def biased_approval(row):
    if row["gender"] == "male":
        return np.random.choice([1, 0], p=[0.8, 0.2])
    else:
        return np.random.choice([1, 0], p=[0.2, 0.8])

df["approved"] = df.apply(biased_approval, axis=1)

df.to_csv("datasets/biased.csv", index=False)
print("Biased dataset generated with features: gender, income, credit_score, approved")
