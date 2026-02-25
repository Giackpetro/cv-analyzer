from flask import Flask, render_template, request, redirect, url_for
from models import db, Profile, Skill
from ai_analyzer import analyze

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    p = Profile.query.first()
    if p is None:
        p = Profile(name="", email="", summary="")
        db.session.add(p)
        db.session.commit()

    if request.method == "POST":
        p.name = request.form.get("name", "").strip()
        p.email = request.form.get("email", "").strip()
        p.summary = request.form.get("summary", "").strip()
        db.session.commit()
        return redirect(url_for("profile", saved=1))

    saved = request.args.get("saved") == "1"
    return render_template("profile.html", profile=p, saved=saved)

@app.route("/skills", methods=["GET", "POST"])
def skills():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            db.session.add(Skill(name=name))
            db.session.commit()
        return redirect(url_for("skills"))

    all_skills = Skill.query.order_by(Skill.name.asc()).all()
    return render_template("skills.html", skills=all_skills)

@app.route("/skills/delete/<int:skill_id>", methods=["POST"])
def delete_skill(skill_id):
    s = Skill.query.get_or_404(skill_id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("skills"))

@app.route("/analyze", methods=["GET", "POST"])
def analyze_page():
    p = Profile.query.first()
    skills = Skill.query.all()
    skill_names = [s.name for s in skills]

    if request.method == "POST":
        job_text = request.form.get("job", "").strip()

        cv_text = (p.summary or "") + " " + " ".join(skill_names)

        final_score, matching, missing, tfidf_score, skill_score, required_skills = analyze(
            cv_text, job_text, skill_names
        )

        return render_template(
            "result.html",
            score=final_score,
            matching=matching,
            missing=missing,
            tfidf_score=tfidf_score,
            skill_score=skill_score,
            required_skills=required_skills
        )

    # GET: mostro solo il form
    return render_template("analyze.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Profile.query.first() is None:
            db.session.add(Profile(name="", email="", summary=""))
            db.session.commit()

    app.run(debug=True)