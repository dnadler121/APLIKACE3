from flask import Flask, render_template, request, session, redirect, url_for
import random
from flask import Blueprint

nerovnice_bp = Blueprint(
    "nerovnice",
    __name__,
    template_folder="templates",
    static_folder="static"
)

TOTAL = 10


def fmt_signed(n):
    if n >= 0:
        return f"+{n}"
    return str(n)


def factor_text(root):
    # kořen root znamená závorku x-root
    if root >= 0:
        return f"x-{root}"
    return f"x+{abs(root)}"


def normalize(s):
    s = s.strip().lower()
    s = s.replace(" ", "")
    s = s.replace("∞", "inf")
    s = s.replace("∪", ",")
    s = s.replace("u", ",")
    s = s.replace("∅", "nic")
    s = s.replace("prazdne", "nic")
    s = s.replace("prázdné", "nic")
    return s


def norm_interval(s):
    s = normalize(s)
    s = s.replace("),(", "),(")
    return s


def solution_for(num_root, den_root, sign):
    # (x-num_root)/(x-den_root) sign 0, ostré nerovnosti
    low = min(num_root, den_root)
    high = max(num_root, den_root)

    if sign == ">":
        # stejné znaménko: vlevo i vpravo
        return f"(-inf;{low}),({high};inf)"
    else:
        # opačné znaménko: mezi nulovými body
        return f"({low};{high})"


def make_example(index):
    values = list(range(-8, 9))
    num_root = random.choice(values)
    den_root = random.choice(values)
    while den_root == num_root:
        den_root = random.choice(values)

    # pravidelně střídáme > a <
    sign = ">" if index % 2 == 0 else "<"

    numerator = factor_text(num_root)
    denominator = factor_text(den_root)

    # pro >0: oba kladné NEBO oba záporné
    # pro <0: čitatel kladný a jmenovatel záporný NEBO čitatel záporný a jmenovatel kladný
    if sign == ">":
        case1 = {
            "n_ineq": f"{numerator}>0",
            "d_ineq": f"{denominator}>0",
            "n_solved": f"x>{num_root}",
            "d_solved": f"x>{den_root}",
        }
        case2 = {
            "n_ineq": f"{numerator}<0",
            "d_ineq": f"{denominator}<0",
            "n_solved": f"x<{num_root}",
            "d_solved": f"x<{den_root}",
        }
    else:
        case1 = {
            "n_ineq": f"{numerator}>0",
            "d_ineq": f"{denominator}<0",
            "n_solved": f"x>{num_root}",
            "d_solved": f"x<{den_root}",
        }
        case2 = {
            "n_ineq": f"{numerator}<0",
            "d_ineq": f"{denominator}>0",
            "n_solved": f"x<{num_root}",
            "d_solved": f"x>{den_root}",
        }

    return {
        "num_root": num_root,
        "den_root": den_root,
        "numerator": numerator,
        "denominator": denominator,
        "sign": sign,
        "task": f"({numerator})/({denominator}) {sign} 0",
        "case1": case1,
        "case2": case2,
        "result": solution_for(num_root, den_root, sign),
    }


def ensure_session():
    if "nerovnice_examples" not in session:
        session["nerovnice_examples"] = [make_example(i) for i in range(TOTAL)]
        session["nerovnice_current"] = 0
        session["nerovnice_score"] = 0
        session["nerovnice_checked1"] = False
        session["nerovnice_checked2"] = False


def current_example():
    ensure_session()
    return session["nerovnice_examples"][session["nerovnice_current"]]


def empty_values():
    return {
        "c1n": "", "c1d": "", "s1n": "", "s1d": "",
        "c2n": "", "c2d": "", "s2n": "", "s2d": "",
        "result": "",
    }


@nerovnice_bp.route("/", methods=["GET", "POST"])
def index():
    ensure_session()

    if session["nerovnice_current"] >= TOTAL:
        score = session["nerovnice_score"]
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

        return render_template("nerovnice_finish.html", score=score, total=TOTAL, grade=grade)

    ex = current_example()
    message = ""
    errors = []
    values = empty_values()

    if request.method == "POST":
        step = request.form.get("step", "")
        values = {key: request.form.get(key, "") for key in values}

        expected = {
            "c1n": ex["case1"]["n_ineq"],
            "c1d": ex["case1"]["d_ineq"],
            "s1n": ex["case1"]["n_solved"],
            "s1d": ex["case1"]["d_solved"],
            "c2n": ex["case2"]["n_ineq"],
            "c2d": ex["case2"]["d_ineq"],
            "s2n": ex["case2"]["n_solved"],
            "s2d": ex["case2"]["d_solved"],
            "result": ex["result"],
        }

        if step == "check_case1":
            keys = ["c1n", "c1d", "s1n", "s1d"]
            errors = [key for key in keys if norm_interval(values[key]) != norm_interval(expected[key])]

            if not errors:
                session["nerovnice_checked1"] = True
                message = "✅ 1. průnik je správně. Pokračuj na 2. průnik."
            else:
                session["nerovnice_checked1"] = False
                message = "1. průnik není celý správně. Oprav červená políčka."

        elif step == "check_case2":
            keys = ["c2n", "c2d", "s2n", "s2d"]
            errors = [key for key in keys if norm_interval(values[key]) != norm_interval(expected[key])]

            if not errors:
                session["nerovnice_checked2"] = True
                message = "✅ 2. průnik je správně. Teď zapiš celkový výsledek."
            else:
                session["nerovnice_checked2"] = False
                message = "2. průnik není celý správně. Oprav červená políčka."

        elif step == "check_result":
            # Nejdřív musí být ověřené oba průniky.
            if not session.get("nerovnice_checked1"):
                errors = ["c1n", "c1d", "s1n", "s1d"]
                message = "Nejdřív zkontroluj a oprav 1. průnik."
            elif not session.get("nerovnice_checked2"):
                errors = ["c2n", "c2d", "s2n", "s2d"]
                message = "Nejdřív zkontroluj a oprav 2. průnik."
            elif norm_interval(values["result"]) == norm_interval(expected["result"]):
                session["nerovnice_score"] += 1
                session["nerovnice_current"] += 1
                session["nerovnice_checked1"] = False
                session["nerovnice_checked2"] = False
                return redirect(url_for("nerovnice.index"))
            else:
                errors = ["result"]
                message = "Celkový výsledek není správně. Zkontroluj sjednocení průniků."

    return render_template(
        "nerovnice_index.html",
        ex=ex,
        current=session["nerovnice_current"] + 1,
        total=TOTAL,
        message=message,
        errors=errors,
        values=values,
        checked1=session.get("nerovnice_checked1", False),
        checked2=session.get("nerovnice_checked2", False),
    )


@nerovnice_bp.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("nerovnice.index"))



