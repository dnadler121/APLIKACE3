from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from .rooms import ROOMS
from flask import Blueprint

gastro_bp = Blueprint(
    "gastro",
    __name__,
    template_folder="templates",
    static_folder="static"
)


MAX_LIVES = 3
TIME_LIMIT_MINUTES = 50

def clean(text):
    text = text.strip().lower()
    for a, b in {
        "á":"a","č":"c","ď":"d","é":"e","ě":"e","í":"i","ň":"n",
        "ó":"o","ř":"r","š":"s","ť":"t","ú":"u","ů":"u","ý":"y","ž":"z"
    }.items():
        text = text.replace(a, b)
    text = text.replace(" ", "").replace(".", "").replace(":", "")
    return text

@gastro_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team = request.form.get("team", "").strip()
        if not team:
            return render_template("gastro_index.html", error="Zadej název týmu.")
        session.clear()
        session["team"] = team
        session["room"] = 0
        session["lives"] = MAX_LIVES
        session["start"] = datetime.now().isoformat()
        session["flash"] = "SMART RESTAURANT SYSTEM ONLINE"
        session["flash_type"] = "info"
        return redirect(url_for("gastro.game"))
    return render_template("gastro_index.html")

@gastro_bp.route("/game", methods=["GET", "POST"])
def game():
    if "team" not in session:
        return redirect(url_for("gastro.index"))

    start = datetime.fromisoformat(session["start"])
    remain = int(((start + timedelta(minutes=TIME_LIMIT_MINUTES)) - datetime.now()).total_seconds())

    if remain <= 0:
        return redirect(url_for("gastro.gameover", reason="Čas vypršel. Kontrola dorazila."))

    room_i = session.get("room", 0)
    if room_i >= len(ROOMS):
        return redirect(url_for("gastro.victory"))

    room = ROOMS[room_i]

    if request.method == "POST":
        answer = clean(request.form.get("answer", ""))
        accepted = [clean(a) for a in room["answers"]]

        if answer in accepted:
            session["room"] = room_i + 1
            session["flash"] = "ACCESS GRANTED"
            session["flash_type"] = "success"
            return redirect(url_for("gastro.game"))

        session["lives"] -= 1
        if session["lives"] <= 0:
            return redirect(url_for("gastro.gameover", reason="Systém vás uzamkl. Došly životy."))
        session["flash"] = "ACCESS DENIED — ztrácíte jeden život"
        session["flash_type"] = "danger"
        return redirect(url_for("gastro.game"))

    flash = session.pop("flash", "")
    flash_type = session.pop("flash_type", "")

    return render_template(
        "gastro_game.html",
        room=room,
        room_number=room_i + 1,
        total_rooms=len(ROOMS),
        remaining=remain,
        lives=session["lives"],
        team=session["team"],
        flash=flash,
        flash_type=flash_type,
    )

@gastro_bp.route("/victory")
def victory():
    if "team" not in session:
        return redirect(url_for("gastro.index"))
    start = datetime.fromisoformat(session["start"])
    used = datetime.now() - start
    return render_template(
        "gastro_victory.html",
        team=session["team"],
        minutes=int(used.total_seconds() // 60),
        seconds=int(used.total_seconds() % 60),
        lives=session["lives"]
    )

@gastro_bp.route("/gameover")
def gameover():
    reason = request.args.get("reason", "Restaurace zůstala uzamčená.")
    room = session.get("room", 0) + 1
    return render_template("gastro_gameover.html", reason=reason, room=room)

@gastro_bp.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("gastro.index"))

