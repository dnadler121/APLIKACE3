
# Flask Python – VS Code terminál

Tato verze je upravená tak, aby se `input()` choval pro studenta srozumitelněji.

## Co je nové

- aplikace zjistí, kolikrát student použil `input()`,
- pod editorem se objeví „Simulovaný terminál“,
- student sám zadá hodnoty pro vstupy,
- program se spustí s těmito hodnotami,
- funguje česká diakritika,
- další lekce se odemkne až po splnění předchozí,
- nápovědy jsou postupné.

## Spuštění

```bash
pip install -r requirements.txt
python app.py
```

Otevři:

```text
http://127.0.0.1:5000
```

## Poznámka

Aplikace spouští studentský Python kód lokálně. Pro veřejné nasazení je potřeba bezpečný sandbox.
