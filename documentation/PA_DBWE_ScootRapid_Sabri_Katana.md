# Praxisarbeit DBWE.TA1A.PA

## Datenbanken und Webentwicklung

### ScootRapid – E-Scooter Vermietungsplattform

---

**Autor:**  
Sabri Katana  
Schlossstrasse 123, 3008 Bern  
sabri.katana@student.ipso.ch

**Klasse:** HFINFP.A.BA.5.25-BE-S2504

**Hochschule:** IPSO – Höhere Fachschule der digitalen Wirtschaft

**Abgabedatum:** 20. März 2026

---

## Inhaltsverzeichnis

1. Management Summary
2. Anwendung
   - 2.1 Anforderungen
   - 2.2 Funktionalität und Bedienung
   - 2.3 API-Dokumentation
3. Architektur
   - 3.1 Datenmodell
   - 3.2 Systemarchitektur
   - 3.3 Anwendungsabläufe
   - 3.4 Bereitstellung
4. Testprotokoll
5. Reflexion
6. Quellenverzeichnis
7. Anhang

---

## 1 Management Summary

Die vorliegende Praxisarbeit dokumentiert die Entwicklung von **ScootRapid**, einer webbasierten E-Scooter-Vermietungsplattform. Das System wurde im Rahmen des Moduls «Datenbanken und Webentwicklung» (DBWE) an der IPSO entwickelt.

### Ausgangslage

Eine fiktive Stadtverwaltung plant die Verbesserung der urbanen Mobilität durch E-Scooter-Sharing. ScootRapid ermöglicht Privatpersonen und Verleihfirmen die Registrierung von E-Scootern. Nutzer können diese über eine Weboberfläche ausleihen und bezahlen.

### Technologie und Infrastruktur

- **Backend:** Python 3.11 mit Flask 2.3.3
- **Datenbank:** MySQL auf Railway Cloud
- **Webserver:** Gunicorn WSGI Server
- **Hosting:** Railway Cloud (PaaS)
- **URL:** https://scoot-rapid-production.up.railway.app/

### Erreichte Ergebnisse

Alle funktionalen Anforderungen der Normaufgabe wurden implementiert:
- Benutzerregistrierung mit drei Rollen (Kunde, Anbieter, Admin)
- Scooter-Verwaltung mit GPS-Koordinaten und QR-Codes
- Ausleihe und Rückgabe mit minutengenauer Abrechnung
- RESTful API mit JWT-Authentifizierung

### Mehrwert und Risiken

**Mehrwert:** Automatisierte Kostenberechnung, QR-Code-Integration, intuitive Benutzeroberfläche, hohe Verfügbarkeit durch Cloud-Hosting.

**Risiken:** Abhängigkeit von Railway Cloud, Free-Tier-Limitierungen bei hoher Last.

**Empfehlung:** Für produktiven Einsatz Migration zu Enterprise-Cloud-Lösung.

---

## 2 Anwendung

### 2.1 Anforderungen

Die Anforderungen basieren auf der Normaufgabe und wurden vollständig umgesetzt.

#### Funktionale Anforderungen

| ID | Anforderung | Status |
|----|-------------|--------|
| FA-01 | Registrierung/Authentifizierung für Anbieter | ✓ Erfüllt |
| FA-02 | Registrierung/Authentifizierung für Fahrer | ✓ Erfüllt |
| FA-03 | Scooter hinzufügen, bearbeiten, entfernen | ✓ Erfüllt |
| FA-04 | Eindeutige Scooter-ID, Akku-Status, GPS | ✓ Erfüllt |
| FA-05 | QR-Code zum Ent-/Verriegeln | ✓ Erfüllt |
| FA-06 | Erfassung Start-/Endzeitpunkt | ✓ Erfüllt |
| FA-07 | Minutengenaue Abrechnung | ✓ Erfüllt |
| FA-08 | Zahlungsmittel und Transaktionen | ✓ Erfüllt |

#### Technische Anforderungen

