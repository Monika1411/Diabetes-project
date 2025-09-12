import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib

# -----------------------------
# 1. Create dummy dataset
# -----------------------------
np.random.seed(42)
n = 500

data = pd.DataFrame({
    "Age": np.random.randint(20, 70, n),
    "BMI": np.random.uniform(18, 40, n),
    "Glucose": np.random.randint(70, 200, n),
    "BloodPressure": np.random.randint(60, 150, n),
    "FamilyHistory": np.random.choice([0, 1], n),
    "Pregnancies": np.random.randint(0, 6, n),
})

# Simulate outcome (just rough, not medical truth)
data["Outcome"] = (
    (data["Glucose"] > 140).astype(int)
    | (data["BMI"] > 30).astype(int)
    | (data["BloodPressure"] > 130).astype(int)
    | data["FamilyHistory"]
)

# -----------------------------
# 2. Split
# -----------------------------
X = data.drop("Outcome", axis=1)
y = data["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# 3. Scale
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# 4. Train model
# -----------------------------
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# -----------------------------
# 5. Save model + scaler
# -----------------------------
joblib.dump(model, "diabetes_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model trained & saved as diabetes_model.pkl and scaler.pkl")
