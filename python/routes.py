
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import subprocess, sys, tempfile, os, ast
from flask import Blueprint

python_bp = Blueprint(
    "python",
    __name__,
    template_folder="templates",
    static_folder="static"
)

LESSONS = [
    {
        "id": 1,
        "title": "print() – první výpis",
        "goal": "Pochopit, že program může vypsat text.",
        "explain": "Funkce print() vypíše hodnotu na obrazovku. Text musí být v uvozovkách.",
        "starter": '# napiš svůj první příkaz pod tento řádek\n',
        "task": "Napiš program, který vypíše jednu vlastní větu.",
        "hints": [
            "Program musí něco vypsat na obrazovku.",
            "K výpisu se používá funkce print().",
            'Vzor: print("Tady je můj text")'
        ],
        "check_type": "print_any"
    },
    {
        "id": 2,
        "title": "Více řádků výstupu",
        "goal": "Použít print() vícekrát za sebou.",
        "explain": "Každý příkaz print() vypíše nový řádek.",
        "starter": 'print("První řádek")\n# doplň ještě další dva výpisy\n',
        "task": "Program musí vypsat alespoň tři řádky textu.",
        "hints": [
            "Jeden print() znamená jeden řádek.",
            "Budeš potřebovat tři příkazy print().",
            'Například:\nprint("A")\nprint("B")\nprint("C")'
        ],
        "check_type": "three_prints"
    },
    {
        "id": 3,
        "title": "Proměnná",
        "goal": "Uložit text do proměnné a vypsat ji.",
        "explain": "Proměnná je pojmenované místo pro hodnotu. Vytvoří se pomocí =.",
        "starter": '# vytvoř proměnnou a potom ji vypiš\n',
        "task": "Vytvoř proměnnou s textem a vypiš proměnnou pomocí print().",
        "hints": [
            "Nejdřív si něco ulož do proměnné.",
            "Proměnná se vytváří například: jmeno = \"Eva\".",
            'Celý tvar může být:\njmeno = "Eva"\nprint(jmeno)'
        ],
        "check_type": "variable_print"
    },
    {
        "id": 4,
        "title": "input() – vstup od uživatele",
        "goal": "Načíst hodnotu od uživatele jako ve VS Code.",
        "explain": "input() se v terminálu zeptá uživatele. V této aplikaci zadáš vstupy do simulovaného terminálu pod editorem.",
        "starter": '# načti vstup a vypiš ho\n',
        "task": "Načti jeden vstup pomocí input() a vypiš ho.",
        "hints": [
            "Budeš potřebovat input() i print().",
            "Výsledek inputu si ulož do proměnné.",
            'Vzor:\nodpoved = input("Napiš něco: ")\nprint(odpoved)'
        ],
        "check_type": "input_print"
    },
    {
        "id": 5,
        "title": "Dva vstupy",
        "goal": "Použít dvě proměnné a dva vstupy.",
        "explain": "Když potřebuješ dva údaje, zavoláš input() dvakrát. Hodnoty zadáš dole do simulovaného terminálu.",
        "starter": '# načti dvě hodnoty a vypiš je\n',
        "task": "Načti dvě hodnoty od uživatele a obě vypiš.",
        "hints": [
            "Budeš potřebovat dva inputy.",
            "Každý vstup si ulož do jiné proměnné.",
            'Vzor:\na = input("Zadej první hodnotu: ")\nb = input("Zadej druhou hodnotu: ")\nprint(a, b)'
        ],
        "check_type": "two_inputs"
    },
    {
        "id": 6,
        "title": "Komentář",
        "goal": "Použít komentář v programu.",
        "explain": "Komentář začíná znakem #. Python ho přeskočí, ale člověku pomáhá pochopit kód.",
        "starter": 'print("Program běží")\n',
        "task": "Doplň do programu komentář a ponech alespoň jeden funkční print().",
        "hints": [
            "Komentář začíná znakem #.",
            "Komentář může být na samostatném řádku.",
            '# toto je komentář\nprint("Program běží")'
        ],
        "check_type": "comment_print"
    },
    {
        "id": 7,
        "title": "int() – celé číslo",
        "goal": "Převést vstup z textu na celé číslo.",
        "explain": "input() načítá text. Pro počítání s celými čísly použij int(input()).",
        "starter": '# načti číslo a přičti k němu 1\n',
        "task": "Načti celé číslo pomocí int(input(...)) a vypiš výsledek nějakého výpočtu.",
        "hints": [
            "Samotný input() nestačí, protože načítá text.",
            "Použij int(input(...)).",
            'Vzor:\nvek = int(input("Zadej věk: "))\nprint(vek + 1)'
        ],
        "check_type": "int_math"
    },
    {
        "id": 8,
        "title": "Operátory + - * /",
        "goal": "Použít matematický operátor.",
        "explain": "Python umí s čísly počítat: +, -, *, /.",
        "starter": 'a = 12\nb = 3\n# vypiš alespoň dva různé výpočty\n',
        "task": "Použij alespoň dva různé matematické operátory a oba výsledky vypiš.",
        "hints": [
            "Operátory jsou +, -, *, /.",
            "Potřebuješ alespoň dva výpisy výpočtů.",
            'Například:\nprint(a + b)\nprint(a * b)'
        ],
        "check_type": "two_math_ops"
    },
    {
        "id": 9,
        "title": "float() – desetinné číslo",
        "goal": "Pracovat s desetinným číslem.",
        "explain": "float() převede vstup na desetinné číslo.",
        "starter": '# načti desetinné číslo a vypočítej s ním výsledek\n',
        "task": "Načti desetinné číslo pomocí float(input(...)) a použij ho ve výpočtu.",
        "hints": [
            "Pro desetinné číslo použij float().",
            "Vstup bude třeba 5.5.",
            'Vzor:\ncislo = float(input("Zadej číslo: "))\nprint(cislo * 2)'
        ],
        "check_type": "float_math"
    },
    {
        "id": 10,
        "title": "f-string",
        "goal": "Vložit proměnnou přímo do věty.",
        "explain": "f-string začíná písmenem f před uvozovkami. Proměnná se vkládá do { }.",
        "starter": 'jmeno = "Student"\n# vypiš větu, ve které použiješ proměnnou\n',
        "task": "Vypiš větu pomocí f-stringu a vlož do ní proměnnou.",
        "hints": [
            "Věta musí začínat f před uvozovkami.",
            "Proměnná se vkládá do složených závorek.",
            'Vzor:\nprint(f"Ahoj, {jmeno}")'
        ],
        "check_type": "fstring"
    },
    {
        "id": 11,
        "title": "Oprav chybu",
        "goal": "Najít a opravit syntaktickou chybu.",
        "explain": "Programátor často neprogramuje od nuly, ale hledá chyby v hotovém kódu.",
        "starter": 'pritn("Ahoj světe")\n',
        "task": "Oprav program tak, aby správně vypsal text.",
        "hints": [
            "Chyba je v názvu funkce.",
            "Python zná print(), ne překlep.",
            'Správně začíná: print('
        ],
        "check_type": "fix_print"
    },
    {
        "id": 12,
        "title": "Mini úkol – vizitka",
        "goal": "Spojit print(), proměnné a f-string.",
        "explain": "Malý program může spojit více jednoduchých dovedností dohromady.",
        "starter": '# vytvoř jednoduchou vizitku\n',
        "task": "Vytvoř alespoň dvě proměnné a vypiš alespoň dvě věty pomocí f-stringu.",
        "hints": [
            "Vytvoř například jméno a obor.",
            "Každou proměnnou použij ve f-stringu.",
            'jmeno = "Eva"\nobor = "kuchař"\nprint(f"Jmenuji se {jmeno}")\nprint(f"Studuji obor {obor}")'
        ],
        "check_type": "mini_project"
    }
]

