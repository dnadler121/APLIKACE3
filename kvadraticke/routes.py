
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sympy import simplify
import random, re, math
from flask import Blueprint

kvadraticke_bp = Blueprint(
    "kvadraticke",
    __name__,
    template_folder="templates",
    static_folder="static"
)

def normalize(expr):
    expr = str(expr).replace(" ", "").replace("−", "-").replace(",", ".")
    expr = expr.replace("^", "**")
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

def format_rovnice(a, b, c):
    if a == 1:
        text = "x²"
    elif a == -1:
        text = "-x²"
    else:
        text = f"{a}x²"
    if b > 0:
        text += f"+{b}x"
    elif b < 0:
        text += f"{b}x"
    if c > 0:
        text += f"+{c}"
    elif c < 0:
        text += f"{c}"
    return text + "=0"

def generuj_priklad():
    a = random.randint(1, 4)
    r1 = random.randint(-8, 8)
    r2 = random.randint(-8, 8)
    if r1 == 0 or r2 == 0 or r1 == r2:
        return generuj_priklad()

    b = -a * (r1 + r2)
    c = a * r1 * r2

    if abs(b) > 30 or abs(c) > 90:
        return generuj_priklad()
    if b == 0 or c == 0:
        return generuj_priklad()

    D = b*b - 4*a*c
    sqrtD = math.isqrt(D)
    if sqrtD * sqrtD != D:
        return generuj_priklad()

    x_plus = (-b + sqrtD)
    x_minus = (-b - sqrtD)
    if x_plus % (2*a) != 0 or x_minus % (2*a) != 0:
        return generuj_priklad()

    x1 = x_plus // (2*a)
    x2 = x_minus // (2*a)
    vetsi = max(x1, x2)
    mensi = min(x1, x2)

    return {
        "zadani": format_rovnice(a, b, c),
        "steps": [
            {"title":"Krok 1a","hint":"Urči koeficient a – číslo před x².","vzor":"u 2x²+5x-3=0 je a = 2","spravne":str(a)},
            {"title":"Krok 1b","hint":"Urči koeficient b – číslo před x.","vzor":"u 2x²+5x-3=0 je b = 5","spravne":str(b)},
            {"title":"Krok 1c","hint":"Urči koeficient c – samotné číslo bez x.","vzor":"u 2x²+5x-3=0 je c = -3","spravne":str(c)},
            {"title":"Krok 2","hint":"Spočítej diskriminant: D = b² - 4ac.","vzor":"D = 5² - 4·2·(-3) = 49","spravne":str(D)},
            {"title":"Krok 3","hint":"Spočítej odmocninu z diskriminantu.","vzor":"√49 = 7","spravne":str(sqrtD)},
            {"title":"Krok 4","hint":"Spočítej větší kořen x₁ = (-b + √D) / 2a.","vzor":"x₁ = (-5 + 7) / 4 = 1/2","spravne":str(vetsi)},
            {"title":"Krok 5","hint":"Spočítej menší kořen x₂ = (-b - √D) / 2a.","vzor":"x₂ = (-5 - 7) / 4 = -3","spravne":str(mensi)}
        ]
    }

def vytvor_ulohy(pocet=10):
    return [generuj_priklad() for _ in range(pocet)]

def znamka(correct, total):
    if total == 0:
        return 5
    p = round((correct / total) * 100)
    if p >= 90: return 1
    if p >= 80: return 2
    if p >= 70: return 3
    if p >= 60: return 4
    return 5

@kvadraticke_bp.route("/")
def home():
    session["uloha"] = 0
    session["correct"] = 0
    session["ulohy"] = vytvor_ulohy()
    return redirect(url_for("kvadraticke.kvadraticke"))

@kvadraticke_bp.route("/kvadraticke/")
def kvadraticke():
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
        return render_template("kvadraticke_finish.html", total=total, correct=correct,
                               procenta=round((correct/total)*100) if total else 0,
                               znamka=znamka(correct, total))

    return render_template("kvadraticke_kvadraticke.html", example=ulohy[index],
                           current=index+1, total=len(ulohy),
                           correct=session.get("correct", 0),
                           znamka=znamka(session.get("correct", 0), len(ulohy)))

@kvadraticke_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    step = int(data["step"]) - 1
    answer = data["answer"]
    index = session.get("uloha", 0)
    spravne = session["ulohy"][index]["steps"][step]["spravne"]
    return jsonify({"correct": kontrola(answer, spravne)})

@kvadraticke_bp.route("/next/")
def next_example():
    session["correct"] = session.get("correct", 0) + 1
    session["uloha"] = session.get("uloha", 0) + 1
    return jsonify({"finished": session["uloha"] >= len(session["ulohy"])})

@kvadraticke_bp.route("/reset/")
def reset():
    session["uloha"] = 0
    session["correct"] = 0
    session["ulohy"] = vytvor_ulohy()
    return jsonify({"ok": True})


