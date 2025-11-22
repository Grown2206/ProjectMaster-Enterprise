# 🏢 Project Master Enterprise v2.0

Eine umfassende Enterprise-Projektmanagement-Suite mit modernster Architektur, Security und Features.

## ✨ Hauptfeatures

### 📊 Projektmanagement
- **Kanban Board** - Visualisiere Aufgaben in To Do, In Progress, Done
- **Multi-Projekt Dashboard** - Übersicht über alle Projekte
- **Timeline & Gantt Charts** - Zeitliche Planung visualisieren
- **Templates** - Projekte aus Vorlagen erstellen
- **Tagging-System** - Projekte kategorisieren und filtern
- **Archivierung** - Abgeschlossene Projekte archivieren

### 👥 Team & Collaboration
- **Team-Management** - Teammitglieder hinzufügen und Rollen zuweisen
- **Aufgabenzuweisung** - Tasks bestimmten Personen zuweisen
- **Kommentare** - Diskussionen direkt an Tasks
- **Activity Log** - Vollständige Audit-Trail aller Änderungen
- **Stakeholder Register** - Wichtige Stakeholder tracken

### 💰 Budget & Finanzen
- **Budget-Planung** - Gesamtbudget festlegen
- **Ausgaben-Tracking** - Alle Ausgaben kategorisiert erfassen
- **Visuelle Auswertung** - Pie-Charts und Reports
- **Budget-Alarm** - Warnung bei Budgetüberschreitung

### 🎯 Strategie & Planung
- **SWOT-Analyse** - Stärken, Schwächen, Chancen, Risiken
- **OKR-Management** - Objectives & Key Results setzen und tracken
- **Retrospektiven** - Start-Stop-Continue Feedback sammeln
- **Risiko-Matrix** - Risiken bewerten und visualisieren

### 🧪 Quality Assurance
- **Test Cases** - Testfälle definieren und verwalten
- **Test Execution** - Tests durchführen und Status dokumentieren
- **Bug Tracker** - Bugs erfassen, priorisieren und fixen
- **Pass Rate** - Automatische Berechnung der Erfolgsquote

### 🧪 Labor & Experimente (NEU)
- **Versuchsdokumentation** - Wissenschaftliche Versuche dokumentieren
- **Matrix-Editor** - Flexible Tabellen für Messwerte
- **Fotodokumentation** - Bilder hochladen und beschriften
- **PDF-Prüfberichte** - Professionelle Reports generieren
- **Vorlagen** - Schnelle Versuchsstrukturen laden

### 📚 Knowledge Management
- **Projekt-Wiki** - Dokumentation und Onboarding-Guides
- **Ideen-Backlog** - Feature-Ideen sammeln
- **Decision Log** - Architektur-Entscheidungen dokumentieren
- **Meeting-Protokolle** - Besprechungen nachvollziehbar machen
- **Dokument-Upload** - PDFs, Excel, Word hochladen

### 🔒 Security & Enterprise Features
- **Benutzer-Authentifizierung** - Sicheres Login-System mit bcrypt
- **Rollen-Management** - Admin, Manager, User, Viewer
- **Secret Safe** - API-Keys und Passwörter sicher speichern
- **Session Management** - Account-Lockout nach Failed-Attempts
- **Audit Logging** - Vollständige Nachvollziehbarkeit
- **Backup-System** - Automatische Datensicherung

### 📊 Analytics & Reports
- **Burn-Down Charts** - Sprint-Fortschritt visualisieren
- **Health Dashboard** - Projekt-Gesundheit bewerten
- **Global View** - Portfolio-Übersicht
- **Activity Feed** - Live-Ticker über alle Projekte
- **PDF Export** - Projektberichte generieren

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Setup

1. **Repository klonen**
```bash
git clone <repository-url>
cd ProjectMaster-Enterprise
```

2. **Virtuelle Umgebung erstellen**
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
source venv/bin/activate
```

3. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env
# Bearbeite .env und passe Werte an
```

5. **Anwendung starten**
```bash
streamlit run project_app.py
```

6. **Im Browser öffnen**
```
http://localhost:8501
```

## 🔐 Standard-Login

**Username:** admin
**Passwort:** 123

⚠️ **WICHTIG:** Passwort nach erstem Login ändern!

## 📁 Projektstruktur

