import streamlit as st
import random
import time

def render_ai_assistant(manager, pid, project):
    st.subheader("🤖 AI Project Copilot")
    st.caption("Generiere automatisch Aufgaben und Risiken basierend auf deinen Projektdaten.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚡ Aufgaben Generator")
        if st.button("Generiere Aufgaben-Vorschläge"):
            with st.spinner("AI analysiert Projektbeschreibung..."):
                time.sleep(1.5) # Simuliere Denkzeit
                suggestions = generate_mock_tasks(project['category'], project['title'])
                st.session_state['ai_task_suggestions'] = suggestions
        
        if 'ai_task_suggestions' in st.session_state:
            st.success(f"{len(st.session_state['ai_task_suggestions'])} Vorschläge gefunden:")
            for task in st.session_state['ai_task_suggestions']:
                c1, c2 = st.columns([4, 1])
                c1.write(task)
                if c2.button("➕", key=f"add_ai_task_{hash(task)}"):
                    manager.add_task(pid, task)
                    st.toast(f"Task '{task}' hinzugefügt!")

    with col2:
        st.markdown("#### 🛡 Risiko Analyse")
        if st.button("Erkenne potenzielle Risiken"):
            with st.spinner("Prüfe Risikofaktoren..."):
                time.sleep(1.5)
                risks = generate_mock_risks(project['category'])
                st.session_state['ai_risk_suggestions'] = risks
        
        if 'ai_risk_suggestions' in st.session_state:
            for r in st.session_state['ai_risk_suggestions']:
                with st.expander(f"⚠ {r['desc']}"):
                    st.write(f"Wahrscheinlichkeit: {r['prob']} | Impact: {r['impact']}")
                    if st.button("Übernehmen", key=f"add_ai_risk_{hash(r['desc'])}"):
                        manager.add_risk(pid, r['desc'], r['prob'], r['impact'])
                        st.rerun()

def generate_mock_tasks(category, title):
    """Einfache Heuristik für Demo-Zwecke"""
    base_tasks = ["Projekt-Kickoff Meeting", "Stakeholder Analyse", "Budget Finalisierung"]
    
    if category == "IT" or category == "Software":
        return base_tasks + ["Git Repository aufsetzen", "Datenbank Schema entwerfen", "API Dokumentation schreiben", "Unit Tests aufsetzen", "Deployment Pipeline konfigurieren"]
    elif category == "Marketing":
        return base_tasks + ["Zielgruppenanalyse", "Social Media Kanäle anlegen", "Content Plan Q1 erstellen", "Ad-Budget freigeben", "Grafik-Assets erstellen"]
    elif category == "HR":
        return base_tasks + ["Stellenanzeige entwerfen", "Interviews koordinieren", "Onboarding Plan schreiben", "Vertragsentwürfe prüfen"]
    else:
        return base_tasks + ["Meilensteinplan erstellen", "Ressourcen anfordern", "Team Meeting"]

def generate_mock_risks(category):
    common = [{"desc": "Budgetüberschreitung", "prob": 5, "impact": 8}, {"desc": "Personalmangel durch Krankheit", "prob": 4, "impact": 7}]
    if category == "IT":
        return common + [{"desc": "Technische Schulden", "prob": 6, "impact": 6}, {"desc": "Sicherheitslücke in 3rd Party Lib", "prob": 3, "impact": 10}]
    return common