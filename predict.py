import pandas as pd
import joblib
import numpy as np

# Load model and scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load dataset to calculate average values (for missing inputs)
data = pd.read_csv("diabetes.csv")
feature_means = data.drop("Outcome", axis=1).mean()

# Function to predict diabetes risk
def predict_diabetes(user_input):
    """
    user_input = dictionary with keys:
      Age, Height, Weight, Glucose, BloodPressure, Pregnancies, Insulin, SkinThickness, DiabetesPedigreeFunction
    Some keys can be missing (optional fields).
    """

    # Convert Height & Weight to BMI if provided
    if "Height" in user_input and "Weight" in user_input:
        height_m = user_input["Height"] / 100  # cm → meters
        user_input["BMI"] = round(user_input["Weight"] / (height_m ** 2), 1)

    # Prepare full feature list (same as dataset)
    features = [
        "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
    ]

    input_filled = []
    for f in features:
        if f in user_input and user_input[f] is not None:
            input_filled.append(user_input[f])
        else:
            # Use dataset mean if missing
            input_filled.append(feature_means[f])

    # Scale & predict
    input_scaled = scaler.transform([input_filled])
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1] * 100

    # Confidence logic
    provided = sum(1 for f in features if f in user_input and user_input[f] is not None)
    confidence = "High" if provided > 6 else "Medium" if provided > 4 else "Low"

    return prediction, probability, confidence


# Example usage (only required fields entered)
user_data = {
    "Age": 45,
    "Height": 160,   # cm
    "Weight": 80,    # kg
    "Glucose": 160,
    "BloodPressure": 130
    # Pregnancies, Insulin, SkinThickness, DiabetesPedigreeFunction not given
}

pred, prob, conf = predict_diabetes(user_data)
print(f"Prediction: {'Diabetes Risk' if pred==1 else 'No Diabetes'}")
print(f"Probability: {prob:.2f}%")
print(f"Confidence Level: {conf}")

