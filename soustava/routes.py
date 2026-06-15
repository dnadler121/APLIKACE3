from flask import render_template, request, session, redirect, url_for, jsonify
from sympy import simplify
import random
import re
from flask import Blueprint

soustava_bp = Blueprint(
    "soustava",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ==================================================
# POMOCNÉ FUNKCE
# ==================================================

def normalize(expr):
    expr = str(expr).strip().replace(" ", "")
    expr = expr.replace("−", "-")
    expr = expr.replace(":", "/")
    expr = expr.replace(";", ",")

    # 3x -> 3*x, 2(x+1) -> 2*(x+1), x(x+1) -> x*(x+1)
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
    expr = re.sub(r'(\d)\(', r'\1*(', expr)
    expr = re.sub(r'([a-zA-Z])\(', r'\1*(', expr)
    expr = expr.replace(")(", ")*(")
    return expr


def equation_to_expression(eq):
    left, right = eq.split("=", 1)
    return simplify(f"({normalize(left)})-({normalize(right)})")


def kontrola(uzivatel, spravne):
    uzivatel = str(uzivatel).strip()
    spravne = str(spravne).strip()

    try:
        if "=" in spravne and "=" in uzivatel:
            expr_user = equation_to_expression(uzivatel)
            expr_correct = equation_to_expression(spravne)
            return simplify(expr_user - expr_correct) == 0

        return simplify(normalize(uzivatel) + "-(" + normalize(spravne) + ")") == 0
    except Exception:
        return normalize(uzivatel) == normalize(spravne)


def fmt_term(coef, var, first=False):
    if coef == 0:
        return ""
    sign = "" if first and coef > 0 else ("+" if coef > 0 else "-")
    abs_coef = abs(coef)
    num = "" if abs_coef == 1 else str(abs_coef)
    return f"{sign}{num}{var}"


def fmt_equation(ax, by, c):
    left = ""
    first = True
    if ax:
        left += fmt_term(ax, "x", first=True)
        first = False
    if by:
        left += fmt_term(by, "y", first=first)
    if not left:
        left = "0"
    return f"{left}={c}"


# ==================================================
# GENEROVÁNÍ SOUSTAVY
# ==================================================

def generuj_soustavu():
    """
    Vytvoříme soustavu vhodnou pro výuku sčítací metody.
    Vždy jde dobře odstranit x: první rovnici vynásobíme číslem -a2.

    Tvar:
        x + b1*y = c1
        a2*x + b2*y = c2
    """
    x = random.choice([i for i in range(-6, 7) if i != 0])
    y = random.choice([i for i in range(-6, 7) if i != 0])

    a1 = 1
    b1 = random.choice([1, 2, 3, 4, -1, -2, -3])
    a2 = random.choice([2, 3, 4, 5, -2, -3, -4])
    b2 = random.choice([1, 2, 3, 4, 5, -1, -2, -3, -4])

    # po vynásobení 1. rovnice číslem -a2 bude koeficient u y: -a2*b1
    # po sečtení s 2. rovnicí nesmí y zmizet
    if (-a2 * b1 + b2) == 0:
        return generuj_soustavu()

    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y

    multiplier = -a2
    mult_ax = multiplier * a1
    mult_by = multiplier * b1
    mult_c = multiplier * c1

    sum_y = mult_by + b2
    sum_c = mult_c + c2

    if sum_y == 0 or sum_c % sum_y != 0:
        return generuj_soustavu()

    y_result = sum_c // sum_y
    if y_result != y:
        return generuj_soustavu()

    zadani1 = fmt_equation(a1, b1, c1)
    zadani2 = fmt_equation(a2, b2, c2)
    vynasobena = fmt_equation(mult_ax, mult_by, mult_c)
    sectena = fmt_equation(0, sum_y, sum_c)

    return {
        "tema": "Soustava rovnic",
        "zadani1": zadani1,
        "zadani2": zadani2,
        "zadani": f"{zadani1} , {zadani2}",
        "a1": a1,
        "b1": b1,
        "c1": c1,
        "a2": a2,
        "b2": b2,
        "c2": c2,
        "multiplier": multiplier,
        "vynasobena": vynasobena,
        "sectena": sectena,
        "y_result": y,
        "x_result": x,
        "kroky": [
            {"spravne": "x"},
            {"spravne_rovnice": "1", "spravne_nasobek": str(multiplier), "spravne": vynasobena},
            {"spravne": sectena},
            {"spravne": f"y={y}"},
            {"spravne": fmt_equation(a1, b1 * y, c1).replace("y", "") if False else f"x{b1*y:+}={c1}"},
            {"spravne": f"x={x}"},
        ],
        "steps": [
            {"title": "Krok 1", "hint": "Vyber proměnnou, kterou budeme odstraňovat.", "vzor": "x"},
            {"title": "Krok 2", "hint": "Vyber rovnici a napiš číslo, kterým ji vynásobíme.", "vzor": f"1. rovnici násobíme číslem {multiplier}"},
            {"title": "Krok 3", "hint": "Zapiš rovnici, která vznikne po sečtení obou rovnic.", "vzor": sectena},
            {"title": "Krok 4", "hint": "Dopočítej hodnotu y.", "vzor": f"y={y}"},
            {"title": "Krok 5", "hint": "Dosaď vypočítané y do první původní rovnice.", "vzor": f"x{b1*y:+}={c1}"},
            {"title": "Krok 6", "hint": "Dopočítej hodnotu x.", "vzor": f"x={x}"},
        ]
    }


def vytvor_ulohy(pocet=5):
    return [generuj_soustavu() for _ in range(pocet)]


def spocitej_znamku(correct, total):
    if total == 0:
        return 5
    procenta = round((correct / total) * 100)
    if procenta >= 90:
        return 1
    elif procenta >= 80:
        return 2
    elif procenta >= 70:
        return 3
    elif procenta >= 60:
        return 4
    return 5


# ==================================================
# ROUTY
# ==================================================

@soustava_bp.route("/")
def home():
    session["uloha"] = 0
    session["correct_examples"] = 0
    session["ulohy"] = vytvor_ulohy()
    return redirect(url_for("soustava.soustavy"))


@soustava_bp.route("/soustavy/")
def soustavy():
    index = session.get("uloha", 0)
    ulohy = session.get("ulohy", [])

    if not ulohy:
        session["uloha"] = 0
        session["correct_examples"] = 0
        session["ulohy"] = vytvor_ulohy()
        ulohy = session["ulohy"]
        index = 0

    if index >= len(ulohy):
        total = len(ulohy)
        correct = session.get("correct_examples", 0)
        return render_template(
            "soustava_finish.html",
            total=total,
            correct=correct,
            procenta=round((correct / total) * 100) if total else 0,
            znamka=spocitej_znamku(correct, total)
        )

    uloha = ulohy[index]
    example = {
    "topic": uloha["tema"],
    "zadani1": uloha["zadani1"],
    "zadani2": uloha["zadani2"],
    "zadani": uloha["zadani"],
    "vynasobena": uloha["vynasobena"],

    "scitani_1": uloha["vynasobena"],
    "scitani_2": uloha["zadani2"],

    "steps": uloha["steps"]
    }   

    correct = session.get("correct_examples", 0)
    total = len(ulohy)

    return render_template(
        "soustava_soustavy.html",
        example=example,
        current=index + 1,
        total=total,
        correct=correct,
        znamka=spocitej_znamku(correct, total)
    )


@soustava_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json(silent=True) or {}
    step = int(data.get("step", 0)) - 1

    index = session.get("uloha", 0)
    ulohy = session.get("ulohy", [])

    if step < 0 or not ulohy or index >= len(ulohy):
        return jsonify({"correct": False})

    uloha = ulohy[index]

    # Krok 1: odstraníme x
    if step == 0:
        answer = str(data.get("answer", "")).strip().lower()
        return jsonify({"correct": answer == "x"})

    # Krok 2: žák vybírá rovnici a násobek
    if step == 1:
        rovnice = str(data.get("rovnice", "")).strip()
        nasobek = str(data.get("nasobek", "")).strip().replace("−", "-")
        correct = rovnice == "1" and nasobek == str(uloha["multiplier"])
        return jsonify({
            "correct": correct,
            "multiplied": uloha["vynasobena"] if correct else ""
        })

    answer = data.get("answer", "")

    # Krok 5: uznáme ekvivalentní rovnici po dosazení y do první rovnice
    spravne = uloha["kroky"][step]["spravne"]
    correct = kontrola(answer, spravne)

    return jsonify({"correct": correct})


@soustava_bp.route("/next/")
def next_example():
    session["correct_examples"] = session.get("correct_examples", 0) + 1
    session["uloha"] = session.get("uloha", 0) + 1
    ulohy = session.get("ulohy", [])
    finished = session["uloha"] >= len(ulohy)
    return jsonify({"finished": finished})


@soustava_bp.route("/reset/")
def reset():
    session["uloha"] = 0
    session["correct_examples"] = 0
    session["ulohy"] = vytvor_ulohy()
    return jsonify({"ok": True})
