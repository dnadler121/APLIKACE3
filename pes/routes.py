from flask import Flask, render_template, request, redirect, url_for, session
from .chapters import CHAPTERS
from datetime import datetime
from flask import Blueprint

pes_bp = Blueprint(
    "pes",
    __name__,
    template_folder="templates",
    static_folder="static"
)

def clean(text):
    text = text.strip().lower()

    replacements = {
        "á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i",
        "ň": "n", "ó": "o", "ř": "r", "š": "s", "ť": "t",
        "ú": "u", "ů": "u", "ý": "y", "ž": "z"
    }

    for a, b in replacements.items():
        text = text.replace(a, b)

    text = text.replace(".", "")
    text = text.replace(",", "")
    text = text.replace("dr ", "doktor ")
    text = text.replace("doktor ", "")
    text = text.replace("sir ", "")
    text = text.replace("pan ", "")
    text = text.replace("pani ", "")

    return text.replace(" ", "")

@pes_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team = request.form.get("team", "").strip()
        if not team:
            return render_template("pes_index.html", error="Zadej jméno týmu.")
        session.clear()
        session["team"] = team
        session["chapter"] = 0
        session["start"] = datetime.now().isoformat()
        session["message"] = "Případ začíná."
        session["status"] = "info"
        return redirect(url_for("pes.story"))
    return render_template("pes_index.html")

@pes_bp.route("/story", methods=["GET", "POST"])
def story():
    if "team" not in session:
        return redirect(url_for("pes.index"))

    chapter_index = session.get("chapter", 0)
    if chapter_index >= len(CHAPTERS):
        return redirect(url_for("pes.victory"))

    chapter = CHAPTERS[chapter_index]
    message = session.pop("message", "")
    status = session.pop("status", "")

    if request.method == "POST":
        answer = clean(request.form.get("answer", ""))
        accepted = [clean(a) for a in chapter["answers"]]

        if answer in accepted:
            session["chapter"] = chapter_index + 1
            session["message"] = "Stopa odhalena. Pokračujete dál."
            session["status"] = "success"
            return redirect(url_for("pes.story"))

        

        session["message"] = "Špatná odpověď. Ztrácíte jeden život."
        session["status"] = "danger"
        return redirect(url_for("pes.story"))

    return render_template(
        "pes_story.html",
        chapter=chapter,
        chapter_number=chapter_index + 1,
        total=len(CHAPTERS),
        team=session["team"],
        message=message,
        status=status
    )

@pes_bp.route("/victory")
def victory():
    return render_template("pes_victory.html", team=session.get("team", "tým"))

@pes_bp.route("/gameover")
def gameover():
    return render_template("pes_gameover.html")

@pes_bp.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("pes.index"))


