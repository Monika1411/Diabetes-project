from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import joblib
import numpy as np
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------- APP CONFIG -------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ------------------- USER MODEL -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)   # <-- NEW FIELD
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ------------------- AUTH ROUTES -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")  # <-- NEW
        email = request.form.get("identifier")  # updated to match form
        password = request.form.get("password")
        confirm = request.form.get("confirm")  # get confirm password

        # check if passwords match
        if password != confirm:
            flash("Passwords do not match ❌", "danger")
            return redirect(url_for("signup"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists! Please log in instead.", "warning")
            return redirect(url_for("login"))

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")  # <-- FIXED
        new_user = User(name=name, email=email, password=hashed_pw)  # store name too
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("identifier")  # can be email or phone
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_email"] = user.email
            session["user_name"] = user.name  # <-- store name in session
            flash("Login successful! 🎉", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email/phone or password ❌", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)  # <-- remove name from session
    flash("Logged out successfully 👋", "info")
    return redirect(url_for("login"))


# ------------------- MODEL LOGIC -------------------
def load_model_and_scaler():
    try:
        model = joblib.load("diabetes_model.pkl")
        scaler = joblib.load("scaler.pkl")
        return model, scaler
    except Exception as e:
        return None, None


def get_diet_recommendation(prediction):
    if prediction == 1:
        result = "⚠️ Possible Diabetes Risk"
        diet = [
            "Avoid sugary drinks & junk foods.",
            "Eat high-fiber foods.",
            "Limit white rice & white bread.",
            "Include green leafy veggies.",
            "Prefer grilled fish/chicken instead of fried."
        ]
    else:
        result = "✅ Low Diabetes Risk"
        diet = [
            "Maintain balanced diet.",
            "Stay hydrated.",
            "Exercise at least 30 mins/day.",
            "Include fresh fruits & veggies.",
            "Avoid too much fast food."
        ]
    return result, diet


# ------------------- MAIN ROUTES -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if 'user_email' not in session:
        flash("Please log in to access the predictor 🔐", "warning")
        return redirect(url_for("login"))

    # ------------------- NEW: Get user's name from session -------------------
    user_name = session.get("user_name")  # <-- get name to pass to template
    user_email = session.get("user_email")
    # ------------------------------------------------------------------------

    if request.method == "POST":
        try:
            age = float(request.form["Age"])
            height = float(request.form["Height"])
            weight = float(request.form["Weight"])
            glucose = float(request.form["Glucose"])
            family = int(request.form["FamilyHistory"])

            bp = request.form.get("BloodPressure")
            preg = request.form.get("Pregnancies")
            bp = float(bp) if bp else 72.0
            preg = float(preg) if preg else 0

            bmi = weight / ((height / 100) ** 2)

            features = np.array([[age, bmi, glucose, bp, family, preg]])
            model, scaler = load_model_and_scaler()
            if not model or not scaler:
                flash("Model or Scaler file missing. Contact admin.", "danger")
                return render_template("index.html", user_name=user_name, user_email=user_email)

            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            proba = model.predict_proba(features_scaled)[0][1]

            result, diet = get_diet_recommendation(prediction)

            return render_template(
                "result.html",
                result=result,
                proba=round(proba * 100, 1),
                diet=diet,
                age=age, bmi=round(bmi, 1), glucose=glucose, bp=bp,
                family=family, preg=preg,
                user_name=user_name,  # <-- Pass name to result.html too
                user_email=user_email
            )
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("index.html", user_name=user_name, user_email=user_email)
    return render_template("index.html", user_name=user_name, user_email=user_email)


@app.route("/download_pdf/<result>/<proba>")
def download_pdf(result, proba):
    if 'user_email' not in session:
        flash("Please log in to download the report 📄", "warning")
        return redirect(url_for("login"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

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

    elements = [
        Paragraph("HealMate - Diabetes Risk Report", title_style),
        Paragraph(f"Date: {datetime.date.today().strftime('%d-%m-%Y')}", normal_style),
        Spacer(1, 12),
        Paragraph("Patient Summary", header_style),
        Paragraph(f"<b>Prediction:</b> {result}", normal_style),
        Paragraph(f"<b>Risk Probability:</b> {proba}%", normal_style),
        Spacer(1, 12),
        Paragraph("Recommended Diet Plan", header_style)
    ]

    if result.startswith("⚠️"):
        diet_data = [
            ["Meal", "Recommendation"],
            ["Breakfast", "Oats with skim milk, fruits"],
            ["Lunch", "Brown rice, grilled chicken/fish, vegetables"],
            ["Snack", "Sprouts, green tea"],
            ["Dinner", "Chapati, dal, salad"]
        ]
    else:
        diet_data = [
            ["Meal", "Recommendation"],
            ["Breakfast", "Fruit salad, multigrain toast"],
            ["Lunch", "Steamed rice, dal, vegetables"],
            ["Snack", "Nuts, herbal tea"],
            ["Dinner", "Soup, salad, chapati"]
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
    elements.append(Paragraph(
        "⚠️ Disclaimer: This is an AI-generated risk report and should not replace professional medical advice. Please consult a healthcare provider.",
        normal_style)
    )

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diabetes_report.pdf", mimetype="application/pdf")


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Creates users.db automatically
    app.run(debug=True)
