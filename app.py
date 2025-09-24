from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import datetime

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


# 📌 Improved PDF route
@app.route("/download_pdf/<result>/<proba>")
def download_pdf(result, proba):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=1,
        spaceAfter=20
    )
    header_style = ParagraphStyle(
        "header",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#2E86C1"),
        spaceBefore=10,
        spaceAfter=10
    )
    normal_style = styles["Normal"]

    # Content
    elements = []
    elements.append(Paragraph("HealMate - Diabetes Risk Report", title_style))
    elements.append(Paragraph(f"Date: {datetime.date.today().strftime('%d-%m-%Y')}", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Patient Summary", header_style))
    elements.append(Paragraph(f"<b>Prediction:</b> {result}", normal_style))
    elements.append(Paragraph(f"<b>Risk Probability:</b> {proba}%", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Recommended Diet Plan 🍽️", header_style))

    diet_data = [
        ["Meal", "Recommendation"],
        ["Breakfast", "Oats with skim milk, fruits"],
        ["Lunch", "Brown rice, grilled chicken/fish, vegetables"],
        ["Snack", "Sprouts, green tea"],
        ["Dinner", "Chapati, dal, salad"]
    ]

    table = Table(diet_data, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("⚠️ Disclaimer: This is an AI-generated risk report and should not replace professional medical advice. Please consult a healthcare provider.", normal_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="diabetes_report.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
