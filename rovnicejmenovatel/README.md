
# Flask aplikace – Rovnice s neznámou ve jmenovateli

Samostatná výuková aplikace.

## Spuštění

```bash
pip install -r requirements.txt
python app.py
```

Potom otevři:

```text
http://127.0.0.1:5000
```

## Co aplikace umí

- generuje rovnice s neznámou ve jmenovateli,
- vede žáka krok za krokem,
- další krok se odemkne až po správné odpovědi,
- na konci zobrazí známku.

## Změna počtu příkladů

Najdi v `app.py`:

```python
def vytvor_ulohy(pocet=5):
```

a změň číslo.


## Upraveno
- rovnice nyní generují pouze celočíselná řešení


## Opraveno ve verzi easy_v2
- vzor u každého kroku se nyní generuje podle aktuální rovnice
- krok 3 akceptuje i tvar před sečtením konstant, např. `4+3x-18=1x-6`
- podmínka v kroku 1 je pouze číslo
- generují se pouze celočíselné výsledky
