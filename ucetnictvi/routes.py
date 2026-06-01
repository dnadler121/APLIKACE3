from flask import render_template, request, redirect, url_for, session, Blueprint
import sqlite3
from datetime import datetime
from pathlib import Path

ucetnictvi_bp = Blueprint(
    "ucetnictvi",
    __name__,
    template_folder="templates",
    static_folder="static"
)

DB_PATH = Path(__file__).with_name("gastro.db")

VAT_RATE = 0.12
START_CASH = 10000


def current_grade(done):

    if done >= 16:
        return 1
    elif done >= 12:
        return 2
    elif done >= 8:
        return 3
    elif done >= 4:
        return 4
    else:
        return 5


OPERATIONS = [
    {"text": "Dodavatel přivezl maso do kuchyně za {net} Kč bez DPH.", "category": "naklad", "net": 1800},
    {"text": "Hosté zaplatili obědové menu za {gross} Kč včetně DPH.", "category": "trzba", "net": 4200},
    {"text": "Restaurace nakoupila zeleninu za {net} Kč bez DPH.", "category": "naklad", "net": 900},
    {"text": "Prodaly se domácí limonády za {gross} Kč včetně DPH.", "category": "trzba", "net": 1450},
    {"text": "Byla zaplacena elektřina za {net} Kč bez DPH.", "category": "naklad", "net": 700},
    {"text": "Hosté zaplatili dezerty za {gross} Kč včetně DPH.", "category": "trzba", "net": 1600},
    {"text": "Restaurace koupila pečivo za {net} Kč bez DPH.", "category": "naklad", "net": 550},
    {"text": "Prodaly se burgery za {gross} Kč včetně DPH.", "category": "trzba", "net": 3600},
    {"text": "Brigádník dostal mzdu za směnu {net} Kč. DPH se nepočítá.", "category": "naklad", "net": 1200, "vat_rate": 0},
    {"text": "Restaurace koupila nápoje do skladu za {net} Kč bez DPH.", "category": "naklad", "net": 1100},
    {"text": "Hosté zaplatili kávu za {gross} Kč včetně DPH.", "category": "trzba", "net": 950},
    {"text": "Restaurace zaplatila úklid za {net} Kč bez DPH.", "category": "naklad", "net": 600},
    {"text": "Proběhla větší rezervace, tržba byla {gross} Kč včetně DPH.", "category": "trzba", "net": 5200},
    {"text": "Dodavatel přivezl sýry za {net} Kč bez DPH.", "category": "naklad", "net": 800},
    {"text": "Prodaly se polévky za {gross} Kč včetně DPH.", "category": "trzba", "net": 1250},
    {"text": "Byla zaplacena reklama na sociálních sítích za {net} Kč bez DPH.", "category": "naklad", "net": 500},
    {"text": "Hosté zaplatili večeře za {gross} Kč včetně DPH.", "category": "trzba", "net": 4800},
    {"text": "Restaurace koupila čisticí prostředky za {net} Kč bez DPH.", "category": "naklad", "net": 400},
    {"text": "Prodaly se nealkoholické nápoje za {gross} Kč včetně DPH.", "category": "trzba", "net": 1800},
    {"text": "Na konci dne se rozbil mixér, oprava stála {net} Kč bez DPH.", "category": "naklad", "net": 750},
]


def money(value):
    return int(round(value))


def op_calc(op):

    rate = op.get("vat_rate", VAT_RATE)
    vat = money(op["net"] * rate)
    gross = op["net"] + vat

    return {
        **op,
        "vat": vat,
        "gross": gross,
        "rate_percent": int(rate * 100)
    }