| Anforderung | Umsetzung |
|-------------|-----------|
| Datenbanksystem | MySQL (Railway) |
| Programmiersprache | Python 3.11 |
| Web-Framework | Flask 2.3.3 |
| Webserver | Gunicorn |

### 2.2 Funktionalität und Bedienung

#### Benutzerrollen

**Kunde:** Scooter ausleihen/zurückgeben, Kosten einsehen, Zahlungen verwalten

**Anbieter:** Kundenrechte + eigene Scooter-Flotte verwalten, Einnahmen einsehen

**Administrator:** Alle Rechte + alle Benutzer/Scooter verwalten

#### Bedienungsanleitung

**Registrierung:**
1. https://scoot-rapid-production.up.railway.app/ aufrufen
2. «Registrieren» klicken
3. Formular ausfüllen (E-Mail, Passwort, Name, Rolle)
4. Registrierung abschliessen

**Scooter ausleihen:**
1. Anmelden
2. «Verfügbare Scooter» wählen
3. Scooter auswählen und Details prüfen
4. «Ausleihen» klicken
5. Standort-Freigabe bestätigen

**Scooter zurückgeben:**
1. Im Dashboard «Aktive Ausleihe» anzeigen
2. «Ausleihe beenden» klicken
3. Kosten werden automatisch berechnet

#### Zugangsdaten für Examinator

| Rolle | E-Mail | Passwort |
|-------|--------|----------|
| Admin | admin@scootrapid.com | Admin123! |
| Provider | provider@scootrapid.com | Provider123! |
| Kunde | kunde@scootrapid.com | Kunde123! |
### 2.3 API-Dokumentation

Die RESTful API ermöglicht programmgesteuerten Zugriff. Authentifizierung erfolgt via JWT.

**Basis-URL:** https://scoot-rapid-production.up.railway.app/api

#### Authentifizierung

**Login:**
```http
POST /api/auth/login
Content-Type: application/json

{"email": "admin@scootrapid.com", "password": "Admin123!"}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {"id": 1, "email": "admin@scootrapid.com", "role": "admin"}
}
```

**Token verwenden:**
```
Authorization: Bearer <access_token>
```

#### Scooter-Endpunkte

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | /api/scooters | Alle Scooter |
| GET | /api/scooters/available | Verfügbare Scooter |
| GET | /api/scooters/{id} | Scooter-Details |
| POST | /api/scooters | Neuer Scooter (Provider) |
| PUT | /api/scooters/{id} | Aktualisieren |
| DELETE | /api/scooters/{id} | Löschen |

#### Ausleihe-Endpunkte

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | /api/rentals | Eigene Ausleihen |
| POST | /api/rentals/start | Ausleihe starten |
| POST | /api/rentals/{id}/end | Ausleihe beenden |

**Beispiel - Ausleihe starten:**
```bash
curl -X POST "https://scoot-rapid-production.up.railway.app/api/rentals/start" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"scooter_id": 1, "latitude": 46.948, "longitude": 7.447}'
```

---

## 3 Architektur

### 3.1 Datenmodell

Das Datenmodell wurde nach den Prinzipien der 3. Normalform entworfen.

#### ERD-Diagramm

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │    scooters     │
├─────────────────┤       ├─────────────────┤
│ PK id           │       │ PK id           │
│    email (UQ)   │       │    identifier   │
│    password_hash│       │    qr_code (UQ) │
│    first_name   │       │    model        │
│    last_name    │       │    brand        │
│    role         │       │    latitude     │
│    created_at   │       │    longitude    │
└────────┬────────┘       │    status       │
         │                │    battery_level│
         │                │ FK provider_id  │
         │                └────────┬────────┘
         │                         │
         └──────────┬──────────────┘
                    │
         ┌──────────▼──────────┐
         │      rentals        │
         ├─────────────────────┤
         │ PK id               │
         │    rental_code      │
         │ FK user_id          │
         │ FK scooter_id       │
         │    start_time       │
         │    end_time         │
         │    start_lat/lon    │
         │    end_lat/lon      │
         │    duration_minutes │
         │    total_cost       │
         │    status           │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │     payments        │
         ├─────────────────────┤
         │ PK id               │
         │ FK rental_id        │
         │    amount           │
         │    method           │
         │    status           │
         │    transaction_id   │
         └─────────────────────┘
