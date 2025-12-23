import pandas as pd
import numpy as np

np.random.seed(42)
size = 200

# Generate features
gender = np.random.choice(["male", "female"], size)
income = np.random.normal(50000, 10000, size).astype(int)
credit_score = np.random.normal(650, 100, size).astype(int)

# Create DataFrame
df = pd.DataFrame({
    "gender": gender,
    "income": income,
    "credit_score": credit_score
})

# Fair approval logic: based purely on credit score
# Threshold around 650 gives decent balance
df["approved"] = (df["credit_score"] > 650).astype(int)

df.to_csv("datasets/dummy.csv", index=False)
print("Balanced dataset generated with features: gender, income, credit_score, approved")
