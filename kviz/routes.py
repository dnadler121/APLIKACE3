from flask import Flask, render_template, request, redirect, url_for, session
import random
import unicodedata
from flask import Blueprint

kviz_bp = Blueprint(
    "kviz",
    __name__,
    template_folder="templates",
    static_folder="static"
)

QUESTIONS = [
    {
        "q": "Doplň číslo v řadě: 3, 6, 12, 24, ?",
        "a": [
            "48"
        ],
        "hint": "Každé číslo se zdvojnásobí."
    },
    {
        "q": "Doplň číslo v řadě: 2, 5, 9, 14, 20, ?",
        "a": [
            "27"
        ],
        "hint": "Přičítá se 3, 4, 5, 6..."
    },
    {
        "q": "Co nepatří mezi čísla: 4, 8, 12, 15, 16, 20?",
        "a": [
            "15"
        ],
        "hint": "Hledej číslo, které není násobkem 4."
    },
    {
        "q": "V každé krabici jsou 3 talíře. Máme 4 krabice. Kolik talířů je celkem?",
        "a": [
            "12"
        ],
        "hint": "4 × 3."
    },
    {
        "q": "Co je větší: polovina ze 100, nebo čtvrtina z 240?",
        "a": [
            "ctvrtina z 240",
            "čtvrtina z 240",
            "60"
        ],
        "hint": "Polovina ze 100 je 50, čtvrtina z 240 je 60."
    },
    {
        "q": "Dnes je středa. Jaký den bude za 10 dní?",
        "a": [
            "sobota"
        ],
        "hint": "Za 7 dní bude znovu středa."
    },
    {
        "q": "Doplň číslo v řadě: 1, 4, 9, 16, ?",
        "a": [
            "25"
        ],
        "hint": "Jsou to druhé mocniny."
    },
    {
        "q": "Co nepatří: nůž, vidlička, lžíce, talíř?",
        "a": [
            "talir",
            "talíř"
        ],
        "hint": "Tři věci jsou příbory."
    },
    {
        "q": "Tři kuchaři připravili dohromady 12 porcí. Každý stejně. Kolik porcí připravil jeden?",
        "a": [
            "4"
        ],
        "hint": "12 : 3."
    },
    {
        "q": "Kód začíná číslem 2. Druhá číslice je dvojnásobek první, třetí je dvojnásobek druhé. Jaký je kód?",
        "a": [
            "248"
        ],
        "hint": "2, potom 4, potom 8."
    },
    {
        "q": "Doplň číslo: 10, 20, 40, 80, ?",
        "a": [
            "160"
        ],
        "hint": "Násobíme dvěma."
    },
    {
        "q": "Na stole je 6 sklenic: 2 plné, 2 poloplné a 2 prázdné. Kolik sklenic je na stole?",
        "a": [
            "6"
        ],
        "hint": "Ptáme se na počet sklenic, ne na obsah."
    },
    {
        "q": "Doplň číslo: 100, 90, 80, 70, ?",
        "a": [
            "60"
        ],
        "hint": "Odečítáme 10."
    },
    {
        "q": "Objednávky stojí 120 Kč, 80 Kč a 50 Kč. Kolik stojí dohromady?",
        "a": [
            "250"
        ],
        "hint": "120 + 80 + 50."
    },
    {
        "q": "Najdi chybějící číslo: 5 + ? = 13",
        "a": [
            "8"
        ],
        "hint": "13 − 5."
    },
    {
        "q": "Máš nádoby 5 l a 3 l. Jaké množství chceš získat v klasické hádance?",
        "a": [
            "4",
            "4l",
            "4 l"
        ],
        "hint": "Cílem je dostat přesně 4 litry."
    },
    {
        "q": "Doplň číslo: 7, 14, 21, 28, ?",
        "a": [
            "35"
        ],
        "hint": "Přičítá se 7."
    },
    {
        "q": "Které číslo je liché: 18, 24, 31, 40?",
        "a": [
            "31"
        ],
        "hint": "Liché číslo není dělitelné dvěma."
    },
    {
        "q": "Kolik je 25 % ze 200?",
        "a": [
            "50"
        ],
        "hint": "Čtvrtina z 200."
    },
    {
        "q": "Doplň číslo: 2, 4, 7, 11, 16, ?",
        "a": [
            "22"
        ],
        "hint": "Přičítá se 2, 3, 4, 5, 6."
    },
    {
        "q": "Host zaplatil 500 Kč. Účet byl 268 Kč. Kolik vrátíš?",
        "a": [
            "232"
        ],
        "hint": "500 − 268."
    },
    {
        "q": "Co je větší: 3 × 18, nebo 4 × 13?",
        "a": [
            "3x18",
            "3×18",
            "54"
        ],
        "hint": "3 × 18 = 54, 4 × 13 = 52."
    },
    {
        "q": "V krabici je 5 pizz. Dvě krabice jsou plné a jedna má jen 3 pizzy. Kolik pizz je celkem?",
        "a": [
            "13"
        ],
        "hint": "5 + 5 + 3."
    },
    {
        "q": "Doplň číslo: 81, 27, 9, 3, ?",
        "a": [
            "1"
        ],
        "hint": "Dělíme třemi."
    },
    {
        "q": "Kolik minut je 1 hodina a půl?",
        "a": [
            "90"
        ],
        "hint": "60 + 30."
    },
    {
        "q": "Co nepatří: 2, 3, 5, 8, 11?",
        "a": [
            "8"
        ],
        "hint": "Ostatní čísla jsou prvočísla."
    },
    {
        "q": "Doplň: 1, 2, 4, 7, 11, ?",
        "a": [
            "16"
        ],
        "hint": "Přičítá se 1, 2, 3, 4, 5."
    },
    {
        "q": "Když 4 jablka stojí 40 Kč, kolik stojí 7 jablek?",
        "a": [
            "70"
        ],
        "hint": "Jedno jablko stojí 10 Kč."
    },
    {
        "q": "Kolik je třetina z 90?",
        "a": [
            "30"
        ],
        "hint": "90 : 3."
    },
    {
        "q": "Doplň číslo: 6, 12, 18, 24, ?",
        "a": [
            "30"
        ],
        "hint": "Přičítá se 6."
    },
    {
        "q": "Na účtu je 320 Kč. Host dá 500 Kč. Kolik se vrací?",
        "a": [
            "180"
        ],
        "hint": "500 − 320."
    },
    {
        "q": "Které číslo chybí: 4, 9, 14, 19, ?",
        "a": [
            "24"
        ],
        "hint": "Přičítá se 5."
    },
    {
        "q": "Máš 3 stoly, u každého sedí 4 hosté. Dva hosté odejdou. Kolik hostů zůstane?",
        "a": [
            "10"
        ],
        "hint": "3 × 4 = 12, potom −2."
    },
    {
        "q": "Kód trezoru je složen z výsledků: 2+3, 10−4, 3×3. Jaký je kód?",
        "a": [
            "569"
        ],
        "hint": "Výsledky napiš za sebe."
    },
    {
        "q": "Finální otázka: Doplň číslo: 2, 6, 12, 20, 30, ?",
        "a": [
            "42"
        ],
        "hint": "Přičítá se 4, 6, 8, 10, 12."
    }
]

