
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sympy import simplify
import random
import re
from flask import Blueprint

rovnicejmenovatel_bp = Blueprint(
    "rovnicejmenovatel",
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==================================================
# NORMALIZACE A KONTROLA
# ==================================================

def normalize(expr):
    expr = str(expr).replace(" ", "")
    expr = expr.replace("−", "-")
    expr = expr.replace(":", "/")

    # 3x -> 3*x
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

    # 2(x-3) -> 2*(x-3)
    expr = re.sub(r'(\d)\(', r'\1*(', expr)

    # x(x-3) -> x*(x-3)
    expr = re.sub(r'([a-zA-Z])\(', r'\1*(', expr)

    expr = expr.replace(")(", ")*(")

    return expr


def equation_expr(eq):
    left, right = eq.split("=")
    return simplify(f"({normalize(left)})-({normalize(right)})")


def kontrola(user, correct):
    user = str(user).strip()
    correct = str(correct).strip()

    try:
        if "=" in user and "=" in correct:
            # Kontrola ekvivalentní rovnice
            return simplify(equation_expr(user) - equation_expr(correct)) == 0

        return simplify(normalize(user) + "-(" + normalize(correct) + ")") == 0

    except Exception:
        return normalize(user) == normalize(correct)


# ==================================================
# GENEROVÁNÍ ROVNIC
# ==================================================

def generuj_rovnici():
    """
    Generujeme rovnici tvaru:

        a/(x-b) + c = d

    tak, aby:
    - podmínka byla x ≠ b,
    - d bylo celé číslo,
    - řešení x bylo celé číslo,
    - řešení nebylo zakázané číslo b.
    """

    b = random.randint(2, 9)          # jmenovatel x-b
    c = random.randint(1, 6)          # číslo vedle zlomku
    d = random.randint(1, 8)          # pravá strana
    reseni = random.randint(-8, 12)   # celočíselné řešení

    if reseni == b:
        return generuj_rovnici()

    # z rovnice a/(x-b)+c=d dopočítáme a
    # a = (d-c)(reseni-b)
    a = (d - c) * (reseni - b)

    if a == 0:
        return generuj_rovnici()

    # nechceme příliš velká čísla
    if abs(a) > 20:
        return generuj_rovnici()

    zadani = f"{a}/(x-{b})+{c}={d}"

    # Krok 1: podmínka - student píše jen číslo
    krok1 = f"{b}"

    # Krok 2: vynásobení jmenovatelem
    # a + c(x-b) = d(x-b)
    krok2 = f"{a}+{c}(x-{b})={d}(x-{b})"

    # Krok 3: roznásobení závorek
    # a + cx - cb = dx - db
    left_const = a - c * b
    right_const = -d * b

    # Zobrazení ponecháme didakticky jako a+cx-cb=dx-db
    # Kontrola ale uzná i zjednodušený tvar.
    krok3_vzor = f"{a}+{c}x-{c*b}={d}x-{d*b}"
    krok3_spravne = f"{c}x{left_const:+}={d}x{right_const:+}"

    # Krok 4: neznámé na jednu stranu
    # cx - dx = right_const - left_const
    coef = c - d
    const = right_const - left_const

    if coef == 0:
        return generuj_rovnici()

    if const % coef != 0:
        return generuj_rovnici()

    vysledek = const // coef

    if vysledek != reseni:
        return generuj_rovnici()

    krok4 = f"{coef}x={const}"
    krok5 = f"x={vysledek}"

    return {
        "zadani": zadani,
        "reseni": vysledek,
        "kroky": [
            {"spravne": krok1},
            {"spravne": krok2},
            {"spravne": krok3_spravne},
            {"spravne": krok4},
            {"spravne": krok5}
        ],
        "steps": [
            {
                "title": "Krok 1",
                "hint": "Napiš pouze číslo, které nesmí vyjít ve jmenovateli.",
                "vzor": f"{b}"
            },
            {
                "title": "Krok 2",
                "hint": "Vynásob celou rovnici jmenovatelem.",
                "vzor": krok2
            },
            {
                "title": "Krok 3",
                "hint": "Roznásob závorky. Můžeš nechat čísla ještě nesečtená.",
                "vzor": krok3_vzor
            },
            {
                "title": "Krok 4",
                "hint": "Převeď neznámé na jednu stranu a čísla na druhou stranu.",
                "vzor": krok4
            },
            {
                "title": "Krok 5",
                "hint": "Vypočítej x.",
                "vzor": krok5
            }
        ]
    }


def vytvor_ulohy(pocet=5):
    return [generuj_rovnici() for _ in range(pocet)]


def znamka(correct, total):
    if total == 0:
        return 5

    p = round((correct / total) * 100)

    if p >= 90:
        return 1
    elif p >= 80:
        return 2
    elif p >= 70:
        return 3
    elif p >= 60:
        return 4
    else:
        return 5


# ==================================================
# ROUTY
# ==================================================

@rovnicejmenovatel_bp.route("/")
def home():
    session["uloha"] = 0
    session["correct"] = 0
    session["ulohy"] = vytvor_ulohy()
    return redirect(url_for("rovnicejmenovatel.rovnice"))


@rovnicejmenovatel_bp.route("/rovnice/")
def rovnice():
    index = session.get("uloha", 0)
    ulohy = session.get("ulohy", [])

    if not ulohy:
        session["uloha"] = 0
        session["correct"] = 0
        session["ulohy"] = vytvor_ulohy()
        ulohy = session["ulohy"]
        index = 0

    if index >= len(ulohy):
        total = len(ulohy)
        correct = session.get("correct", 0)

        return render_template(
            "rovnicejmenovatel_finish.html",
            total=total,
            correct=correct,
            procenta=round((correct / total) * 100) if total else 0,
            znamka=znamka(correct, total)
        )

    uloha = ulohy[index]

    return render_template(
        "rovnicejmenovatel_rovnice.html",
        example=uloha,
        current=index + 1,
        total=len(ulohy),
        correct=session.get("correct", 0),
        znamka=znamka(session.get("correct", 0), len(ulohy))
    )


@rovnicejmenovatel_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    step = int(data["step"]) - 1
    answer = data["answer"]

    index = session.get("uloha", 0)
    uloha = session["ulohy"][index]

    spravne = uloha["kroky"][step]["spravne"]

    # Krok 1: stačí přesně číslo podmínky
    if step == 0:
        correct = normalize(answer) == normalize(spravne)
    else:
        correct = kontrola(answer, spravne)

    return jsonify({"correct": correct})


@rovnicejmenovatel_bp.route("/next/")
def next_example():
    session["correct"] = session.get("correct", 0) + 1
    session["uloha"] = session.get("uloha", 0) + 1

    done = session["uloha"] >= len(session["ulohy"])

    return jsonify({"finished": done})


@rovnicejmenovatel_bp.route("/reset/")
def reset():
    session["uloha"] = 0
    session["correct"] = 0
    session["ulohy"] = vytvor_ulohy()
    return jsonify({"ok": True})