```

#### Tabellenbeschreibung

**users:** Benutzerinformationen mit Rollen (customer, provider, admin)

**scooters:** E-Scooter mit GPS, QR-Code, Status (available, in_use, maintenance)

**rentals:** Ausleihvorgänge mit Start-/Endzeit und Kostenberechnung

**payments:** Zahlungstransaktionen mit Status und Methode
### 3.2 Systemarchitektur

Die Anwendung folgt dem MVC-Pattern mit Service-Schicht.

#### Architektur-Diagramm

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│  ┌─────────────┐  ┌─────────────┐      │
│  │ Web Browser │  │ API Client  │      │
│  │ (Bootstrap) │  │ (Postman)   │      │
│  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────┘
                    │ HTTPS
                    ▼
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│  ┌─────────────────────────────────┐   │
│  │        Flask Application        │   │
│  │  ┌────────────┐ ┌────────────┐  │   │
│  │  │ Web Ctrl   │ │ API Ctrl   │  │   │
│  │  │ - auth     │ │ - auth_api │  │   │
│  │  │ - scooter  │ │ - scooter  │  │   │
│  │  │ - rental   │ │ - rental   │  │   │
│  │  └────────────┘ └────────────┘  │   │
│  │  ┌────────────────────────────┐ │   │
│  │  │     SERVICE LAYER          │ │   │
│  │  │ - RentalService            │ │   │
│  │  │ - PaymentService           │ │   │
│  │  │ - QRCodeService            │ │   │
│  │  └────────────────────────────┘ │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    │ SQLAlchemy
                    ▼
┌─────────────────────────────────────────┐
│            DATA LAYER                   │
│  ┌─────────────────────────────────┐   │
│  │     SQLAlchemy Models           │   │
│  │  User | Scooter | Rental        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │     MySQL Database              │   │
│  │     (Railway Cloud)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### Projektstruktur

```
scoot-rapid/
├── app/
│   ├── __init__.py          # App Factory
│   ├── models/              # DB-Modelle
│   ├── controllers/         # Web-Controller
│   ├── api/                 # REST-API
│   ├── templates/           # Jinja2
│   ├── static/              # CSS, JS
│   └── utils/               # Hilfsfunktionen
├── config.py
├── requirements.txt
└── wsgi.py
```

### 3.3 Anwendungsabläufe

#### Sequenzdiagramm: Ausleihe

```
Benutzer    Browser     Controller    Service      Database
    │          │            │            │            │
    │─Scooter──▶            │            │            │
    │ wählen   │            │            │            │
    │          │──GET───────▶            │            │
    │          │            │──query─────▶            │
    │          │            │            │──SELECT────▶
    │          │            │            │◀──data─────│
    │          │◀──HTML─────│            │            │
    │◀─Seite───│            │            │            │
    │          │            │            │            │
    │─Ausleihen▶            │            │            │
    │          │──POST──────▶            │            │
    │          │            │──start()───▶            │
    │          │            │            │──INSERT────▶
    │          │            │            │──UPDATE────▶
    │          │◀──redirect─│            │            │
    │◀─Dashboard│            │            │            │
```

#### Kostenberechnung

```
Formel: Gesamtkosten = Grundgebühr + (Minuten × Minutenpreis)

Beispiel (10 Minuten Fahrt):
- Grundgebühr: CHF 1.50
- Minutenpreis: CHF 0.30
- Berechnung: 1.50 + (10 × 0.30) = CHF 4.50
```

#### Zustandsdiagramm: Scooter-Status

```
        ┌──────────┐
        │ AVAILABLE│◀────────────┐
        └────┬─────┘             │
             │ Ausleihe          │ Rückgabe
             ▼                   │
        ┌──────────┐             │
        │  IN_USE  │─────────────┘
        └────┬─────┘
             │ Problem
             ▼
        ┌──────────┐
        │MAINTENANCE│
        └────┬─────┘
             │ Repariert
             ▼
        ┌──────────┐
        │ OFFLINE  │───▶ AVAILABLE
        └──────────┘