def init_progress():
    session.permanent = True
    if "done" not in session:
        session["done"] = []
    if "hint_level" not in session:
        session["hint_level"] = {}

def is_unlocked(lesson_id):
    if lesson_id == 1:
        return True
    return (lesson_id - 1) in session.get("done", [])

def count_input_calls_in_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0
    return sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "input"
    )

def build_stdin_from_form(form, input_count):
    values = []
    for i in range(input_count):
        values.append(form.get(f"stdin_{i}", ""))
    return "\n".join(values) + ("\n" if input_count > 0 else "")

def run_code(code, stdin=""):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "student_code.py")

        safe_code = (
            "# -*- coding: utf-8 -*-\n"
            "import sys\n"
            "try:\n"
            "    sys.stdout.reconfigure(encoding='utf-8')\n"
            "    sys.stderr.reconfigure(encoding='utf-8')\n"
            "except Exception:\n"
            "    pass\n\n"
            + code
        )

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(safe_code)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", path],
                input=stdin,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=3,
                env=env
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "Program běžel příliš dlouho. Zkontroluj, jestli nemáš nekonečný cyklus."

def parse_code(code):
    try:
        return ast.parse(code), None
    except SyntaxError as e:
        return None, f"SyntaxError: {e.msg} na řádku {e.lineno}"

def calls(tree, name):
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name]

def has_print(tree): return bool(calls(tree, "print"))
def count_prints(tree): return len(calls(tree, "print"))
def count_inputs(tree): return len(calls(tree, "input"))
def has_assignment(tree): return any(isinstance(n, ast.Assign) for n in ast.walk(tree))
def has_comment(code): return any(line.strip().startswith("#") for line in code.splitlines())

def has_int_input(tree):
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "int"
        and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "input" for x in ast.walk(n))
        for n in ast.walk(tree)
    )

def has_float_input(tree):
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float"
        and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "input" for x in ast.walk(n))
        for n in ast.walk(tree)
    )

def math_ops(tree):
    found = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Add): found.add("+")
            if isinstance(n.op, ast.Sub): found.add("-")
            if isinstance(n.op, ast.Mult): found.add("*")
            if isinstance(n.op, ast.Div): found.add("/")
    return found

def fstring_count(tree):
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.JoinedStr))

