
# Samostatná Flask aplikace – Soustavy rovnic

Toto je vytažený samostatný modul ze širší matematické aplikace.
Obsahuje pouze téma **soustavy rovnic**.

## Spuštění

```bash
pip install -r requirements.txt
python app.py
```

Potom otevři:

```text
http://127.0.0.1:5000
```

## Co aplikace dělá

- generuje soustavy rovnic s celočíselným řešením,
- vede studenta krok za krokem sčítací metodou,
- další krok se odemkne až po správné odpovědi,
- po vyřešení příkladu se pokračuje na další soustavu,
- na konci zobrazí úspěšnost a známku.

## Kde změnit počet příkladů

V souboru `app.py` najdi funkci:

```python
def vytvor_ulohy(pocet=5):
```

a změň číslo `5` například na `10`.
