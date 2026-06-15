
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from sympy import simplify
import random, re
from flask import Blueprint

rovnice_bp = Blueprint(
    "rovnice",
    __name__,
    template_folder="templates",
    static_folder="static"
)

def normalize(expr):
    expr = str(expr).replace(" ", "")
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
    expr = re.sub(r'(\d)\(', r'\1*(', expr)
    return expr

def equation_expr(eq):
    left,right = eq.split("=")
    return simplify(f"({normalize(left)})-({normalize(right)})")

def kontrola(user, correct):
    try:
        return simplify(equation_expr(user)-equation_expr(correct)) == 0
    except:
        return normalize(user)==normalize(correct)

def generuj():
    while True:
        a = random.randint(2,6)
        d = random.randint(1,5)

        if a == d:
            continue

        b = random.randint(1,9)
        x = random.randint(-8,12)

        if x == 0:
            continue

        c = x*(a-d)-d*b+a*b

        if c == 0 or abs(c) > 40:
            continue

        coef = a-d
        konst = d*b-(a*b-c)

        if konst % coef != 0:
            continue

        zadani = f"{a}(x+{b})-{c}={d}(x+{b})"

        krok1 = f"{a}x+{a*b}-{c}={d}x+{d*b}"
        krok2 = f"{a}x-{d}x={d*b}-{a*b-c}"
        krok3 = f"{coef}x={konst}"
        krok4 = f"x={konst//coef}"

        return {
            "zadani": zadani,
            "steps":[
                {"title":"Krok 1","hint":"Roznásob závorky.","vzor":"3x+15-3=2x+10","spravne":krok1},
                {"title":"Krok 2","hint":"Převeď x na jednu stranu.","vzor":"3x-2x=10-12","spravne":krok2},
                {"title":"Krok 3","hint":"Sečti a odečti členy.","vzor":"x=-2","spravne":krok3},
                {"title":"Krok 4","hint":"Vypočítej x.","vzor":"x=-2","spravne":krok4}
            ]
        }

def vytvor():
    return [generuj() for _ in range(10)]

def znamka(c,t):
    p = round((c/t)*100)
    if p>=90:return 1
    if p>=80:return 2
    if p>=70:return 3
    if p>=60:return 4
    return 5

@rovnice_bp.route("/")
def home():
    session["uloha"]=0
    session["correct"]=0
    session["ulohy"]=vytvor()
    return redirect(url_for("rovnice.rovnice"))

@rovnice_bp.route("/rovnice/")
def rovnice():

    idx=session["uloha"]
    ulohy=session["ulohy"]

    if idx>=len(ulohy):
        total=len(ulohy)
        correct=session["correct"]

        return render_template(
            "rovnice_finish.html",
            total=total,
            correct=correct,
            procenta=round((correct/total)*100),
            znamka=znamka(correct,total)
        )

    return render_template(
        "rovnice_rovnice.html",
        example=ulohy[idx],
        current=idx+1,
        total=len(ulohy),
        correct=session["correct"],
        znamka=znamka(max(session["correct"],1),len(ulohy))
    )

@rovnice_bp.route("/check", methods=["POST"])
def check():
    data=request.get_json()

    step=int(data["step"])-1
    answer=data["answer"]

    idx=session["uloha"]

    spravne=session["ulohy"][idx]["steps"][step]["spravne"]

    return jsonify({"correct":kontrola(answer,spravne)})

@rovnice_bp.route("/next/")
def next_example():
    session["correct"]+=1
    session["uloha"]+=1

    return jsonify({
        "finished":session["uloha"]>=len(session["ulohy"])
    })

@rovnice_bp.route("/reset/")
def reset():
    session["uloha"]=0
    session["correct"]=0
    session["ulohy"]=vytvor()

    return jsonify({"ok":True})


