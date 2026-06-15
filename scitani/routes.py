from flask import Flask, render_template, request, redirect, url_for, session
import random
from functools import reduce
from operator import mul

from flask import Blueprint

scitani_bp = Blueprint(
    "scitani",
    __name__,
    template_folder="templates",
    static_folder="static"
)

DIVISORS = [2,3,5,7,11]

def product(items):
    return reduce(mul, items, 1)

def make_item(value, next_id):
    return {
        "id": next_id,
        "value": value,
        "crossed": False,
        "used": False
    }

def generate_example():

    denominators = [2,3,4,5,6,8,9,10,12]

    a = random.randint(1,50)
    b = random.randint(1,50)

    d1 = random.choice(denominators)
    d2 = random.choice(denominators)

    return a,b,d1,d2

def is_prime(n):

    if n <= 1:
        return False

    d = 2

    while d*d <= n:

        if n % d == 0:
            return False

        d += 1

    return True

@scitani_bp.route("/")
def index():

    session["completed"] = 0

    a,b,d1,d2 = generate_example()

    session["a"] = a
    session["b"] = b
    session["d1"] = d1
    session["d2"] = d2

    session["rows"] = [
        [make_item(d1,1)],
        [make_item(d2,2)]
    ]

    session["original"] = [d1,d2]
    session["next_id"] = 3

    return render_template(
        "scitani_index.html",
        a=a,b=b,d1=d1,d2=d2
    )
@scitani_bp.route("/dalsi")
def dalsi():

    a,b,d1,d2 = generate_example()

    session["a"] = a
    session["b"] = b
    session["d1"] = d1
    session["d2"] = d2

    session["rows"] = [
        [make_item(d1,1)],
        [make_item(d2,2)]
    ]

    session["original"] = [d1,d2]
    session["next_id"] = 3

    return render_template(
        "scitani_index.html",
        a=a,b=b,d1=d1,d2=d2
    )

@scitani_bp.route("/rozklad", methods=["GET","POST"])
def rozklad():

    rows = session["rows"]
    error = None

    if request.method == "POST":

        if request.form.get("finish"):

            hotovo = True

            for row in rows:
                for item in row:
                    if not is_prime(item["value"]):
                        hotovo = False

            if hotovo:
                return redirect(url_for("scitani.skrtani"))

            else:
                error = "Ještě existuje číslo, které jde rozložit."

        else:

            try:
                row_index = int(request.form["row"])
                item_id = int(request.form["item"])
                divisor = int(request.form["divisor"])

            except:
                error = "Vyber číslo a dělitele."

            else:

                target = None

                for item in rows[row_index]:

                    if item["id"] == item_id:
                        target = item

                if target is None:
                    error = "Musíš vybrat číslo."

                elif target["value"] % divisor != 0:
                    error = "Tímto dělitelem nejde číslo rozložit."

                else:

                    value = target["value"]

                    rows[row_index].remove(target)

                    left = divisor
                    right = value // divisor

                    next_id = session["next_id"]

                    rows[row_index].append(make_item(left,next_id))
                    next_id += 1

                    if right != 1:
                        rows[row_index].append(make_item(right,next_id))
                        next_id += 1

                    session["next_id"] = next_id
                    session["rows"] = rows
                    session.modified = True

                    return redirect(url_for("scitani.rozklad"))

    return render_template(
        "scitani_rozklad.html",
        rows=rows,
        divisors=DIVISORS,
        original=session["original"],
        error=error,
        a=session["a"],
        b=session["b"],
        d1=session["d1"],
        d2=session["d2"]
    )

@scitani_bp.route("/skrtani",methods=["GET","POST"])
def skrtani():

    rows = session["rows"]
    error = None

    if request.method == "POST":

        if request.form.get("done"):

            lze_skrtat = False

            for item_a in rows[0]:

                if item_a.get("used", False):
                    continue

                for item_b in rows[1]:

                    if item_b.get("crossed", False):
                        continue

                    if item_a["value"] == item_b["value"]:
                        lze_skrtat = True

            if lze_skrtat:

                error = "Ještě můžeš něco vyškrtnout."

            else:

                final = []

                for row in rows:

                    for item in row:

                        if not item["crossed"]:
                            final.append(item["value"])

                session["final"] = final

                return redirect(url_for("scitani.citatele"))
        try:
            a = int(request.form["a"])
            b = int(request.form["b"])

        except:
            error = "Vyber dvě čísla."

        else:

            item_a = None
            item_b = None

            for item in rows[0]:

                if item["id"] == a:
                    item_a = item

            for item in rows[1]:

                if item["id"] == b:
                    item_b = item

            if item_a.get("used", False) or item_b.get("crossed", False):

                error = "Toto číslo už bylo vyškrtnuté."

            elif item_a["value"] != item_b["value"]:

                error = "Škrtat můžeš jen stejná čísla."

            else:

                item_a["used"] = True
                item_b["crossed"] = True

                session["rows"] = rows
                session.modified = True

                return redirect(url_for("scitani.skrtani"))

    return render_template(
        "scitani_skrtani.html",
        rows=rows,
        error=error,
        original=session["original"],
        a=session["a"],
        b=session["b"],
        d1=session["d1"],
        d2=session["d2"]
    )

@scitani_bp.route("/citatele", methods=["GET","POST"])
def citatele():

    nsn = product(session["final"])

    c1 = session["a"] * (nsn // session["d1"])
    c2 = session["b"] * (nsn // session["d2"])

    session["c1"] = c1
    session["c2"] = c2
    session["nsn"] = nsn

    error = None

    if request.method == "POST":

        value = request.form["value"].replace(" ","")

        if value == f"{c1}+{c2}":
            return redirect(url_for("scitani.vysledek"))

        else:
            error = "Špatný zápis."

    return render_template(
        "scitani_citatele.html",
        a=session["a"],
        b=session["b"],
        d1=session["d1"],
        d2=session["d2"],
        nsn=nsn,
        error=error
    )

@scitani_bp.route("/vysledek", methods=["GET","POST"])
def vysledek():

    error = None

    result = session["c1"] + session["c2"]

    if request.method == "POST":

        value = request.form["value"].strip()

        if value == str(result):

            session["completed"] += 1

            if session["completed"] >= 10:
                return redirect(url_for("scitani.konec"))

            return redirect(url_for("scitani.dalsi"))

        else:
            error = "Špatně."

    return render_template(
        "scitani_vysledek.html",
        c1=session["c1"],
        c2=session["c2"],
        nsn=session["nsn"],
        error=error
    )

@scitani_bp.route("/konec")
def konec():

    done = session["completed"]

    if done >= 10:
        grade = 1
    elif done >= 8:
        grade = 2
    elif done >= 6:
        grade = 3
    elif done >= 4:
        grade = 4
    else:
        grade = 5

    return render_template(
        "scitani_konec.html",
        done=done,
        grade=grade
    )