def db():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    with db() as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                finished_at TEXT,
                current_step INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL,
                op_index INTEGER NOT NULL,
                operation_text TEXT NOT NULL,
                category TEXT NOT NULL,
                net INTEGER NOT NULL,
                vat INTEGER NOT NULL,
                gross INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(attempt_id, op_index)
            );

            CREATE TABLE IF NOT EXISTS final_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL,
                q1_revenues INTEGER NOT NULL,
                q2_expenses INTEGER NOT NULL,
                q3_profit INTEGER NOT NULL,
                q4_result TEXT NOT NULL,
                correct INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def get_attempt(attempt_id):

    with db() as conn:

        return conn.execute(
            "SELECT * FROM attempts WHERE id=?",
            (attempt_id,)
        ).fetchone()


def get_entries(attempt_id):

    with db() as conn:

        return conn.execute(
            "SELECT * FROM entries WHERE attempt_id=? ORDER BY op_index",
            (attempt_id,)
        ).fetchall()


def totals(entries):

    revenues = sum(
        e["net"] for e in entries
        if e["category"] == "trzba"
    )

    expenses = sum(
        e["net"] for e in entries
        if e["category"] == "naklad"
    )

    output_vat = sum(
        e["vat"] for e in entries
        if e["category"] == "trzba"
    )

    input_vat = sum(
        e["vat"] for e in entries
        if e["category"] == "naklad"
    )

    cash = (
        START_CASH
        + sum(e["gross"] for e in entries if e["category"] == "trzba")
        - sum(e["gross"] for e in entries if e["category"] == "naklad")
    )

    profit = revenues - expenses
    vat_due = output_vat - input_vat

    return {
        "revenues": revenues,
        "expenses": expenses,
        "profit": profit,
        "output_vat": output_vat,
        "input_vat": input_vat,
        "vat_due": vat_due,
        "cash": cash,
        "start_cash": START_CASH,
    }


@ucetnictvi_bp.before_request
def setup():
    init_db()


@ucetnictvi_bp.route("/", methods=["GET", "POST"])
def index():

    session["completed"] = 0

    if request.method == "POST":

        name = request.form.get("student_name", "").strip()

        if not name:

            grade = current_grade(session.get("completed", 0))

            return render_template(
                "index.html",
                error="Napiš prosím jméno nebo přezdívku.",
                grade=grade
            )

        with db() as conn:

            cur = conn.execute(
                """
                INSERT INTO attempts
                (student_name, created_at, current_step)
                VALUES (?, ?, 0)
                """,
                (
                    name,
                    datetime.now().isoformat(timespec="seconds")
                ),
            )

            attempt_id = cur.lastrowid

        session["attempt_id"] = attempt_id

        return redirect(url_for("ucetnictvi.game"))

    grade = current_grade(session.get("completed", 0))

    return render_template(
        "index.html",
        grade=grade
    )


@ucetnictvi_bp.route("/reset")
def reset():

    session.clear()

    return redirect(url_for("ucetnictvi.index"))


