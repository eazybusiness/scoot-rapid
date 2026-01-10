# ScootRapid Dokumentation

Professionelle Dokumentation mit Diagrammen und DOCX-Export.

## 📁 Ordnerstruktur

```
documentation/
├── scripts/                    # Python Skripte
│   ├── generate_diagrams.py   # Diagramm-Generator
│   ├── html_to_docx.py        # HTML zu DOCX Konverter
│   └── generate_docs.py       # Master-Generator
├── diagrams/                  # Generierte Diagramme
│   ├── scootrapid_architecture.png
│   ├── scootrapid_database_schema.png
│   ├── scootrapid_api_flow.png
│   ├── scootrapid_performance.png
│   └── scootrapid_deployment.png
├── generated/                 # Finale Dokumente
│   └── ScootRapid_Dokumentation.docx
└── requirements.txt           # Python Abhängigkeiten
```

## 🚀 Schnellstart

### 1. Abhängigkeiten installieren
```bash
cd documentation/scripts
pip install -r requirements.txt
```

### 2. Komplette Dokumentation generieren
```bash
python generate_docs.py
```

### 3. Einzelschritte
```bash
# Nur Diagramme generieren
python generate_diagrams.py

# Nur DOCX konvertieren
python html_to_docx.py
```

## 🎨 Diagramme

### Verfügbare Diagramme:
- **Architecture**: System-Architektur mit Komponenten
- **Database Schema**: ER-Diagramm der Datenbank
- **API Flow**: API-Flussdiagramm
- **Performance**: Performance-Metriken Dashboard
- **Deployment**: Deployment-Architektur

### Diagramm-Generator:
```python
from generate_diagrams import ScootRapidDiagramGenerator

generator = ScootRapidDiagramGenerator()
generator.generate_all_diagrams()
```

## 📄 DOCX-Export

### Features:
- ✅ Professionelle Formatierung
- ✅ Unternehmens-Branding (ScootRapid Colors)
- ✅ Automatische Diagramm-Einbindung
- ✅ API-Dokumentation mit Code-Blöcken
- ✅ Tabellen und Listen
- ✅ Test-Ergebnisse und Compliance

### Konverter:
```python
from html_to_docx import HTMLToDocxConverter

converter = HTMLToDocxConverter()
converter.parse_html_file("../DOKUMENTATION.html")
converter.add_diagrams_section("../diagrams")
converter.save_document("ScootRapid_Dokumentation.docx")
```

## 📊 Generierte Dateien

Nach Ausführung von `generate_docs.py`:

```
generated/
└── ScootRapid_Dokumentation.docx    # Professionelle Word-Dokumentation

diagrams/
├── scootrapid_architecture.png      # System-Architektur
├── scootrapid_database_schema.png   # Datenbank-Schema
├── scootrapid_api_flow.png          # API-Fluss
├── scootrapid_performance.png       # Performance-Dashboard
└── scootrapid_deployment.png        # Deployment-Architektur
```

## 🎯 Verwendungszweck

### **Für die Systemabgabe:**
- Professionelle Word-Dokumentation
- Hochauflösende Diagramme (300 DPI)
- Vollständige API-Dokumentation
- Test-Ergebnisse und Nachweise

### **Für Kunden:**
- Technische Dokumentation
- System-Architektur
- API-Integration Guide
- Performance-Analysen

### **Für Entwickler:**
- Datenbank-Schema
- API-Referenz
- Deployment-Guide
- Code-Beispiele

## 🔧 Technologie-Stack

### **Diagramm-Generierung:**
- **matplotlib**: Professionelle Plots
- **plotly**: Interaktive Diagramme
- **pandas**: Datenverarbeitung
- **kaleido**: Bild-Export

### **DOCX-Konvertierung:**
- **python-docx**: Word-Dokumentation
- **beautifulsoup4**: HTML-Parsing
- **PIL**: Bildverarbeitung

### **Design:**
- **Farbschema**: ScootRapid Corporate Design
- **Schriftarten**: Arial, Consolas
- **Auflösung**: 300 DPI für Druckqualität

## 📝 Anpassung

### **Farben anpassen:**
```python
self.colors = {
    'primary': '#1a237e',    # ScootRapid Blau
    'secondary': '#3949ab',  # Sekundär
    'success': '#4caf50',    # Erfolg
    'warning': '#ff9800',    # Warnung
    'error': '#f44336',      # Fehler
}
```

### **Neue Diagramme hinzufügen:**
```python
def create_custom_diagram(self):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    # Diagramm-Code hier
    plt.savefig(f"{self.output_dir}/custom_diagram.png", dpi=300)
```

## 🚨 Fehlerbehebung

### **Häufige Probleme:**

1. **Module nicht gefunden:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Bilder nicht generiert:**
   ```bash
   # Überprüfe kaleido Installation
   pip install kaleido
   ```

3. **DOCX leer:**
   ```bash
   # Überprüfe HTML-Datei-Pfad
   ls -la ../DOKUMENTATION.html
   ```

### **Debug-Modus:**
```bash
# Mit Debug-Ausgaben
python -v generate_docs.py
```

## 📞 Support

Bei Problemen mit der Dokumentation:
- 📧 **Email**: np@hiplus.de
- 🌐 **Profil**: https://me.hiplus.de
- 📱 **vCard**: Nils_Peters.vcf

---

**ScootRapid - Lean E-Scooter Rental Platform**  
*Professionelle Dokumentation für Systemabgabe und Kunden*
