
from flask import Flask, render_template, request, session, redirect, url_for
import random
from flask import Blueprint

intervaly_bp = Blueprint(
    "intervaly",
    __name__,
    template_folder="templates",
    static_folder="static"
)

def random_interval():
    values = list(range(-8,9))

    a = random.choice(values)
    b = random.choice(values)

    while a >= b:
        a = random.choice(values)
        b = random.choice(values)

    left = random.choice(["(", "["])
    right = random.choice([")", "]"])

    return {
        "a": a,
        "b": b,
        "left": left,
        "right": right
    }

def text(i):
    return f"{i['left']}{i['a']}; {i['b']}{i['right']}"

def normalize(s):

    s = s.replace(" ", "")
    s = s.replace("∪", "U")
    s = s.replace("u", "U")
    s = s.lower()

    # pokud je mezi dvěma intervaly čárka,
    # změní ji na U
    s = s.replace("),(", ")U(")
    s = s.replace("],[", "]U[")
    s = s.replace("),[", ")U[")
    s = s.replace("],(", "]U(")

    return s

def intersection(A,B):

    start = max(A["a"], B["a"])
    end = min(A["b"], B["b"])

    if start > end:
        return "∅"

    left_closed = (
        (start > A["a"] or A["left"] == "[")
        and
        (start > B["a"] or B["left"] == "[")
    )

    right_closed = (
        (end < A["b"] or A["right"] == "]")
        and
        (end < B["b"] or B["right"] == "]")
    )

    if start == end and not(left_closed and right_closed):
        return "∅"

    left = "[" if left_closed else "("
    right = "]" if right_closed else ")"

    return f"{left}{start}; {end}{right}"

def union(A,B):

    first = A if A["a"] <= B["a"] else B
    second = B if A["a"] <= B["a"] else A

    separate = (
        first["b"] < second["a"]
        or
        (
            first["b"] == second["a"]
            and
            first["right"] == ")"
            and
            second["left"] == "("
        )
    )

    if separate:
        return f"{text(first)} U {text(second)}"

    start = min(A["a"], B["a"])
    end = max(A["b"], B["b"])

    left_closed = (
        A["left"] == "[" if A["a"] < B["a"]
        else B["left"] == "[" if B["a"] < A["a"]
        else A["left"] == "[" or B["left"] == "["
    )

    right_closed = (
        A["right"] == "]" if A["b"] > B["b"]
        else B["right"] == "]" if B["b"] > A["b"]
        else A["right"] == "]" or B["right"] == "]"
    )

    left = "[" if left_closed else "("
    right = "]" if right_closed else ")"

    return f"{left}{start}; {end}{right}"

def create_example():

    A = random_interval()
    B = random_interval()

    current = session.get("current", 0)

    if current % 2 == 0:
        operation = "průnik"
    else:
        operation = "sjednocení"

    if operation == "průnik":
        result = intersection(A,B)
    else:
        result = union(A,B)

    return {
        "A": A,
        "B": B,
        "operation": operation,
        "result": result
    }

@intervaly_bp.route("/", methods=["GET","POST"])
def index():

    if "examples" not in session:

        session["examples"] = [create_example() for _ in range(10)]
        session["current"] = 0
        session["correct"] = 0

    current = session["current"]

    if current >= 10:

        score = session["correct"]

        if score >= 9:
            grade = 1
        elif score >= 7:
            grade = 2
        elif score >= 5:
            grade = 3
        elif score >= 3:
            grade = 4
        else:
            grade = 5

        return render_template(
            "intervaly_finish.html",
            score=score,
            grade=grade
        )

    example = session["examples"][current]

    message = ""

    if request.method == "POST":

        answer = normalize(request.form.get("answer",""))
        correct = normalize(example["result"])
        if correct == "∅":

            if answer in ["∅", "nic", "prazdne"]:

                session["correct"] += 1
                session["current"] += 1

                return redirect(url_for("intervaly.index"))
        if answer == correct:

            session["correct"] += 1
            session["current"] += 1

            return redirect(url_for("intervaly.index"))

        else:
            message = "Špatně. Zkus to znovu."

    return render_template(
        "intervaly_index.html",
        example=example,
        current=current+1,
        message=message
    )

@intervaly_bp.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("intervaly.index"))