```
### 3.4 Bereitstellung der Komponenten

Die Anwendung wird auf **Railway Cloud Platform** betrieben.

#### Deployment-Diagramm

```
┌─────────────────────────────────────────┐
│              INTERNET                   │
│  ┌──────────┐      ┌──────────┐        │
│  │ Browser  │      │ API Client│        │
│  └────┬─────┘      └────┬─────┘        │
└───────┼─────────────────┼───────────────┘
        └────────┬────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────┐
│        RAILWAY CLOUD PLATFORM           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │         Web Service             │   │
│  │  ┌───────────┐ ┌─────────────┐  │   │
│  │  │ Gunicorn  │ │ Flask App   │  │   │
│  │  │ (4 Worker)│─▶│             │  │   │
│  │  └───────────┘ └─────────────┘  │   │
│  └─────────────────────────────────┘   │
│                 │                       │
│                 ▼ Internal Network      │
│  ┌─────────────────────────────────┐   │
│  │        MySQL Database           │   │
│  │  Host: mysql.railway.internal   │   │
│  │  Tables: users, scooters,       │   │
│  │          rentals, payments      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Environment Variables:                 │
│  - FLASK_ENV=production                │
│  - SECRET_KEY=***                      │
│  - SQLALCHEMY_DATABASE_URI=mysql://... │
│  - BASE_PRICE_PER_MINUTE=0.30         │
│  - START_FEE=1.50                      │
└─────────────────────────────────────────┘