@ucetnictvi_bp.route("/game", methods=["GET", "POST"])
def game():

    attempt_id = session.get("attempt_id")

    if not attempt_id:
        return redirect(url_for("ucetnictvi.index"))

    attempt = get_attempt(attempt_id)

    if not attempt:
        session.clear()
        return redirect(url_for("ucetnictvi.index"))

    step = attempt["current_step"]

    entries = get_entries(attempt_id)

    side_totals = totals(entries)

    if step >= len(OPERATIONS):
        return redirect(url_for("ucetnictvi.result"))

    op = op_calc(OPERATIONS[step])

    text = op["text"].format(
        net=op["net"],
        vat=op["vat"],
        gross=op["gross"]
    )

    errors = []

    values = {}

    if request.method == "POST":

        values = {
            "category": request.form.get("category", ""),
            "net": request.form.get("net", ""),
            "vat": request.form.get("vat", ""),
            "gross": request.form.get("gross", ""),
        }

        try:

            net = int(values["net"])
            vat = int(values["vat"])
            gross = int(values["gross"])

        except ValueError:

            errors.append("Do částek piš pouze celá čísla v Kč.")

            net = vat = gross = None

        if values["category"] != op["category"]:
            errors.append("Špatná kolonka: rozhodni, jestli je to TRŽBA nebo NÁKLAD.")

        if net is not None and net != op["net"]:
            errors.append("Částka bez DPH není správně.")

        if vat is not None and vat != op["vat"]:
            errors.append("DPH není správně.")

        if gross is not None and gross != op["gross"]:
            errors.append("Celkem není správně.")

        if not errors:

            with db() as conn:

                conn.execute(
                    """
                    INSERT OR REPLACE INTO entries
                    (
                        attempt_id,
                        op_index,
                        operation_text,
                        category,
                        net,
                        vat,
                        gross,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        attempt_id,
                        step,
                        text,
                        op["category"],
                        op["net"],
                        op["vat"],
                        op["gross"],
                        datetime.now().isoformat(timespec="seconds")
                    ),
                )

                conn.execute(
                    "UPDATE attempts SET current_step=? WHERE id=?",
                    (step + 1, attempt_id)
                )

            session["completed"] += 1

            return redirect(url_for("ucetnictvi.game"))

    grade = current_grade(session.get("completed", 0))

    return render_template(
        "game.html",
        attempt=attempt,
        step=step,
        total_steps=len(OPERATIONS),
        operation_text=text,
        op=op,
        entries=entries,
        totals=side_totals,
        errors=errors,
        values=values,
        grade=grade
    )


@ucetnictvi_bp.route("/result", methods=["GET", "POST"])
def result():

    attempt_id = session.get("attempt_id")

    if not attempt_id:
        return redirect(url_for("ucetnictvi.index"))

    attempt = get_attempt(attempt_id)

    entries = get_entries(attempt_id)

    t = totals(entries)

    if len(entries) < len(OPERATIONS):
        return redirect(url_for("ucetnictvi.game"))

    feedback = None

    if request.method == "POST":

        try:

            q1 = int(request.form.get("q1_revenues", ""))
            q2 = int(request.form.get("q2_expenses", ""))
            q3 = int(request.form.get("q3_profit", ""))
            q4 = request.form.get("q4_result", "")

        except ValueError:

            feedback = {
                "ok": False,
                "text": "Do prvních tří odpovědí piš pouze čísla."
            }

        else:

            expected_result = (
                "zisk"
                if t["profit"] >= 0
                else "ztrata"
            )

            ok = (
                q1 == t["revenues"]
                and q2 == t["expenses"]
                and q3 == t["profit"]
                and q4 == expected_result
            )

            with db() as conn:

                conn.execute(
                    """
                    INSERT INTO final_answers
                    (
                        attempt_id,
                        q1_revenues,
                        q2_expenses,
                        q3_profit,
                        q4_result,
                        correct,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        attempt_id,
                        q1,
                        q2,
                        q3,
                        q4,
                        1 if ok else 0,
                        datetime.now().isoformat(timespec="seconds")
                    ),
                )

                if ok:

                    conn.execute(
                        "UPDATE attempts SET finished_at=? WHERE id=?",
                        (
                            datetime.now().isoformat(timespec="seconds"),
                            attempt_id
                        )
                    )

            feedback = {
                "ok": ok,
                "text":
                    "Výborně, restaurace je správně vyhodnocená."
                    if ok
                    else
                    "Ještě ne. Podívej se vpravo na výkaz a zkus odpovědi opravit."
            }

    grade = current_grade(session.get("completed", 0))

    return render_template(
        "result.html",
        attempt=attempt,
        entries=entries,
        totals=t,
        feedback=feedback,
        grade=grade
    )


@ucetnictvi_bp.route("/teacher")
def teacher():

    with db() as conn:

        attempts = conn.execute(
            "SELECT * FROM attempts ORDER BY id DESC LIMIT 100"
        ).fetchall()

    grade = current_grade(session.get("completed", 0))

    return render_template(
        "teacher.html",
        attempts=attempts,
        grade=grade
    )