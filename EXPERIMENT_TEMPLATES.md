# 🧬 Experiment Templates - Feature Documentation

## Übersicht

Die neue **Experiment Templates** Feature ermöglicht es Benutzern, vorgefertigte Versuchsvorlagen zu verwenden, um schnell und einfach neue Experimente zu erstellen - ähnlich wie bei den Projekt-Templates.

## Was ist neu?

### 1. Experiment Templates Library
- **8 vorkonfigurierte Vorlagen** für verschiedene Test- und Versuchstypen
- Schneller Zugriff über Sidebar → "🧬 Versuchs-Templates"
- Detaillierte Vorschau jeder Vorlage vor der Erstellung

### 2. Vorgefertigte Vorlagen

#### 🧪 Chemical Resistance Test
- Chemische Beständigkeitsprüfung
- 8 Materialproben (V2A, V4A, Aluminium, Kunststoff)
- 6 Prüfkriterien (Wochen 1-4, Gesamtbewertung, Anmerkungen)

#### ⚙️ Mechanical Durability Test
- Mechanische Dauerprüfung von Bauteilen
- 6 Prüflinge (Serie A, B, Referenzen)
- 7 Prüfkriterien (Zyklen, Kraft, Verformung, etc.)

#### 🌡️ Climate Chamber Test
- Klimakammertest für verschiedene Umgebungsbedingungen
- 5 Muster (verschiedene Beschichtungen)
- 8 Prüfkriterien (Temperatur-/Feuchtigkeitsphasen)

#### ✅ Product Validation Test
- Produktvalidierung und Vergleichstest
- 5 Muster (verschiedene Lieferanten)
- 8 Prüfkriterien (Maßhaltigkeit, Qualität, Funktion, etc.)

#### 🔍 QS Sampling Test
- Qualitätssicherungs-Stichprobenprüfung
- 10 Stichproben
- 7 Prüfkriterien (Sichtprüfung, Maße, Gewicht, etc.)

#### 👅 Food Sensory Analysis
- Sensorische Bewertung von Lebensmitteln
- 5 Proben (verschiedene Rezepturen)
- 7 Prüfkriterien (Aussehen, Geruch, Geschmack, etc.)

#### 💻 Software Performance Test
- Software-Performance- und Lasttests
- 6 Tests (verschiedene User-Lasten)
- 7 Prüfkriterien (Antwortzeit, CPU, RAM, etc.)

#### 👤 Usability Test
- Usability- und User-Experience-Test
- 6 Testpersonen (verschiedene Erfahrungslevel)
- 7 Prüfkriterien (Aufgabenzeiten, Fehler, Zufriedenheit)

## Verwendung

### Schritt 1: Template-Bibliothek öffnen
- Klicke in der Sidebar auf **"🧬 Versuchs-Templates"**

### Schritt 2: Template auswählen
- Browse durch die 8 verfügbaren Templates
- Klicke auf **"📋 Vorlage Details"** für mehr Informationen
- Klicke auf **"✨ Versuch aus Template erstellen"**

### Schritt 3: Versuch anpassen
- **Versuchsname**: Wird automatisch generiert (Template-Name + Datum)
- **Prüfer**: Automatisch auf aktuellen Benutzer gesetzt
- **Projekt verknüpfen**: Optional ein Projekt zuordnen
- **Beschreibung**: Aus Template vorausgefüllt, anpassbar
- **Prüflinge**: Vorausgefüllt, editierbar (einer pro Zeile)
- **Prüfkriterien**: Vorausgefüllt, editierbar (kommagetrennt)

### Schritt 4: Versuch erstellen
- Klicke auf **"🚀 Versuch erstellen"**
- Der Versuch wird mit allen vordefinierten Daten erstellt
- Automatische Navigation zu den Versuchsdetails

## Technische Details

### Neue Dateien
- **`experiment_templates.py`** (420 Zeilen)
  - `ExperimentTemplateLibrary` Klasse mit 8 Templates
  - `render_experiment_template_library()` - Template-Bibliothek UI
  - `render_create_from_experiment_template()` - Template-Erstellungs-UI

### Geänderte Dateien
- **`project_app.py`**
  - Import von `experiment_templates`
  - Neuer Sidebar-Button "🧬 Versuchs-Templates"
  - Routing für `experiment_templates` und `create_from_experiment_template` Views

### Template-Struktur
Jedes Template enthält:
```python
{
    "icon": "🧪",  # Emoji-Icon
    "description": "Beschreibung",  # Kurzbeschreibung
    "data": {
        "category": "Kategorie",  # z.B. "Chemische Prüfung"
        "description": "Details",  # Ausführliche Beschreibung
        "samples": [...],  # Liste der Prüflinge
        "matrix_columns": [...],  # Liste der Prüfkriterien
        "result_summary": "..."  # Bewertungsskala/Prüfbedingungen
    }
}
```

## Vorteile

✅ **Zeitersparnis**: Bis zu 90% schneller als manuelle Erstellung
✅ **Best Practices**: Bewährte Strukturen integriert
✅ **Konsistenz**: Standardisierte Versuchssetups
✅ **Flexibilität**: Alle Vorlagen vollständig anpassbar
✅ **Vollständig**: Prüflinge und Kriterien vorkonfiguriert
✅ **Einfach**: One-Click Erstellung mit intelligenten Defaults

## Integration mit bestehenden Features

### Kompatibel mit:
- ✅ **Labor & Tests** - Nahtlose Integration
- ✅ **Projekt-Verknüpfung** - Versuche können Projekten zugeordnet werden
- ✅ **Datenerfassung** - Matrix sofort bereit für Dateneingabe
- ✅ **Fotodokumentation** - Alle Template-basierten Versuche unterstützen Fotos
- ✅ **Berichte** - Template-Daten fließen in Berichte ein

## Zukünftige Erweiterungen

Mögliche zukünftige Features:
- 📝 Benutzerdefinierte Templates speichern
- 🔄 Templates aus bestehenden Versuchen erstellen
- 📤 Templates exportieren/importieren
- 🏢 Unternehmens-Template-Bibliothek
- 📊 Template-Nutzungsstatistiken

## Bug Fixes

### TypeError Bug behoben
**Problem**: `TypeError: ProjectManager.add_project() got an unexpected keyword argument 'title'`

**Ursache**: `templates_library.py` verwendete keyword arguments, aber `project_app.py` nutzte noch den alten `data_manager.py` statt `data_manager_v2.py`

**Lösung**:
- `project_app.py` migriert zu `data_manager_v2`
- Import geändert: `from data_manager_v2 import get_project_manager`
- Initialisierung aktualisiert: `get_project_manager()` statt `ProjectManager()`

**Auswirkung**:
- Projekt-Templates funktionieren jetzt einwandfrei
- Bessere Datenvalidierung durch data_manager_v2
- Improved error handling und logging

---

**Version**: 2.2
**Datum**: 2025-11-22
**Autor**: Claude AI Assistant