URL: https://scoot-rapid-production.up.railway.app/
GitHub: https://github.com/eazybusiness/scoot-rapid
```

#### Technologiebegründung

| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| Hosting | Railway | Git-Deployment, Free Tier, Managed DB |
| Webserver | Gunicorn | Produktionsreif, Multi-Worker |
| Datenbank | MySQL | Gemäss Aufgabenstellung |
| Framework | Flask | Leichtgewichtig, aus Unterricht |
| ORM | SQLAlchemy | Sicherheit, Abstraktion |
| Auth | JWT | API-kompatibel, stateless |

#### Abweichungen vom Unterricht

| Abweichung | Begründung |
|------------|------------|
| Railway Cloud | Internet-Verfügbarkeit erforderlich |
| JWT statt Session | API-Kompatibilität |
| Bootstrap 5 | Professionelles UI |
| qrcode-Bibliothek | Normaufgabe: QR-Code |

---

## 4 Testprotokoll

### Testfall-Übersicht

| Nr | Testfall | Erwartet | Tatsächlich | Status |
|----|----------|----------|-------------|--------|
| T01 | Benutzerregistrierung | Konto erstellt | Konto erstellt, Login OK | ✓ Pass |
| T02 | Falscher Login | Fehlermeldung | "Ungültige Daten" | ✓ Pass |
| T03 | Scooter erstellen | In DB mit QR | Scooter + QR-Code | ✓ Pass |
| T04 | Scooter ausleihen | Status 'in_use' | Rental erstellt | ✓ Pass |
| T05 | Ausleihe beenden | Kosten berechnet | CHF 4.50 (10 Min) | ✓ Pass |
| T06 | Doppelte Ausleihe | Fehlermeldung | "Bereits ausgeliehen" | ✓ Pass |
| T07 | API-Login | JWT Token | access_token OK | ✓ Pass |
| T08 | API ohne Token | 401 Error | "Missing Auth" | ✓ Pass |
| T09 | Scooter-Liste API | JSON Array | Scooter-Objekte | ✓ Pass |
| T10 | Ungültiger Scooter | Fehlermeldung | "Nicht verfügbar" | ✓ Pass |

### Detaillierte Tests

#### T04: Scooter ausleihen

**Vorbedingung:** Eingeloggt als Kunde, Scooter verfügbar

**Durchführung:**
1. Verfügbare Scooter anzeigen
2. Scooter SR-001 auswählen
3. «Ausleihen» klicken

**Erwartet:** Rental erstellt, Status = 'in_use'

**Tatsächlich:** ✓ Erfüllt

#### T07: API-Login

**Durchführung:**
```bash
curl -X POST "https://scoot-rapid-production.up.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@scootrapid.com","password":"Admin123!"}'
```

**Erwartet:** JSON mit access_token

**Tatsächlich:** ✓ Token erhalten
## 5 Reflexion

### 5.1 Erreichte Ziele

Die Praxisarbeit hat alle Ziele erreicht:

- **Lauffähige Anwendung:** ScootRapid unter https://scoot-rapid-production.up.railway.app/ erreichbar
- **Funktionale Anforderungen:** Alle Normaufgabe-Anforderungen implementiert
- **RESTful API:** JWT-authentifizierte API, testbar mit curl/Postman
- **Dokumentation:** Architektur mit Diagrammen, Abweichungen begründet

### 5.2 Herausforderungen

**Cloud-Deployment:** Railway erforderte Anpassungen für Umgebungsvariablen. Lösung: python-dotenv und flexible Config-Klasse.

**JWT-Authentifizierung:** Token-Handling für API. Lösung: Flask-JWT-Extended.

**QR-Code-Generierung:** Lösung mit qrcode-Bibliothek, Base64-Einbettung.

### 5.3 Lerngewinn

- Full-Stack-Entwicklung (Frontend, Backend, Datenbank)
- RESTful API-Design mit Token-Authentifizierung
- Cloud-Deployment und Konfigurationsmanagement
- Selbständige Projektplanung und -umsetzung

### 5.4 Ausblick

Für produktive Nutzung:
- Mobile App mit QR-Scanner
- Echte Payment-Integration (Stripe)
- WebSocket für Echtzeittracking
- Load Balancer und DB-Replikation

---

## 6 Quellenverzeichnis

Flask Documentation. (2024). *Flask User's Guide*. https://flask.palletsprojects.com/

SQLAlchemy Documentation. (2024). *SQLAlchemy ORM Tutorial*. https://docs.sqlalchemy.org/

Railway Documentation. (2024). *Railway Deployment Guide*. https://docs.railway.app/

Bootstrap. (2024). *Bootstrap 5 Documentation*. https://getbootstrap.com/docs/

JWT.io. (2024). *Introduction to JSON Web Tokens*. https://jwt.io/introduction/

IPSO Bildung. (2024). *Leitfaden für schriftliche Arbeiten*. Version 2.0.

---

## 7 Anhang

### A. Zugangsdaten

**URL:** https://scoot-rapid-production.up.railway.app/

**GitHub:** https://github.com/eazybusiness/scoot-rapid

| Rolle | E-Mail | Passwort |
|-------|--------|----------|
| Admin | admin@scootrapid.com | Admin123! |
| Provider | provider@scootrapid.com | Provider123! |
| Customer | kunde@scootrapid.com | Kunde123! |

### B. API-Testbefehle

```bash
# Login
curl -X POST "https://scoot-rapid-production.up.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@scootrapid.com","password":"Admin123!"}'

# Scooter auflisten
curl -X GET "https://scoot-rapid-production.up.railway.app/api/scooters" \
  -H "Authorization: Bearer <TOKEN>"

# Verfügbare Scooter
curl -X GET "https://scoot-rapid-production.up.railway.app/api/scooters/available" \
  -H "Authorization: Bearer <TOKEN>"
```

### C. Technologie-Stack

| Kategorie | Technologie | Version |
|-----------|-------------|---------|
| Sprache | Python | 3.11 |
| Framework | Flask | 2.3.3 |
| ORM | SQLAlchemy | 2.0.19 |
| Datenbank | MySQL | 8.0 |
| Webserver | Gunicorn | 21.2.0 |
| Auth | Flask-JWT-Extended | 4.5.2 |
| Frontend | Bootstrap | 5.3 |
| Hosting | Railway | - |

---

**Ende der Dokumentation**

*Sabri Katana, März 2026*
