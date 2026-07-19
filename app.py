from utils.pdf_reader import extract_pdf_text
from utils.ai_analyzer import analyze_report
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import json
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from flask_bcrypt import Bcrypt
from flask import flash
from models import db, User, Report
app = Flask(__name__)

app.secret_key = "mediguardian_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mediguardian.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= HOME =================
@app.route("/")
def home():

    if current_user.is_authenticated:
        return render_template("index.html")

    return redirect(url_for("login"))

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists."

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            fullname=fullname,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for("home"))

        flash("Invalid Email or Password")

    return render_template("login.html")
# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))
# ================= UPLOAD PAGE =================
@app.route("/upload")
def upload():
    return render_template("upload.html")

# ================= ANALYZE =================
@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["report"]
    
    
    if file.filename == "":
        return redirect(url_for("upload"))


    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

    file.save(filepath)
    if file.filename.lower().endswith(".pdf"):

        extracted_text = extract_pdf_text(filepath)

        print("----------------")
        print(extracted_text)
        print("----------------")
        print(len(extracted_text))
        print("========== PDF TEXT ==========")
        print(extracted_text[:1000])

        # Clean OCR text
        clean_text = " ".join(extracted_text.split())

        # Limit very large reports
        if len(clean_text) > 12000:
            clean_text = clean_text[:12000]

        try:
            
            analysis = analyze_report(clean_text)

            session["analysis"] = analysis
            print(session["analysis"]["detailed_exercises"][0]["name"])
            print(session["analysis"]["protein_recipes"][0]["name"])

            # Save report if user is logged in
            if current_user.is_authenticated:

                report = Report(
                    user_id=current_user.id,
                    report_name=file.filename,
                    report_type=analysis["report_type"],
                    health_score=analysis["health_score"],
                    priority=analysis["priority"],
                    summary=analysis["summary"],
                    analysis_json=json.dumps(analysis)
                )

                db.session.add(report)
                db.session.commit()

            return render_template(
                "dashboard.html",
                analysis=analysis
            )
        except Exception as e:

            print("========== AI ERROR ==========")
            print(e)

            return f"""
            <h2>AI Error</h2>

            <pre>{str(e)}</pre>
            """
    return f"""
    <h1>✅ Report Uploaded Successfully!</h1>

    <h3>File Name:</h3>

    <p>{file.filename}</p>

    <h3>Saved To:</h3>

    <p>{filepath}</p>

    <br>

    <a href='/upload'>Upload Another Report</a>
    """


@app.route("/dashboard")
def dashboard():

    analysis = session.get("analysis")

    if not analysis:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        analysis=analysis
    )

# ================= HISTORY =================
@app.route("/history")
@login_required
def history():

    reports = Report.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Report.uploaded_at.desc()
    ).all()

    return render_template(
        "history.html",
        reports=reports
    )

@app.route("/report/<int:report_id>")
@login_required
def view_report(report_id):

    report = Report.query.filter_by(
        id=report_id,
        user_id=current_user.id
    ).first_or_404()

    analysis = json.loads(report.analysis_json)

    session["analysis"] = analysis

    return render_template(
        "dashboard.html",
        analysis=analysis
    )       
@app.route("/card/<card_id>")
def card_detail(card_id):

    analysis = session.get("analysis")

    if not analysis:
        return "No report found. Please upload a report first."

    for card in analysis["cards"]:
        if card["id"] == card_id:
            return render_template(
                "detail.html",
                card=card,
                analysis=analysis
            )

    return "Card not found."

# ================= DIET =================
@app.route("/diet")
def diet():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("diet.html", analysis=analysis)


# ================= EXERCISE =================
@app.route("/exercise")
def exercise():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("exercises.html", analysis=analysis)
@app.route("/recipe-page")
@login_required
def recipe_page():
    return render_template(
        "recipes.html",
        analysis=session["analysis"]
    )


# ================= LIFESTYLE =================
@app.route("/lifestyle")
def lifestyle():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("lifestyle.html", analysis=analysis)


# ================= WATER =================
@app.route("/water")
def water():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("water.html", analysis=analysis)


# ================= SLEEP =================
@app.route("/sleep")
def sleep():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("sleep.html", analysis=analysis)


# ================= IMAGES =================
@app.route("/images")
def images():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("images.html", analysis=analysis)


# ================= VIDEOS =================
@app.route("/videos")
def videos():
    analysis = session.get("analysis")
    if not analysis:
        return redirect(url_for("upload"))
    return render_template("videos.html", analysis=analysis)
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/exercise-page")
@login_required
def exercise_page():
    return render_template(
        "exercises.html",
        analysis=session["analysis"]
    )

# ================= MAIN =================
@app.route("/download")
def download_report():

    analysis = session.get("analysis")

    if not analysis:
        return "No report available."

    from utils.pdf_generator import create_pdf

    pdf_path = create_pdf(analysis)

    return send_file(
        pdf_path,
        as_attachment=True
    )
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)