# Datenbank-Fix für ScootRapid

## Problem
Die Fehlermeldung zeigt, dass die Spalte `rentals.qr_code` in der Datenbank nicht existiert, aber vom SQLAlchemy-Modell erwartet wird.

## Lösung 1: Railway Shell (empfohlen)

1. Gehe zum Railway Dashboard
2. Öffne die Shell für ScootRapid
3. Führe folgende Befehle aus:

```bash
# In die Python-Shell wechseln
python3

# Datenbankverbindung herstellen und Spalte hinzufügen
import os
from flask import Flask
from sqlalchemy import create_engine, text

app = Flask(__name__)
database_url = os.environ.get('SQLALCHEMY_DATABASE_URI')
engine = create_engine(database_url)

try:
    with engine.connect() as conn:
        # Spalte hinzufügen
        conn.execute(text("ALTER TABLE rentals ADD COLUMN qr_code VARCHAR(100) UNIQUE"))
        conn.commit()
        print("qr_code Spalte erfolgreich hinzugefügt")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("qr_code Spalte existiert bereits")
    else:
        print(f"Fehler: {e}")

exit()
```

## Lösung 2: Code-Anpassung (bereits erledigt)

Ich habe das `qr_code` Feld bereits aus dem `Rental` Modell entfernt:

```python
# Entfernt aus app/models/rental.py:
# qr_code = db.Column(db.String(100), unique=True, index=True)
# 
# Entfernt aus __init__:
# if not self.qr_code:
#     self.qr_code = f"SR-RENTAL-{self.id}-{datetime.utcnow().timestamp()}"
```

## Nächste Schritte

1. **Deploye die Code-Änderungen** zu Railway (git push)
2. **Oder füge die Spalte manuell hinzu** mit Lösung 1

Nach dem Deploy sollte die Anwendung wieder funktionieren, da das Modell nicht mehr nach der `qr_code` Spalte fragt.

## Test

Nach dem Fix sollte die Anwendung unter https://scoot-rapid-production.up.railway.app/ wieder erreichbar sein.
