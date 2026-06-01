from flask import Flask, render_template, request, session, redirect, jsonify
from sympy import simplify
import re
import random

from flask import Blueprint
matematika_bp = Blueprint(
"matematika",
__name__,
template_folder="templates",
static_folder="static"
)


# ==================================================
# POMOCNÉ FUNKCE
# ==================================================

def normalize(expr):

    expr = expr.replace(" ", "")

    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

    expr = re.sub(r'(\d)\(', r'\1*(', expr)

    expr = re.sub(r'([a-zA-Z])\(', r'\1*(', expr)

    expr = expr.replace(")(", ")*(")
    expr = re.sub(r'(\d)\(', r'\1*(', expr)

    return expr


def equation_to_expression(eq):

    left, right = eq.split("=")

    return simplify(f"({left})-({right})")


def kontrola(uzivatel, spravne):
    uzivatel = uzivatel.replace("inf", "∞")
    spravne = spravne.replace("inf", "∞")

    uzivatel = normalize(uzivatel)
    spravne = normalize(spravne)

    try:

        # rovnice
        if "=" in spravne and "=" in uzivatel:

            expr_user = equation_to_expression(uzivatel)
            expr_correct = equation_to_expression(spravne)

            return simplify(expr_user - expr_correct) == 0

        # intervaly
        if "(" in spravne or "∅" in spravne:
            return uzivatel == spravne

        # nerovnice
        if ">" in spravne or "<" in spravne:
            return uzivatel == spravne

        return simplify(uzivatel) == simplify(spravne)

    except:
        return uzivatel == spravne


# ==================================================
# GENEROVÁNÍ ROVNICE
# ==================================================

def generuj_rovnici():

    x = random.randint(-6, 6)

    while x == 0:
        x = random.randint(-6, 6)

    j = random.randint(2, 8)

    a = j * random.randint(2, 6)

    b = j - x

    c = random.randint(1, 5)

    prava = a // j + c

    zadani = f"{a}/(x{b:+})+{c}={prava}"

    # KROK 1
    krok1 = f"{a}+{c}*(x{b:+})={prava}*(x{b:+})"

    # KROK 2
    leva_konst = c * b
    prava_konst = prava * b

    krok2 = f"{a}+{c}x{leva_konst:+}={prava}x{prava_konst:+}"

    # KROK 3
    krok3 = f"{c}x-{prava}x={prava_konst}{-leva_konst:+}{-a:+}"

    # KROK 4
    leva = c - prava

    prava_strana = prava_konst - leva_konst - a

    krok4 = f"{leva}x={prava_strana}"

    
    # KROK 5
    vysledek = prava_strana // leva

    krok5 = f"x={vysledek}"

    return {

        "tema": "Rovnice se jmenovatelem",

        "vzor": [
            "2/(x+3)+5=7",
            "2+5*(x+3)=7*(x+3)",
            "2+5x+15=7x+21",
            "5x-7x=21-15-2",
            "-2x=4",
            "x=-2"
        ],

        "zadani": zadani,

        "kroky": [

            {
                "spravne": krok1
            },

            {
                "spravne": krok2
            },

            {
                "spravne": krok3
            },

            {
                "spravne": krok4
            },

            {
                "spravne": krok5
            },

            
        ]
    }

# ==================================================
# INTERVALY
# ==================================================

def generuj_intervaly():

    a = random.randint(-10, 3)
    b = random.randint(a + 2, 10)

    c = random.randint(-10, 3)
    d = random.randint(c + 2, 10)

    typ = random.choice(["∩", "∪"])

    interval1 = f"({a},{b})"
    interval2 = f"({c},{d})"

    if typ == "∩":

        levy = max(a, c)
        pravy = min(b, d)

        if levy >= pravy:
            vysledek = "∅"

        else:
            vysledek = f"({levy},{pravy})"

    else:

        levy = min(a, c)
        pravy = max(b, d)

        vysledek = f"({levy},{pravy})"

    return {

        "tema": "Intervaly",

        "vzor": [
            "(1,5) ∩ (3,7)",
            "(3,5)"
        ],

        "zadani": f"{interval1} {typ} {interval2}",

        "kroky": [

            {
                "spravne": vysledek
            }

        ]
    }


# ==================================================
# NEROVNICE
# ==================================================

def generuj_nerovnici():

    a = random.randint(1, 9)
    b = random.randint(1, 9)

    znamenko1 = random.choice(["+", "-"])
    znamenko2 = random.choice(["+", "-"])

    if znamenko1 == "+":
        horni = f"(x+{a})"
        nulovy1 = -a
    else:
        horni = f"(x-{a})"
        nulovy1 = a

    if znamenko2 == "+":
        dolni = f"(x+{b})"
        nulovy2 = -b
    else:
        dolni = f"(x-{b})"
        nulovy2 = b

    zadani = f"{horni}/{dolni}>0"

    mensi = min(nulovy1, nulovy2)
    vetsi = max(nulovy1, nulovy2)

    vysledek = f"(-inf,{mensi}),({vetsi},inf)"

    return {

        "tema": "Nerovnice",

        "vzor": [

            "(x-5)/(x+8)>0",

            "Nulové body:",
            "x=5",
            "x=-8",

            "Výsledek:",
            "(-inf,-8),(5,inf)"

        ],

        "zadani": zadani,

        "kroky": [

            {
                "spravne": f"x={nulovy1}"
            },

            {
                "spravne": f"x={nulovy2}"
            },

            {
                "spravne": vysledek
            }

        ]
    }
# ==================================================
# SOUSTAVY
# ==================================================

