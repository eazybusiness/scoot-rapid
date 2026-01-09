# Contributing to ScootRapid

Vielen Dank für Ihr Interesse an ScootRapid! Dieses Dokument hilft Ihnen dabei, zum Projekt beizutragen.

## 🚀 Quick Start

### Voraussetzungen
- Python 3.11+
- MySQL 8.0+
- Git
- Docker (optional)

### Lokale Entwicklung einrichten

1. **Repository klonen**
```bash
git clone https://github.com/eazybusiness/scoot-rapid.git
cd scoot-rapid
```

2. **Virtuelle Umgebung erstellen**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# oder venv\Scripts\activate  # Windows
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Datenbank einrichten**
```bash
# Test-Datenbank erstellen
mysql -u root -p -e "CREATE DATABASE scoot_rapid_test;"
```

5. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env
# .env Datei bearbeiten
```

6. **Datenbank initialisieren**
```bash
flask db upgrade
flask seed-db  # Testdaten erstellen
```

7. **Entwicklungsserver starten**
```bash
python wsgi.py
```

## 📋 Development Workflow

### 1. Branch erstellen
```bash
git checkout -b feature/ihre-feature-name
# oder
git checkout -b fix/bug-beschreibung
```

### 2. Änderungen entwickeln
- Code schreiben
- Tests hinzufügen
- Dokumentation aktualisieren

### 3. Code Quality prüfen
```bash
# Code formatieren
black app/ api/ tests/

# Linting
flake8 app/ api/ tests/

# Type checking
mypy app/

# Security check
bandit -r app/
```

### 4. Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=app --cov=api --cov-report=html

# Spezifische Tests
pytest tests/test_models.py -v
```

### 5. Commit erstellen
```bash
git add .
git commit -m "feat: Add scooter rating system"
```

### 6. Push und Pull Request
```bash
git push origin feature/ihre-feature-name
# Pull Request auf GitHub erstellen
```

## 🏗️ Projektstruktur

```
scoot-rapid/
├── app/                    # Hauptanwendung
│   ├── models/            # Datenbank-Models
│   ├── controllers/       # Route-Handler
│   ├── templates/         # HTML-Templates
│   ├── static/           # CSS/JS/Assets
│   └── utils/            # Hilfsfunktionen
├── api/                   # REST API
├── tests/                 # Tests
├── migrations/            # Datenbank-Migrationen
├── docs/                  # Dokumentation
└── scripts/               # Hilfsskripte
```

## 🧪 Testing Guidelines

### Test-Typen

1. **Unit Tests**: Testen einzelne Funktionen/Klassen
2. **Integration Tests**: Testen Service-Interaktionen
3. **API Tests**: Testen REST-Endpunkte
4. **UI Tests**: Testen Web-Interface

### Test-Schreiben

```python
# tests/test_models.py
import pytest
from app.models.scooter import Scooter

def test_scooter_creation():
    """Test creating a new scooter"""
    scooter = Scooter(
        identifier="SC001",
        model="Xiaomi Mi Electric Scooter",
        brand="Xiaomi"
    )
    assert scooter.identifier == "SC001"
    assert scooter.status == "available"

def test_scooter_availability():
    """Test scooter availability check"""
    scooter = Scooter(status="available")
    assert scooter.is_available()
    
    scooter.status = "in_use"
    assert not scooter.is_available()
```

### Test-Datenbank

```python
# tests/conftest.py
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Test user erstellen und einloggen
    client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'test123456',
        'first_name': 'Test',
        'last_name': 'User'
    })
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'test123456'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}
```

## 📝 Code Style

### Python Code Style

Wir verwenden folgende Tools und Standards:

- **Black**: Code-Formatierung
- **flake8**: Linting
- **isort**: Import-Sortierung
- **mypy**: Type Checking

### Beispiel

```python
# ✅ Guter Stil
from typing import List, Optional
from flask import Blueprint, jsonify, request
from app.models.scooter import Scooter
from app.utils.decorators import require_auth

scooters_bp = Blueprint('scooters', __name__)

@scooters_bp.route('/api/scooters', methods=['GET'])
@require_auth
def get_scooters() -> List[dict]:
    """Get all available scooters."""
    status = request.args.get('status', 'available')
    scooters = Scooter.query.filter_by(status=status).all()
    return jsonify([scooter.to_dict() for scooter in scooters])

# ❌ Schlechter Stil
def getScooters():
    scooters=Scooter.query.all()
    return jsonify([s.to_dict() for s in scooters])
```

### JavaScript Code Style

```javascript
// ✅ Guter Stil
const updateScooterStatus = async (scooterId, status) => {
  try {
    const response = await fetch(`/api/scooters/${scooterId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ status })
    });
    
    if (!response.ok) {
      throw new Error('Failed to update scooter status');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating scooter:', error);
    throw error;
  }
};

// ❌ Schlechter Stil
function updateScooter(scooterId, status){
  fetch('/api/scooters/'+scooterId,{
    method:'PUT',
    body:JSON.stringify({status:status})
  }).then(response=>response.json())
}
```

## 🐛 Bug Reports

### Bug Report erstellen

1. **Suchen** Sie nach existing Issues
2. **Erstellen** Sie neues Issue mit:
   - Klarem Titel
   - Detaillierter Beschreibung
   - Schritten zur Reproduktion
   - Erwartetem vs. tatsächlichen Verhalten
   - Environment-Informationen

### Bug Report Template

```markdown
## Bug Description
Kurze Beschreibung des Bugs

