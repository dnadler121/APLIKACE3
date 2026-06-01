from flask import Blueprint, render_template, request, redirect, url_for, session
import random
from copy import deepcopy

dane_bp = Blueprint(
    "dane",
    __name__,
    template_folder="templates",
    static_folder="static"
)

SOCIAL_RATE = 0.071
HEALTH_RATE = 0.045
TAX_RATE = 0.15
TAX_DISCOUNT = 2570
DPP_LIMIT = 12000
DPC_LIMIT = 4500

SCENARIOS = [
    {
        "kind": "HPP",
        "title": "Klasický zaměstnanec na HPP",
        "role": "kuchař ve školní jídelně",
        "hours": 160,
        "rate": 170,
        "color": "blue",
        "explain": "U klasického pracovního poměru se z hrubé mzdy odvádí sociální i zdravotní pojištění.",
    },
    {
        "kind": "DPP",
        "title": "Zaměstnanec na DPP",
        "role": "brigádník při víkendové akci",
        "hours": 40,
        "rate": 250,
        "color": "green",
        "explain": "U DPP se v této výukové úloze pojistné neplatí, pokud příjem nepřesáhne 12 000 Kč.",
    },
    {
        "kind": "DPČ",
        "title": "Zaměstnanec na DPČ",
        "role": "pomocná síla v restauraci",
        "hours": 45,
        "rate": 130,
        "color": "orange",
        "explain": "U DPČ se v této výukové úloze pojistné platí od hranice 4 500 Kč.",
    }
]


def make_tasks():

    tasks = deepcopy(SCENARIOS)

    variants = {
        "HPP": [
            (160, 170),
            (150, 180),
            (168, 165)
        ],
        "DPP": [
            (40, 250),
            (30, 300),
            (48, 230)
        ],
        "DPČ": [
            (45, 130),
            (50, 120),
            (60, 110)
        ]
    }

    for task in tasks:

        h, r = random.choice(variants[task["kind"]])

        task["hours"] = h
        task["rate"] = r
        task["gross"] = h * r

        task.update(calc_pay(task))

    return tasks


def insurance_applies(task):

    if task["kind"] == "HPP":
        return True

    if task["kind"] == "DPP":
        return task["gross"] >= DPP_LIMIT

    if task["kind"] == "DPČ":
        return task["gross"] >= DPC_LIMIT

    return False


def calc_pay(task):

    gross = task["hours"] * task["rate"]

    applies = insurance_applies(
        {
            **task,
            "gross": gross
        }
    )

    social = round(gross * SOCIAL_RATE) if applies else 0
    health = round(gross * HEALTH_RATE) if applies else 0

    tax_before_discount = round(gross * TAX_RATE)

    tax_after_discount = max(
        0,
        tax_before_discount - TAX_DISCOUNT
    )

    net = (
        gross
        - social
        - health
        - tax_after_discount
    )

    return {
        "gross": gross,
        "insurance_applies": applies,
        "social": social,
        "health": health,
        "tax_before_discount": tax_before_discount,
        "tax_after_discount": tax_after_discount,
        "net": net
    }


STEPS = [
    {
        "field": "gross",
        "label": "Hrubý příjem",
        "question": "Vypočítej hrubý příjem.",
        "hint": "Hrubý příjem = počet hodin × hodinová sazba.",
    },
    {
        "field": "social",
        "label": "Sociální pojištění zaměstnance",
        "question": "Vypočítej sociální pojištění zaměstnance.",
        "hint": "Pokud se pojistné platí, počítej 7,1 % z hrubého příjmu. Pokud se neplatí, zadej 0.",
    },
    {
        "field": "health",
        "label": "Zdravotní pojištění zaměstnance",
        "question": "Vypočítej zdravotní pojištění zaměstnance.",
        "hint": "Pokud se pojistné platí, počítej 4,5 % z hrubého příjmu. Pokud se neplatí, zadej 0.",
    },
    {
        "field": "tax_before_discount",
        "label": "Daň před slevou",
        "question": "Vypočítej daň před slevou na poplatníka.",
        "hint": "Daň před slevou = 15 % z hrubého příjmu.",
    },
    {
        "field": "tax_after_discount",
        "label": "Daň po slevě",
        "question": "Vypočítej daň po slevě na poplatníka.",
        "hint": "Daň po slevě = daň před slevou − 2 570 Kč. Pokud vyjde záporně, zadej 0.",
    },
    {
        "field": "net",
        "label": "Čistý příjem",
        "question": "Vypočítej čistý příjem.",
        "hint": "Čistý příjem = hrubý příjem − sociální − zdravotní − daň po slevě.",
    }
]


