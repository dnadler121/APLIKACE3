
from flask import Flask, render_template, request, redirect, url_for
import json
from flask import Blueprint

ucitel_bp = Blueprint(
    "ucitel",
    __name__,
    template_folder="templates",
    static_folder="static"
)

with open("ucitel/stories/golden_spoon.json", encoding="utf-8") as f:
    data = json.load(f)
    STORY = data["chapters"]

def normalize(text):
    replacements = {
        "á":"a","č":"c","ď":"d","é":"e","ě":"e",
        "í":"i","ň":"n","ó":"o","ř":"r","š":"s",
        "ť":"t","ú":"u","ů":"u","ý":"y","ž":"z"
    }

    text = text.lower().strip()

    for a,b in replacements.items():
        text = text.replace(a,b)

    return text

@ucitel_bp.route("/")
def index():
    return redirect(url_for("ucitel.step", step_id=1))

@ucitel_bp.route("/step/<int:step_id>", methods=["GET","POST"])
def step(step_id):

    if step_id < 1 or step_id > len(STORY):
        return redirect(url_for("ucitel.finish"))

    current = STORY[step_id - 1]

    if request.method == "POST":

        answer = normalize(request.form.get("answer",""))

        if normalize(current["answer"]) in answer:
            return redirect(url_for("ucitel.success", next_step=step_id + 1))

        return render_template(
            "ucitel_step.html",
            current=current,
            step_id=step_id,
            total=len(STORY),
            error=True
        )

    return render_template(
        "ucitel_step.html",
        current=current,
        step_id=step_id,
        total=len(STORY),
        error=False
    )

@ucitel_bp.route("/success/<int:next_step>")
def success(next_step):
    return render_template("ucitel_success.html", next_step=next_step)

@ucitel_bp.route("/finish")
def finish():
    return render_template("ucitel_finish.html")