```
ProjectMaster-Enterprise/
├── project_app.py              # Haupt-Streamlit-App
├── config.py                   # Zentrale Konfiguration
├── logger.py                   # Logging-System
├── security.py                 # Security & Hashing
├── validators.py               # Input-Validierung
│
├── data_manager_v2.py          # Verbesserter Data Manager
├── user_manager.py             # User Management
├── auth_manager.py             # Authentifizierung
│
├── kanban_board.py             # Kanban Board UI
├── ui_components.py            # UI Helper Components
├── extended_features.py        # Extended Features
├── strategy_tools.py           # Strategie-Tools
├── knowledge_base.py           # Wiki & Knowledge Base
├── qa_module.py                # QA & Testing
├── experiment_module.py        # Labor & Experimente
├── calendar_module.py          # Kalender-Ansicht
├── global_dashboard.py         # Global Portfolio View
│
├── pdf_export.py               # PDF-Report-Generator
├── ai_assistant.py             # AI-Mock-Assistent
├── utils.py                    # Utility-Funktionen
│
├── requirements.txt            # Python-Dependencies
├── .env.example                # Environment-Template
├── .gitignore                  # Git-Ignore-Regeln
└── README.md                   # Diese Datei
```

## ⚙️ Konfiguration

### Umgebungsvariablen (.env)

```env
# Anwendung
APP_NAME=ProjectMaster Enterprise
APP_VERSION=2.0.0
APP_ENV=development  # oder production

# Security
SECRET_KEY=your-secret-key-change-this
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5

# Datenbank
DATABASE_TYPE=json  # oder sqlite
DATABASE_PATH=./data/

# File Storage
MAX_UPLOAD_SIZE_MB=10

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/app.log

# Features
ENABLE_BACKUP=true
BACKUP_INTERVAL_HOURS=24
```

## 🛠️ Entwicklung

### Code-Qualität

```bash
# Code formatieren
black .

# Linting
flake8 .

# Type checking
mypy .
```

### Tests ausführen

```bash
pytest
pytest --cov=. --cov-report=html
```

## 🔧 Technologie-Stack

- **Frontend:** Streamlit 1.28+
- **Datenvisualisierung:** Plotly, Pandas
- **Security:** bcrypt, cryptography
- **PDF-Generierung:** fpdf, reportlab
- **Logging:** Python logging, loguru (optional)
- **Datenbank:** JSON (Standard), SQLite (Optional)

## 📋 Roadmap & Geplante Features

- [ ] PostgreSQL/MySQL Support
- [ ] REST API mit FastAPI
- [ ] Email-Benachrichtigungen
- [ ] Echtzeit-Collaboration (WebSockets)
- [ ] Mobile App
- [ ] CI/CD Integration (GitHub Actions, GitLab CI)
- [ ] Integration mit Jira, Trello, Slack
- [ ] AI-gestützte Risiko-Analyse
- [ ] Zeiterfassung & Timesheet
- [ ] Gantt-Chart Editor (interaktiv)

## 🐛 Known Issues & Workarounds

- PDF-Export benötigt vollständige Projektdaten
- Große Bild-Uploads (>10MB) können Performance beeinträchtigen
- Datenbankwechsel erfordert Migration (Tool in Entwicklung)

## 🤝 Contributing

Contributions sind willkommen! Bitte folge diesen Schritten:

1. Fork das Projekt
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Code-Stil
- Folge PEP 8
- Docstrings für alle Funktionen
- Type Hints verwenden
- Tests für neue Features

## 📝 Changelog

### Version 2.0.0 (2025-11-22)
- ✨ Komplette Code-Überarbeitung mit verbesserter Architektur
- 🔒 Security-Verbesserungen (Passwort-Hashing, Input-Validierung)
- 📊 Neues Labor & Experimente Modul
- 🧪 Erweiterte QA-Features
- 📝 Logging & Audit-Trail
- 🗄️ Backup-System
- 🐛 Zahlreiche Bugfixes
- 📚 Verbesserte Dokumentation

### Version 1.0.0
- Initial Release

## 📄 Lizenz

Dieses Projekt ist proprietär. Alle Rechte vorbehalten.

## 👤 Autor

**Project Master Enterprise Team**

## 💬 Support

Bei Fragen oder Problemen:
- GitHub Issues: [Repository Issues](https://github.com/yourrepo/issues)
- Email: support@projectmaster.com
- Dokumentation: [Wiki](https://github.com/yourrepo/wiki)

## 🌟 Acknowledgments

- Streamlit-Community für das großartige Framework
- Alle Contributors und Tester

---

**Made with ❤️ for modern project management**