def normalize(text):
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace(" ", "")
    return text

@kviz_bp.route("/")
def index():
    session.clear()
    return render_template("kviz_index.html", total=len(QUESTIONS))

@kviz_bp.route("/start")
def start():
    order = list(range(len(QUESTIONS)))
    random.shuffle(order)
    session["order"] = order
    session["current"] = 0
    session["score"] = 0
    session["wrong"] = 0
    session["attempts"] = 0
    return redirect(url_for("kviz.question"))

@kviz_bp.route("/question", methods=["GET", "POST"])
def question():
    order = session.get("order")
    if not order:
        return redirect(url_for("kviz.index"))

    current = session.get("current", 0)
    if current >= len(order):
        return redirect(url_for("kviz.finish"))

    item = QUESTIONS[order[current]]
    message = ""
    show_hint = False

    if request.method == "POST":
        user_answer = request.form.get("answer", "")
        good_answers = [normalize(ans) for ans in item["a"]]

        if normalize(user_answer) in good_answers:
            session["score"] += 1
            session["current"] += 1
            session["attempts"] = 0
            return redirect(url_for("kviz.question"))
        else:
            session["wrong"] += 1
            session["attempts"] += 1
            message = "🔒 Špatně. Dveře zůstávají zamčené."
            show_hint = session["attempts"] >= 2

    progress = int((current / len(order)) * 100)

    return render_template(
        "kviz_question.html",
        item=item,
        number=current + 1,
        total=len(order),
        score=session.get("score", 0),
        wrong=session.get("wrong", 0),
        attempts=session.get("attempts", 0),
        message=message,
        show_hint=show_hint,
        progress=progress
    )

@kviz_bp.route("/skip")
def skip():
    session["current"] = session.get("current", 0) + 1
    session["attempts"] = 0
    return redirect(url_for("kviz.question"))

@kviz_bp.route("/finish")
def finish():
    score = session.get("score", 0)
    total = len(QUESTIONS)
    percent = round(score / total * 100)

    if percent >= 90:
        grade = "1"
        title = "🏆 Matematický šampion"
    elif percent >= 80:
        grade = "2"
        title = "🔥 Výborný hráč"
    elif percent >= 70:
        grade = "3"
        title = "🙂 Dobrá práce"
    elif percent >= 60:
        grade = "4"
        title = "🛠️ Prošel jsi hrou"
    else:
        grade = "5"
        title = "😅 Restaurace přežila jen těsně"

    return render_template("kviz_finish.html", score=score, total=total, percent=percent, grade=grade, title=title, wrong=session.get("wrong", 0))