def generuj_soustavu():

    x = random.randint(-5, 5)
    y = random.randint(-5, 5)

    while x == 0:
        x = random.randint(-5, 5)

    while y == 0:
        y = random.randint(-5, 5)

    a1 = random.randint(1, 4)
    b1 = random.randint(1, 5)

    nasobek = random.randint(2, 4)

    a2 = a1 * nasobek
    b2 = random.randint(1, 5)

    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y

    zadani = (
        f"{a1}x+{b1}y={c1} , "
        f"{a2}x+{b2}y={c2}"
    )

    # vynásobená první rovnice
    nx = -a2
    ny = -(b1 * nasobek)
    nc = -(c1 * nasobek)

    krok2 = f"{nx}x{ny:+}y={nc}"

    # součet
    vys_y = ny + b2
    vys_c = nc + c2

    if vys_y == 0:
        return generuj_soustavu()

    if vys_c % vys_y != 0:
        return generuj_soustavu()

    krok3 = f"{vys_y}y={vys_c}"

    # y
    krok4 = f"y={y}"

    # dosazení
    krok5 = f"{a1}x+{b1}({y})={c1}"

    # x
    krok6 = f"x={x}"

    return {

        "tema": "Soustava rovnic",

        "a2": a2,

        "zadani": zadani,

        "kroky": [

            {
                "spravne": "x"
            },

            {
                "spravne": krok2
            },

            {
                "spravne": krok3
            },

            {
                "spravne": krok4
            },

            {
                "spravne": krok5
            },

            {
                "spravne": krok6
            }

        ],

        "steps": [

            {
                "title": "Krok 1",
                "hint": "Napiš proměnnou, kterou odstraníme",
                "vzor": "x"
            },

            {
                "title": "Krok 2",
                "hint": "Vynásob jednu rovnici tak, aby šlo odstranit x",
                "vzor": "-12x-3y=-51"
            },

            {
                "title": "Krok 3",
                "hint": "Sečti obě rovnice",
                "vzor": "2y=10"
            },

            {
                "title": "Krok 4",
                "hint": "Dopočítej y",
                "vzor": "y=5"
            },

            {
                "title": "Krok 5",
                "hint": "Dosadíme y do první rovnice",
                "vzor": "4x+1(5)=17"
            },

            {
                "title": "Krok 6",
                "hint": "Dopočítej x",
                "vzor": "x=3"
            }

]
    }
# ==================================================
# VYTVOŘENÍ ÚLOH
# ==================================================

def vytvor_ulohy():

    return [

        generuj_rovnici(),

        generuj_intervaly(),

        generuj_nerovnici(),

        generuj_soustavu()

    ]


# ==================================================
# ROUTY
# ==================================================

@matematika_bp.route("/")
def home():

    session["uloha"] = 0

    session["ulohy"] = vytvor_ulohy()

    return redirect("matematika/")


@matematika_bp.route("/matematika/")
def matematika():

    index = session.get("uloha", 0)

    ulohy = session.get("ulohy", [])

    if index >= len(ulohy):

        return render_template(
            "matematika_finish.html",
            total=len(ulohy)
        )

    uloha = ulohy[index]

    # pokud úloha nemá vlastní steps
    if "steps" not in uloha:

        example = {

            "topic": uloha["tema"],

            "zadani": uloha["zadani"],

            "steps": [

                {
                    "title": f"Krok {i+1}",
                    "hint": "Doplň celý krok",

                    # POSUN O 1
                    "vzor": (
                        uloha["vzor"][i + 1]
                        if i + 1 < len(uloha["vzor"])
                        else ""
                    )
                }

                for i in range(len(uloha["kroky"]))

            ]
        }

    else:

        example = {

            "topic": uloha["tema"],

            "zadani": uloha["zadani"],

            # SOUSTAVY ZŮSTANOU STEJNÉ
            "steps": uloha["steps"]

        }

    return render_template(
        "matematika_matematika.html",
        example=example,
        current=index + 1,
        total=len(ulohy)
    )


@matematika_bp.route("/check", methods=["POST"])
def check():

    data = request.get_json()

    step = data["step"] - 1
    answer = data["answer"]

    index = session.get("uloha", 0)
    ulohy = session.get("ulohy", [])

    uloha = ulohy[index]

    # KROK 2 U SOUSTAV
    if uloha["tema"] == "Soustava rovnic" and step == 1:

        try:

            user = normalize(answer)

            leva, prava = user.split("=")

            match = re.match(
                r'([+-]?\d*)\*?x([+-]\d*)\*?y',
                leva
            )

            if not match:

                correct = False

            else:

                ux_text = match.group(1)

                if ux_text in ["", "+"]:
                    ux = 1

                elif ux_text == "-":
                    ux = -1

                else:
                    ux = int(ux_text)

                a2 = uloha["a2"]

                # po sečtení musí zmizet x
                correct = (ux + a2 == 0)

        except:

            correct = False

        return jsonify({
            "correct": correct
        })

    # klasická kontrola
    spravne = uloha["kroky"][step]["spravne"]

    correct = kontrola(answer, spravne)

    return jsonify({
        "correct": correct
    })


@matematika_bp.route("/next/")
def next_example():

    session["uloha"] += 1

    ulohy = session.get("ulohy", [])

    finished = session["uloha"] >= len(ulohy)

    return jsonify({
        "finished": finished
    })


@matematika_bp.route("/reset/")
def reset():

    session["uloha"] = 0

    session["ulohy"] = vytvor_ulohy()

    return jsonify({
        "ok": True
    })