## Steps to Reproduce
1. Gehe zu...
2. Klicke auf...
3. Fülle aus...
4. Siehe Fehler

## Expected Behavior
Beschreiben, was passieren sollte

## Actual Behavior
Beschreiben, was tatsächlich passiert

## Environment
- OS: [z.B. Ubuntu 20.04]
- Python: [z.B. 3.11.0]
- Browser: [z.B. Chrome 120]
- Version: [z.B. v2.1.0]

## Additional Context
Zusätzliche Informationen, Logs, Screenshots
```

## ✨ Feature Requests

### Feature Request erstellen

1. **Diskutieren** Sie die Idee im Discussions Tab
2. **Erstellen** Sie Issue mit:
   - Use Case Beschreibung
   - Akzeptanzkriterien
   - Design-Überlegungen

### Feature Request Template

```markdown
## Feature Description
Klare Beschreibung des gewünschten Features

## Problem Statement
Welches Problem wird gelöst?

## Proposed Solution
Vorgeschlagene Implementierung

## Acceptance Criteria
- [ ] Benutzer kann X tun
- [ ] System zeigt Y an
- [ ] Performance-Ziel erreicht

## Design Considerations
UI/UX, API, Database, etc.

## Additional Notes
Ressourcen, Dependencies, Timeline
```

## 🔄 Pull Request Guidelines

### PR Checklist

- [ ] Code folgt Style Guidelines
- [ ] Tests enthalten (>80% Coverage)
- [ ] Dokumentation aktualisiert
- [ ] CHANGELOG.md aktualisiert
- [ ] Alle Tests bestehen
- [ ] Manuelles Testing durchgeführt

### PR Template

```markdown
## Description
Kurze Beschreibung der Änderungen

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests geschrieben/aktualisiert
- [ ] Integration tests durchgeführt
- [ ] Manual testing bestanden

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 📚 Documentation

### Dokumentations-Typen

1. **API-Dokumentation**: OpenAPI/Swagger Specs
2. **User-Dokumentation**: Bedienungsanleitungen
3. **Developer-Dokumentation**: Architektur, Setup
4. **Code-Dokumentation**: Docstrings, Comments

### Docstring Guidelines

```python
def calculate_rental_cost(start_time, end_time, base_fee=1.50, price_per_minute=0.30):
    """
    Calculate the total cost of a rental.
    
    Args:
        start_time (datetime): When the rental started
        end_time (datetime): When the rental ended
        base_fee (float): Base rental fee in EUR
        price_per_minute (float): Price per minute in EUR
    
    Returns:
        float: Total rental cost in EUR
        
    Raises:
        ValueError: If end_time is before start_time
        
    Example:
        >>> from datetime import datetime, timedelta
        >>> start = datetime(2024, 1, 15, 10, 0)
        >>> end = datetime(2024, 1, 15, 10, 30)
        >>> calculate_rental_cost(start, end)
        10.5
    """
    if end_time < start_time:
        raise ValueError("End time must be after start time")
    
    duration_minutes = (end_time - start_time).total_seconds() / 60
    return base_fee + (duration_minutes * price_per_minute)
```

## 🚀 Deployment

### Development Deployment

```bash
# Lokal testen
python wsgi.py

# Mit Docker
docker-compose up -d
```

### Production Deployment

```bash
# Railway Deployment
git push origin main

# Manual Deployment
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Environment Variablen

```bash
# Development
export FLASK_ENV=development
export DATABASE_URL=mysql+pymysql://localhost/scoot_rapid_dev

# Production
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://user:pass@host/scoot_rapid
export SECRET_KEY=your-production-secret-key
```

## 🤝 Community Guidelines

### Verhaltensregeln

1. **Respektvoll** und professionell kommunizieren
2. **Konstruktive** Kritik anbieten
3. **Inklusiv** und offen sein
4. **Hilfsbereit** bei Fragen und Problemen

### Kommunikation

- **GitHub Issues**: Für Bugs und Features
- **Discussions**: Für allgemeine Fragen
- **Pull Requests**: Für Code-Reviews
- **Email**: Für private Anliegen

## 🏆 Recognition

### Contributor Types

1. **Code Contributors**: Pull Requests
2. **Documentation Writers**: Docs und Tutorials
3. **Bug Reporters**: Issue Reports
4. **Community Helpers**: Fragen beantworten

### Recognition

- Contributors in README.md erwähnen
- Release Notes mit Credits
- Annual Contributor Awards

## 📞 Hilfe bekommen

### Wo Hilfe finden

1. **Documentation**: README.md und docs/
2. **GitHub Issues**: Existing durchsuchen
3. **Discussions**: Fragen stellen
4. **Email**: maintainer@scoot-rapid.com

### Häufige Fragen

**Q: Wie füge ich einen neuen API-Endpunkt hinzu?**
A: Siehe "API Development" Guide in docs/

**Q: Wie schreibe ich Tests?**
A: Siehe "Testing Guidelines" oben

**Q: Wie deploye ich Änderungen?**
A: Siehe "Deployment" Sektion

---

## 📄 Lizenz

Durch Beiträge zu ScootRapid stimmen Sie zu, dass Ihre Beiträge unter derselben Lizenz wie das Projekt veröffentlicht werden.

---

**Vielen Dank für Ihr Beitrag!** 🎉
