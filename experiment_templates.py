"""
Experiment Templates Library
Pre-configured templates for different test types and experiments
"""

import streamlit as st
from typing import Dict, List
import uuid
from datetime import datetime


class ExperimentTemplateLibrary:
    """Library of experiment templates"""

    TEMPLATES = {
        "Chemical Resistance Test": {
            "icon": "🧪",
            "description": "Chemische Beständigkeitsprüfung mit verschiedenen Materialien",
            "data": {
                "category": "Chemische Prüfung",
                "description": "Test der chemischen Beständigkeit verschiedener Materialproben gegen aggressive Medien",
                "samples": [
                    "Blech 01 (V2A glasgeperlt)",
                    "Blech 02 (V2A blank)",
                    "Blech 03 (V2A geschliffen)",
                    "Blech 04 (V4A glasgeperlt)",
                    "Blech 05 (V4A geschliffen)",
                    "Blech 06 (V4A blank)",
                    "Blech 07 (Aluminium eloxiert)",
                    "Blech 08 (Kunststoff PP)"
                ],
                "matrix_columns": [
                    "Woche 1 (5% Konzentration)",
                    "Woche 2 (15% Konzentration)",
                    "Woche 3 (15% trocken)",
                    "Woche 4 (15% trocken)",
                    "Gesamtbewertung",
                    "Anmerkungen"
                ],
                "result_summary": "Bewertungsskala: 1=keine Veränderung, 2=leichte Verfärbung, 3=starke Verfärbung, 4=Korrosion, 5=Zerstörung"
            }
        },
        "Mechanical Durability Test": {
            "icon": "⚙️",
            "description": "Mechanische Dauerprüfung von Bauteilen",
            "data": {
                "category": "Mechanische Dauerprüfung",
                "description": "Langzeit-Dauertest zur Prüfung der mechanischen Belastbarkeit",
                "samples": [
                    "Prüfling 1 (Serie A)",
                    "Prüfling 2 (Serie A)",
                    "Prüfling 3 (Serie B)",
                    "Prüfling 4 (Serie B)",
                    "Prüfling 5 (Referenz Alt)",
                    "Prüfling 6 (Referenz Neu)"
                ],
                "matrix_columns": [
                    "Zyklen (Anzahl)",
                    "Maximalkraft (N)",
                    "Verformung (mm)",
                    "Verschleiß (%)",
                    "Rissbildung",
                    "Funktionsfähigkeit",
                    "Bewertung"
                ],
                "result_summary": "Prüfbedingungen: 10.000 Zyklen bei Raumtemperatur, Belastung 500N"
            }
        },
        "Climate Chamber Test": {
            "icon": "🌡️",
            "description": "Klimakammertest für verschiedene Umgebungsbedingungen",
            "data": {
                "category": "Klimatest",
                "description": "Simulation verschiedener Klimabedingungen (Temperatur, Luftfeuchtigkeit)",
                "samples": [
                    "Muster 1 (Standardausführung)",
                    "Muster 2 (Beschichtet)",
                    "Muster 3 (Versiegelt)",
                    "Muster 4 (Unbeschichtet)",
                    "Referenzmuster"
                ],
                "matrix_columns": [
                    "Ausgangszustand",
                    "Nach 24h (+40°C, 90% rF)",
                    "Nach 48h (+40°C, 90% rF)",
                    "Nach 72h (+40°C, 90% rF)",
                    "Nach Kältephase (-20°C)",
                    "Nach Temperaturwechsel",
                    "Endzustand",
                    "Auffälligkeiten"
                ],
                "result_summary": "Klimaprofil: Warm/Feucht (40°C/90%rF), Kalt (-20°C), Temperaturwechsel (±60°C)"
            }
        },
        "Product Validation Test": {
            "icon": "✅",
            "description": "Produktvalidierung und Vergleichstest",
            "data": {
                "category": "Validierung",
                "description": "Vergleichende Bewertung verschiedener Produktvarianten oder Lieferanten",
                "samples": [
                    "Muster A (Lieferant 1)",
                    "Muster B (Lieferant 2)",
                    "Muster C (Lieferant 3)",
                    "Referenzmuster (Aktuell)",
                    "Prototyp (Neu)"
                ],
                "matrix_columns": [
                    "Maßhaltigkeit",
                    "Oberflächenqualität",
                    "Material",
                    "Funktion",
                    "Dokumentation",
                    "Preis-Leistung",
                    "Gesamturteil",
                    "Freigabe"
                ],
                "result_summary": "Bewertung: 1=sehr gut, 2=gut, 3=befriedigend, 4=ausreichend, 5=mangelhaft, 6=ungenügend"
            }
        },
        "QS Sampling Test": {
            "icon": "🔍",
            "description": "Qualitätssicherungs-Stichprobenprüfung",
            "data": {
                "category": "Funktionstest",
                "description": "Stichprobenprüfung zur Qualitätssicherung einer Produktcharge",
                "samples": [
                    "Stichprobe 1 (Los 2024-001)",
                    "Stichprobe 2 (Los 2024-001)",
                    "Stichprobe 3 (Los 2024-001)",
                    "Stichprobe 4 (Los 2024-001)",
                    "Stichprobe 5 (Los 2024-001)",
                    "Stichprobe 6 (Los 2024-001)",
                    "Stichprobe 7 (Los 2024-001)",
                    "Stichprobe 8 (Los 2024-001)",
                    "Stichprobe 9 (Los 2024-001)",
                    "Stichprobe 10 (Los 2024-001)"
                ],
                "matrix_columns": [
                    "Sichtprüfung",
                    "Maße (mm)",
                    "Gewicht (g)",
                    "Funktion",
                    "Kennzeichnung",
                    "Verpackung",
                    "i.O. / n.i.O."
                ],
                "result_summary": "AQL 1.5, Prüfniveau II, Stichprobengröße n=10"
            }
        },
        "Food Sensory Analysis": {
            "icon": "👅",
            "description": "Sensorische Bewertung von Lebensmitteln",
            "data": {
                "category": "Funktionstest",
                "description": "Sensorische Analyse verschiedener Produktvarianten (Geschmack, Geruch, Aussehen)",
                "samples": [
                    "Probe A (Rezeptur 1)",
                    "Probe B (Rezeptur 2)",
                    "Probe C (Rezeptur 3)",
                    "Probe D (Referenz)",
                    "Probe E (Wettbewerber)"
                ],
                "matrix_columns": [
                    "Aussehen (1-10)",
                    "Geruch (1-10)",
                    "Geschmack (1-10)",
                    "Konsistenz (1-10)",
                    "Nachgeschmack (1-10)",
                    "Gesamteindruck (1-10)",
                    "Kaufbereitschaft"
                ],
                "result_summary": "Sensorikpanel: 10 Prüfer, Skala 1-10 (1=sehr schlecht, 10=hervorragend)"
            }
        },
        "Software Performance Test": {
            "icon": "💻",
            "description": "Software-Performance- und Lasttests",
            "data": {
                "category": "Funktionstest",
                "description": "Performance-Tests unter verschiedenen Lastszenarien",
                "samples": [
                    "Test 1 (10 User)",
                    "Test 2 (50 User)",
                    "Test 3 (100 User)",
                    "Test 4 (500 User)",
                    "Test 5 (1000 User)",
                    "Test 6 (Spitzenlast)"
                ],
                "matrix_columns": [
                    "Antwortzeit Ø (ms)",
                    "Antwortzeit Max (ms)",
                    "CPU-Auslastung (%)",
                    "RAM-Auslastung (MB)",
                    "Fehlerrate (%)",
                    "Durchsatz (req/s)",
                    "Bewertung"
                ],
                "result_summary": "Lasttest über 30 Minuten, Ramp-up: 60 Sekunden, Ziel: <200ms Antwortzeit bei <1% Fehlerrate"
            }
        },
        "Usability Test": {
            "icon": "👤",
            "description": "Usability- und User-Experience-Test",
            "data": {
                "category": "Validierung",
                "description": "Benutzerfreundlichkeitstest mit verschiedenen Testpersonen",
                "samples": [
                    "Testperson 1 (Experte)",
                    "Testperson 2 (Fortgeschritten)",
                    "Testperson 3 (Anfänger)",
                    "Testperson 4 (Anfänger)",
                    "Testperson 5 (Senior)",
                    "Testperson 6 (Senior)"
                ],
                "matrix_columns": [
                    "Aufgabe 1: Login (Zeit)",
                    "Aufgabe 2: Navigation (Zeit)",
                    "Aufgabe 3: Formular (Zeit)",
                    "Aufgabe 4: Suche (Zeit)",
                    "Fehleranzahl",
                    "Zufriedenheit (1-10)",
                    "Verbesserungsvorschläge"
                ],
                "result_summary": "Think-Aloud-Methode, 4 Standardaufgaben, Erfolgskriterium: <2 Fehler pro Person"
            }
        }
    }

    @classmethod
    def get_template_names(cls) -> List[str]:
        """Get list of template names"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template(cls, name: str) -> Dict:
        """Get template by name"""
        return cls.TEMPLATES.get(name)


def render_experiment_template_library(manager):
    """Render experiment template library interface"""
    st.title("🧪 Experiment Templates")

    st.markdown("""
    Wähle eine vorkonfigurierte Versuchsvorlage und erstelle damit in Sekunden
    einen neuen Versuch mit vordefinierten Prüflingen und Kriterien.
    """)

    # Template selection
    template_names = ExperimentTemplateLibrary.get_template_names()

    # Display templates in grid
    cols = st.columns(2)

    for idx, template_name in enumerate(template_names):
        template = ExperimentTemplateLibrary.get_template(template_name)
        col = cols[idx % 2]

        with col:
            with st.container():
                st.markdown(f"### {template['icon']} {template_name}")
                st.caption(template['description'])

                # Template details
                with st.expander("📋 Vorlage Details"):
                    data = template['data']
                    st.write(f"**Kategorie:** {data['category']}")
                    st.write(f"**Beschreibung:** {data['description']}")
                    st.write(f"**Anzahl Prüflinge:** {len(data['samples'])}")
                    st.write(f"**Anzahl Kriterien:** {len(data['matrix_columns'])}")

                    st.markdown("**Prüflinge:**")
                    for sample in data['samples'][:3]:
                        st.write(f"• {sample}")
                    if len(data['samples']) > 3:
                        st.write(f"• ... und {len(data['samples']) - 3} weitere")

                    st.markdown("**Prüfkriterien:**")
                    for col_name in data['matrix_columns'][:3]:
                        st.write(f"• {col_name}")
                    if len(data['matrix_columns']) > 3:
                        st.write(f"• ... und {len(data['matrix_columns']) - 3} weitere")

                # Create from template button
                if st.button(f"✨ Versuch aus Template erstellen", key=f"create_{template_name}", use_container_width=True):
                    st.session_state.selected_template = template_name
                    st.session_state.view = 'create_from_experiment_template'
                    st.rerun()

                st.divider()


def render_create_from_experiment_template(manager):
    """Create experiment from template"""
    st.title("✨ Versuch aus Template erstellen")

    template_name = st.session_state.get('selected_template')

    if not template_name:
        st.error("Kein Template ausgewählt")
        if st.button("← Zurück zur Template-Bibliothek"):
            st.session_state.view = 'experiment_templates'
            st.rerun()
        return

    template = ExperimentTemplateLibrary.get_template(template_name)

    # Back button
    if st.button("← Zurück zur Template-Bibliothek"):
        st.session_state.view = 'experiment_templates'
        st.rerun()

    st.markdown(f"### {template['icon']} {template_name}")
    st.info(template['description'])

    # Form to customize template
    with st.form("create_experiment_from_template"):
        st.markdown("### 📝 Versuchsdetails")

        experiment_name = st.text_input(
            "Versuchsname *",
            value=f"{template_name} - {datetime.now().strftime('%Y-%m-%d')}",
            help="Eindeutiger Name für diesen Versuch"
        )

        col1, col2 = st.columns(2)

        with col1:
            tester = st.text_input(
                "Prüfer *",
                value=st.session_state.auth.current_user_name(),
                help="Verantwortlicher Prüfer"
            )

        with col2:
            project_link = st.selectbox(
                "Projekt verknüpfen (optional)",
                options=["Kein Projekt"] + [p['title'] for p in manager.projects if not p.get('is_deleted')],
                help="Optional: Versuch einem Projekt zuordnen"
            )

        description = st.text_area(
            "Zusätzliche Beschreibung",
            value=template['data']['description'],
            height=100,
            help="Zielsetzung und Parameter des Versuchs"
        )

        st.markdown("### 🧪 Prüflinge")
        st.caption("Du kannst die vorkonfigurierten Prüflinge anpassen (einer pro Zeile)")

        samples_text = st.text_area(
            "Prüflinge",
            value="\n".join(template['data']['samples']),
            height=200,
            help="Ein Prüfling pro Zeile"
        )

        st.markdown("### 📊 Prüfkriterien")
        st.caption("Du kannst die vorkonfigurierten Kriterien anpassen (kommagetrennt)")

        columns_text = st.text_area(
            "Prüfkriterien",
            value=", ".join(template['data']['matrix_columns']),
            height=100,
            help="Kommagetrennte Spaltennamen"
        )

        submitted = st.form_submit_button("🚀 Versuch erstellen", type="primary", use_container_width=True)

        if submitted:
            if not experiment_name or not tester:
                st.error("Bitte Versuchsname und Prüfer angeben")
            else:
                # Parse samples
                sample_list = []
                for line in samples_text.split('\n'):
                    if line.strip():
                        sample_list.append({
                            "id": str(uuid.uuid4()),
                            "name": line.strip()
                        })

                # Parse columns
                column_list = [c.strip() for c in columns_text.split(',') if c.strip()]

                # Create matrix data
                matrix_data = []
                for sample in sample_list:
                    row_obj = {
                        "sample_id": sample['id'],
                        "sample_name": sample['name']
                    }
                    for col in column_list:
                        row_obj[col] = ""
                    matrix_data.append(row_obj)

                # Get project ID if linked
                project_id = None
                if project_link != "Kein Projekt":
                    project = next((p for p in manager.projects if p['title'] == project_link), None)
                    if project:
                        project_id = project['id']

                # Create experiment
                exp_id = manager.add_experiment(
                    name=experiment_name,
                    description=description,
                    category=template['data']['category'],
                    tester=tester,
                    project_id=project_id
                )

                # Update experiment with template data
                manager.update_experiment_matrix(
                    exp_id,
                    sample_list,
                    column_list,
                    matrix_data
                )

                # Update result summary if provided
                if template['data'].get('result_summary'):
                    exp = manager.get_experiment(exp_id)
                    if exp:
                        exp['result_summary'] = template['data']['result_summary']
                        manager.save_experiments()

                st.success(f"✅ Versuch '{experiment_name}' erfolgreich erstellt!")
                st.balloons()

                # Navigate to experiment details
                st.session_state.selected_experiment_id = exp_id
                st.session_state.view = 'experiment_details'
                st.rerun()