def current_grade(points, max_points):

    percent = round((points / max_points) * 100)

    if percent >= 90:
        return 1
    elif percent >= 80:
        return 2
    elif percent >= 70:
        return 3
    elif percent >= 60:
        return 4
    else:
        return 5


def init_game():

    session.clear()

    session["tasks"] = make_tasks()

    session["task_index"] = 0
    session["step_index"] = 0

    session["attempts"] = {}

    session["points"] = 0

    session["max_points"] = (
        len(SCENARIOS)
        * len(STEPS)
    )


@dane_bp.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        init_game()

        return redirect(url_for("dane.lesson"))

    return render_template(
        "dane_index.html",
        tasks=SCENARIOS,
        steps=STEPS,
        current_grade=5
    )


@dane_bp.route("/lesson", methods=["GET", "POST"])
def lesson():

    if "tasks" not in session:
        init_game()

    task_index = session.get("task_index", 0)
    step_index = session.get("step_index", 0)

    if task_index >= len(session["tasks"]):
        return redirect(url_for("dane.result"))

    task = session["tasks"][task_index]

    step = STEPS[step_index]

    key = f"{task_index}-{step_index}"

    error = False

    if request.method == "POST":

        user_answer = request.form.get(
            "answer",
            ""
        ).strip().replace(" ", "")

        try:
            answer = int(user_answer)
        except ValueError:
            answer = None

        correct_value = int(task[step["field"]])

        if answer == correct_value:

            attempts = session.get("attempts", {})

            if key not in attempts:
                attempts[key] = 0

            if attempts[key] == 0:
                session["points"] += 1
            else:
                session["points"] += 0.5

            attempts[key] += 1

            session["attempts"] = attempts

            step_index += 1

            if step_index >= len(STEPS):
                step_index = 0
                task_index += 1

            session["step_index"] = step_index
            session["task_index"] = task_index

            session.modified = True

            if task_index >= len(session["tasks"]):
                return redirect(url_for("dane.result"))

            return redirect(url_for("dane.lesson"))

        else:

            attempts = session.get("attempts", {})

            attempts[key] = attempts.get(key, 0) + 1

            session["attempts"] = attempts

            session.modified = True

            error = True

    done_steps = (
        task_index * len(STEPS)
        + step_index
    )

    total_steps = (
        len(session["tasks"])
        * len(STEPS)
    )

    progress = round(
        done_steps / total_steps * 100
    )

    attempts = session.get(
        "attempts",
        {}
    ).get(key, 0)

    points = session.get("points", 0)

    max_points = session.get("max_points", 18)

    current_grade_value = current_grade(
        points,
        max_points
    )

    return render_template(
        "dane_lesson.html",
        task=task,
        step=step,
        task_index=task_index,
        step_index=step_index,
        total_tasks=len(session["tasks"]),
        total_steps_per_task=len(STEPS),
        done_steps=done_steps,
        total_steps=total_steps,
        progress=progress,
        error=error,
        attempts=attempts,
        dpp_limit=DPP_LIMIT,
        dpc_limit=DPC_LIMIT,
        tax_discount=TAX_DISCOUNT,
        current_grade=current_grade_value,
        points=points,
        max_points=max_points
    )


@dane_bp.route("/result")
def result():

    points = session.get("points", 0)

    max_points = session.get(
        "max_points",
        18
    )

    percent = round(
        (points / max_points) * 100
    )

    grade = current_grade(
        points,
        max_points
    )

    tasks = session.get("tasks", [])

    best = (
        max(tasks, key=lambda t: t["net"])
        if tasks else None
    )

    return render_template(
        "dane_result.html",
        points=points,
        max_points=max_points,
        percent=percent,
        grade=grade,
        tasks=tasks,
        best=best
    )