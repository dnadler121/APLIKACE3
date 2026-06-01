from flask import Blueprint, render_template, request, redirect, url_for, session
import random
from functools import reduce
from operator import mul

nsn_bp = Blueprint(
    "nsn",
    __name__,
    template_folder="templates",
    static_folder="static"
)

DIVISORS = [2, 3, 5, 7, 11]


def product(items):
    return reduce(mul, items, 1)


def make_item(value, next_id):
    return {
        "id": next_id,
        "value": value,
        "crossed": False
    }


def generate_example():

    while True:

        a = random.randint(10, 100)
        b = random.randint(10, 100)

        if a != b:
            return a, b


def is_prime(n):

    if n <= 1:
        return False

    d = 2

    while d * d <= n:

        if n % d == 0:
            return False

        d += 1

    return True


@nsn_bp.route("/")
def index():

    if "completed" not in session:
        session["completed"] = 0

    a, b = generate_example()

    session["rows"] = [
        [make_item(a, 1)],
        [make_item(b, 2)]
    ]

    session["original"] = [a, b]
    session["next_id"] = 3

    return render_template(
        "nsn_index.html",
        a=a,
        b=b
    )


@nsn_bp.route("/rozklad", methods=["GET", "POST"])
def rozklad():

    rows = session["rows"]

    error = None

    if request.method == "POST" and request.form.get("custom"):

        try:

            a = int(request.form["custom_a"])
            b = int(request.form["custom_b"])

        except:
            error = "Zadej dvě čísla."

        else:

            session["rows"] = [
                [make_item(a, 1)],
                [make_item(b, 2)]
            ]

            session["original"] = [a, b]
            session["next_id"] = 3

            session.modified = True

            return redirect(url_for("nsn.rozklad"))

    if request.method == "POST" and not request.form.get("custom"):

        if request.form.get("finish"):

            hotovo = True

            for row in rows:

                for item in row:

                    if not is_prime(item["value"]):
                        hotovo = False

            if hotovo:
                return redirect(url_for("nsn.skrtani"))

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

                    rows[row_index].append(
                        make_item(left, next_id)
                    )

                    next_id += 1

                    if right != 1:

                        rows[row_index].append(
                            make_item(right, next_id)
                        )

                        next_id += 1

                    session["next_id"] = next_id
                    session["rows"] = rows

                    session.modified = True

                    return redirect(url_for("nsn.rozklad"))

    return render_template(
        "nsn_rozklad.html",
        rows=rows,
        divisors=DIVISORS,
        original=session["original"],
        error=error
    )


@nsn_bp.route("/skrtani", methods=["GET", "POST"])
def skrtani():

    rows = session["rows"]

    error = None

    if request.method == "POST":

        if request.form.get("done"):

            final = []

            for row in rows:

                for item in row:

                    if not item["crossed"]:
                        final.append(item["value"])

            session["final"] = final

            return redirect(url_for("nsn.nasobeni"))

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

            if item_b["crossed"]:

                error = "Toto číslo už bylo vyškrtnuté."

            elif item_a["value"] != item_b["value"]:

                error = "Škrtat můžeš jen stejná čísla."

            else:

                item_b["crossed"] = True

                session["rows"] = rows
                session.modified = True

                return redirect(url_for("nsn.skrtani"))

    return render_template(
        "nsn_skrtani.html",
        rows=rows,
        error=error,
        original=session["original"]
    )


@nsn_bp.route("/nasobeni", methods=["GET", "POST"])
def nasobeni():

    final = session["final"]

    result = product(final)

    error = None

    if request.method == "POST":

        try:

            value = int(request.form["value"])

        except:
            error = "Napiš číslo."

        else:

            if value == result:

                session["completed"] += 1

                return redirect(url_for("nsn.vysledek"))

            else:
                error = "Špatně."

    return render_template(
        "nsn_nasobeni.html",
        final=final,
        error=error
    )


@nsn_bp.route("/vysledek")
def vysledek():

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
        "nsn_vysledek.html",
        done=done,
        grade=grade
    )