def check_solution(lesson, code, output, error):
    tree, syntax_error = parse_code(code)
    if syntax_error:
        return False, "Program není syntakticky správně: " + syntax_error
    if error:
        return False, "Program se sice syntakticky načetl, ale při spuštění spadl. Podívej se do chybové hlášky."

    t = lesson["check_type"]
    if t == "print_any":
        return has_print(tree) and output.strip() != "", "Použij print() tak, aby program opravdu něco vypsal."
    if t == "three_prints":
        return count_prints(tree) >= 3 and len(output.splitlines()) >= 3, "Potřebuješ alespoň tři příkazy print() a tři řádky výstupu."
    if t == "variable_print":
        return has_assignment(tree) and has_print(tree), "Musí tam být proměnná vytvořená pomocí = a potom print()."
    if t == "input_print":
        return count_inputs(tree) >= 1 and has_assignment(tree) and has_print(tree), "Použij input(), ulož ho do proměnné a vypiš ji."
    if t == "two_inputs":
        return count_inputs(tree) >= 2 and has_print(tree), "Použij alespoň dva inputy a jeden print()."
    if t == "comment_print":
        return has_comment(code) and has_print(tree), "Doplň komentář začínající # a ponech funkční print()."
    if t == "int_math":
        return has_int_input(tree) and len(math_ops(tree)) >= 1 and has_print(tree), "Použij int(input(...)), výpočet a print()."
    if t == "two_math_ops":
        return len(math_ops(tree)) >= 2 and count_prints(tree) >= 2, "Použij alespoň dva různé operátory a vypiš dva výsledky."
    if t == "float_math":
        return has_float_input(tree) and len(math_ops(tree)) >= 1 and has_print(tree), "Použij float(input(...)), výpočet a print()."
    if t == "fstring":
        return fstring_count(tree) >= 1 and has_print(tree), "Použij f-string v printu, například print(f\"Ahoj {jmeno}\")."
    if t == "fix_print":
        return has_print(tree) and output.strip() != "", "Oprav překlep tak, aby program použil print() a něco vypsal."
    if t == "mini_project":
        return sum(isinstance(n, ast.Assign) for n in ast.walk(tree)) >= 2 and fstring_count(tree) >= 2 and count_prints(tree) >= 2, "Vytvoř dvě proměnné a vypiš dvě věty pomocí f-stringu."
    return False, "Neznámý typ kontroly."

@python_bp.route("/")
def index():
    init_progress()
    return render_template("python_index.html", lessons=LESSONS, done=session["done"], is_unlocked=is_unlocked)

@python_bp.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("python.index"))

@python_bp.route("/hint/<int:lesson_id>")
def hint(lesson_id):
    init_progress()
    levels = session.get("hint_level", {})
    key = str(lesson_id)
    levels[key] = min(levels.get(key, 0) + 1, 3)
    session["hint_level"] = levels
    return redirect(url_for("python.lesson", lesson_id=lesson_id))

@python_bp.route("/lesson/<int:lesson_id>", methods=["GET", "POST"])
def lesson(lesson_id):
    init_progress()
    if not is_unlocked(lesson_id):
        return redirect(url_for("python.index"))

    lesson = next((l for l in LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        return redirect(url_for("python.index"))

    code = lesson["starter"]
    output = ""
    error = ""
    message = ""
    success = False
    input_values = []
    terminal_note = ""

    if request.method == "POST":
        code = request.form.get("code", "")
        action = request.form.get("action", "run")
        input_count = count_input_calls_in_code(code)
        input_values = [request.form.get(f"stdin_{i}", "") for i in range(input_count)]
        stdin = build_stdin_from_form(request.form, input_count)
        output, error = run_code(code, stdin)

        if input_count > 0:
            terminal_note = f"Program požadoval {input_count} vstupů. Hodnoty byly zadány ručně v simulovaném terminálu."

        if action == "check":
            success, detail = check_solution(lesson, code, output, error)
            if success:
                message = "Výborně! Úkol je splněný a další lekce se odemkla."
                done = set(session["done"])
                done.add(lesson_id)
                session["done"] = sorted(done)
            else:
                message = "Ještě to není ono. " + detail
    else:
        input_count = count_input_calls_in_code(code)
        input_values = [""] * input_count

    next_id = lesson_id + 1 if lesson_id < len(LESSONS) else None
    prev_id = lesson_id - 1 if lesson_id > 1 else None
    hint_level = session.get("hint_level", {}).get(str(lesson_id), 0)

    return render_template("python_lesson.html", lesson=lesson, code=code, output=output, error=error,
                           message=message, success=success, next_id=next_id, prev_id=prev_id,
                           total=len(LESSONS), done=session["done"], hint_level=hint_level,
                           input_count=input_count, input_values=input_values,
                           terminal_note=terminal_note)

@python_bp.route("/teacher")
def teacher():
    init_progress()
    percent = round(len(session["done"]) / len(LESSONS) * 100)
    if percent >= 90:
        grade = 1
    elif percent >= 80:
        grade = 2
    elif percent >= 70:
        grade = 3
    elif percent >= 60:
        grade = 4
    else:
        grade = 5
    return render_template("python_teacher.html", lessons=LESSONS, done=session["done"], percent=percent, grade=grade)


