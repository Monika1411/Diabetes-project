from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Load model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            age = float(request.form["Age"])
            height = float(request.form["Height"])
            weight = float(request.form["Weight"])
            glucose = float(request.form["Glucose"])
            family = int(request.form["FamilyHistory"])

            # Optional inputs
            bp = request.form.get("BloodPressure")
            preg = request.form.get("Pregnancies")

            bp = float(bp) if bp else 72.0
            preg = float(preg) if preg else 0

            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)

            # Feature array
            features = np.array([[age, bmi, glucose, bp, family, preg]])
            features_scaled = scaler.transform(features)

            # Prediction
            prediction = model.predict(features_scaled)[0]
            proba = model.predict_proba(features_scaled)[0][1]

            if prediction == 1:
                result = "⚠️ Possible Diabetes Risk"
                diet = [
                    "Avoid sugary drinks & junk foods 🍩🥤",
                    "Eat high-fiber foods 🌾",
                    "Limit white rice & white bread 🍚🍞",
                    "Include green leafy veggies 🥬",
                    "Prefer grilled fish/chicken instead of fried 🍗🐟"
                ]
            else:
                result = "✅ Low Diabetes Risk"
                diet = [
                    "Maintain balanced diet 🥗",
                    "Stay hydrated 💧",
                    "Exercise at least 30 mins/day 🏃‍♀️",
                    "Include fresh fruits & veggies 🍎🥦",
                    "Avoid too much fast food 🍔🍕"
                ]

            return render_template("result.html",
                                   result=result,
                                   proba=round(proba*100, 1),
                                   diet=diet,
                                   age=age, bmi=round(bmi,1), glucose=glucose, bp=bp)

        except Exception as e:
            return render_template("index.html", result=f"Error: {str(e)}")

    return render_template("index.html")


@app.route("/download_pdf/<result>/<proba>")
def download_pdf(result, proba):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)

    p.drawString(100, 750, "HealMate - Diabetes Risk Report")
    p.drawString(100, 720, f"Prediction: {result}")
    p.drawString(100, 700, f"Risk Probability: {proba}%")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diabetes_report.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
