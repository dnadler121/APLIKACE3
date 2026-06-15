
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sympy import simplify
import random
import re
from flask import Blueprint

algebra_bp = Blueprint(
    "algebra",
    __name__,
    template_folder="templates",
    static_folder="static"
)


def normalize(expr):
    expr = str(expr).replace(" ", "")
    expr = expr.replace("−", "-").replace(",", ".").replace("^", "**")
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
    expr = re.sub(r'(\d)\(', r'\1*(', expr)
    expr = re.sub(r'([a-zA-Z])\(', r'\1*(', expr)
    expr = expr.replace(")(", ")*(")
    return expr


def kontrola(user, correct):
    try:
        return simplify(normalize(user) + "-(" + normalize(correct) + ")") == 0
    except Exception:
        return normalize(user) == normalize(correct)


def signed(num):
    return f"+{num}" if num >= 0 else str(num)


def format_linear(a, var):
    if a == 1:
        return var
    if a == -1:
        return "-" + var
    return f"{a}{var}"


def priklad_vytykani():
    k = random.randint(2, 9)
    a = random.randint(2, 8)
    b = random.randint(1, 12)
    if random.choice([True, False]):
        b = -b

    zadani = f"{k*a}x{signed(k*b)}"
    reseni = f"{k}({a}x{signed(b)})"

    return {
        "typ": "Vytýkání",
        "zadani": zadani,
        "reseni": reseni,
        "hint": "Vytkni největší společný číselný násobek před závorku.",
        "vzor": "6x+12 → 6(x+2)"
    }


def priklad_roznasobovani():
    k = random.randint(2, 9)
    a = random.randint(1, 8)
    b = random.randint(1, 12)
    if random.choice([True, False]):
        b = -b

    zadani = f"{k}({a}x{signed(b)})"
    reseni = f"{k*a}x{signed(k*b)}"

    return {
        "typ": "Roznásobování",
        "zadani": zadani,
        "reseni": reseni,
        "hint": "Vynásob číslem před závorkou každý člen v závorce.",
        "vzor": "3(x-4) → 3x-12"
    }


def priklad_scitani_clenu():
    ax1 = random.randint(1, 8)
    ax2 = random.randint(1, 8) * random.choice([1, -1])
    ay1 = random.randint(1, 8)
    ay2 = random.randint(1, 8) * random.choice([1, -1])
    c1 = random.randint(1, 10)
    c2 = random.randint(1, 10) * random.choice([1, -1])

    zadani = f"{ax1}x{signed(ay1)}y{signed(ax2)}x{signed(ay2)}y{signed(c1)}{signed(c2)}"

    sx = ax1 + ax2
    sy = ay1 + ay2
    sc = c1 + c2

    parts = []
    if sx != 0:
        parts.append(format_linear(sx, "x"))

    if sy != 0:
        y_text = format_linear(sy, "y")
        if parts and sy > 0:
            y_text = "+" + y_text
        parts.append(y_text)

    if sc != 0:
        parts.append(signed(sc) if parts else str(sc))

    if not parts:
        return priklad_scitani_clenu()

    return {
        "typ": "Sčítání stejných členů",
        "zadani": zadani,
        "reseni": "".join(parts),
        "hint": "Sečti zvlášť členy s x, zvlášť členy s y a zvlášť samotná čísla.",
        "vzor": "3x+2y+4x-y → 7x+y"
    }


def generuj_priklad(page_index):
    if page_index in [0, 1]:
        return priklad_vytykani()
    if page_index in [2, 3]:
        return priklad_roznasobovani()
    if page_index in [4, 5]:
        return priklad_scitani_clenu()
    return random.choice([priklad_vytykani, priklad_roznasobovani, priklad_scitani_clenu])()


def vytvor_stranky(pocet=10):
    return [
        {"cislo": i + 1, "priklady": [generuj_priklad(i), generuj_priklad(i)]}
        for i in range(pocet)
    ]


def znamka(correct_pages, total_pages):
    if total_pages == 0:
        return 5
    p = round((correct_pages / total_pages) * 100)
    if p >= 90:
        return 1
    if p >= 80:
        return 2
    if p >= 70:
        return 3
    if p >= 60:
        return 4
    return 5


@algebra_bp.route("/")
def home():
    session["page"] = 0
    session["correct_pages"] = 0
    session["pages"] = vytvor_stranky()
    return redirect(url_for("algebra.algebra"))


@algebra_bp.route("/algebra/")
def algebra():
    pages = session.get("pages", [])
    page_index = session.get("page", 0)

    if not pages:
        session["page"] = 0
        session["correct_pages"] = 0
        session["pages"] = vytvor_stranky()
        pages = session["pages"]
        page_index = 0

    if page_index >= len(pages):
        total = len(pages)
        correct = session.get("correct_pages", 0)
        return render_template(
            "algebra_finish.html",
            total=total,
            correct=correct,
            procenta=round((correct / total) * 100) if total else 0,
            znamka=znamka(correct, total)
        )

    return render_template(
        "algebra_algebra.html",
        page=pages[page_index],
        current=page_index + 1,
        total=len(pages),
        correct=session.get("correct_pages", 0),
        znamka=znamka(session.get("correct_pages", 0), len(pages))
    )


@algebra_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    answer1 = data.get("answer1", "")
    answer2 = data.get("answer2", "")

    pages = session.get("pages", [])
    page_index = session.get("page", 0)

    if not pages or page_index >= len(pages):
        return jsonify({"ok": False})

    p1 = pages[page_index]["priklady"][0]
    p2 = pages[page_index]["priklady"][1]

    correct1 = kontrola(answer1, p1["reseni"])
    correct2 = kontrola(answer2, p2["reseni"])

    return jsonify({
        "ok": correct1 and correct2,
        "correct1": correct1,
        "correct2": correct2
    })


@algebra_bp.route("/next/")
def next_page():
    session["correct_pages"] = session.get("correct_pages", 0) + 1
    session["page"] = session.get("page", 0) + 1
    return jsonify({"finished": session["page"] >= len(session.get("pages", []))})


@algebra_bp.route("/reset/")
def reset():
    session["page"] = 0
    session["correct_pages"] = 0
    session["pages"] = vytvor_stranky()
    return jsonify({"ok": True})



