"""
Automation Rules Engine
Automated actions based on triggers
"""

import streamlit as st
from datetime import datetime
import uuid


def render_automation_center(manager):
    """Render automation rules center"""
    st.title("🤖 Automation Center")

    st.markdown("""
    Erstelle Regeln um Aktionen automatisch auszuführen.
    **Beispiele:**
    - Wenn Budget > 90% → Sende Warnung
    - Wenn Task Status = Done → Progress +10%
    - Wenn Deadline in 3 Tagen → Status = Critical
    """)

    # Initialize automations in session state
    if 'automation_rules' not in st.session_state:
        st.session_state.automation_rules = []

    tabs = st.tabs(["📋 Active Rules", "➕ Create Rule", "📊 Execution Log"])

    with tabs[0]:
        render_active_rules()

    with tabs[1]:
        render_create_rule()

    with tabs[2]:
        render_execution_log()


def render_active_rules():
    """Display active automation rules"""
    st.subheader("📋 Aktive Automatisierungsregeln")

    if not st.session_state.automation_rules:
        st.info("Keine Automatisierungsregeln definiert")
        return

    for idx, rule in enumerate(st.session_state.automation_rules):
        render_rule_card(rule, idx)


def render_rule_card(rule, idx):
    """Render automation rule card"""
    with st.expander(f"🤖 {rule['name']}", expanded=False):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Trigger:** {rule['trigger_description']}")
            st.markdown(f"**Aktion:** {rule['action_description']}")

            is_active = rule.get('active', True)
            status_text = "✅ Aktiv" if is_active else "⏸️ Pausiert"
            st.caption(f"Status: {status_text}")

            st.caption(f"Erstellt: {rule.get('created_at', 'N/A')}")
            st.caption(f"Ausgeführt: {rule.get('execution_count', 0)}x")

        with col2:
            if st.button("⏸️ Pausieren" if is_active else "▶️ Aktivieren", key=f"toggle_{idx}"):
                rule['active'] = not is_active
                st.rerun()

            if st.button("🗑 Löschen", key=f"delete_{idx}"):
                st.session_state.automation_rules.pop(idx)
                st.rerun()


def render_create_rule():
    """Create new automation rule"""
    st.subheader("➕ Neue Automatisierungsregel erstellen")

    with st.form("create_automation_rule"):
        rule_name = st.text_input("Regelname", placeholder="z.B. Budget-Warnung")

        st.markdown("### 🎯 Trigger (Wenn...)")

        trigger_type = st.selectbox(
            "Trigger-Typ",
            [
                "Budget-Schwellwert",
                "Task Status-Änderung",
                "Deadline erreicht",
                "Projekt-Fortschritt",
                "Team-Member hinzugefügt"
            ]
        )

        trigger_condition = None

        if trigger_type == "Budget-Schwellwert":
            trigger_condition = st.slider("Budget-Nutzung (%)", 0, 150, 90)

        elif trigger_type == "Task Status-Änderung":
            trigger_condition = st.selectbox("Status", ["To Do", "In Progress", "Done"])

        elif trigger_type == "Deadline erreicht":
            trigger_condition = st.number_input("Tage vor Deadline", min_value=1, max_value=30, value=3)

        elif trigger_type == "Projekt-Fortschritt":
            trigger_condition = st.slider("Fortschritt (%)", 0, 100, 50)

        st.markdown("### ⚡ Aktion (Dann...)")

        action_type = st.selectbox(
            "Aktions-Typ",
            [
                "Status ändern",
                "Priorität erhöhen",
                "Benachrichtigung senden",
                "Tag hinzufügen",
                "Team-Member benachrichtigen"
            ]
        )

        action_value = None

        if action_type == "Status ändern":
            action_value = st.selectbox("Neuer Status", ["Idee", "Planung", "In Arbeit", "Review", "Abgeschlossen"])

        elif action_type == "Priorität erhöhen":
            action_value = st.selectbox("Neue Priorität", ["Med", "High", "Critical"])

        elif action_type == "Tag hinzufügen":
            action_value = st.text_input("Tag", placeholder="z.B. 'urgent'")

        submitted = st.form_submit_button("🚀 Regel erstellen", type="primary", use_container_width=True)

        if submitted:
            if not rule_name:
                st.error("Bitte Regelname eingeben")
            else:
                new_rule = {
                    'id': str(uuid.uuid4()),
                    'name': rule_name,
                    'trigger_type': trigger_type,
                    'trigger_condition': trigger_condition,
                    'trigger_description': f"{trigger_type}: {trigger_condition}",
                    'action_type': action_type,
                    'action_value': action_value,
                    'action_description': f"{action_type}: {action_value}",
                    'active': True,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'execution_count': 0
                }

                st.session_state.automation_rules.append(new_rule)
                st.success(f"✅ Regel '{rule_name}' erstellt!")
                st.balloons()
                st.rerun()


def render_execution_log():
    """Display automation execution log"""
    st.subheader("📊 Ausführungsprotokoll")

    if 'automation_log' not in st.session_state:
        st.session_state.automation_log = []

    if not st.session_state.automation_log:
        st.info("Noch keine Automatisierungen ausgeführt")
        return

    for log_entry in st.session_state.automation_log[-50:]:
        with st.container():
            col1, col2 = st.columns([4, 1])

            col1.write(f"**{log_entry.get('rule_name', 'N/A')}**")
            col1.caption(f"{log_entry.get('description', 'N/A')}")

            col2.caption(log_entry.get('timestamp', 'N/A'))

            st.divider()


def execute_automation_rules(manager):
    """Execute automation rules (called periodically)"""
    if 'automation_rules' not in st.session_state:
        return

    if 'automation_log' not in st.session_state:
        st.session_state.automation_log = []

    for rule in st.session_state.automation_rules:
        if not rule.get('active', True):
            continue

        # Check trigger conditions
        triggered = check_trigger(manager, rule)

        if triggered:
            # Execute action
            execute_action(manager, rule)

            # Log execution
            st.session_state.automation_log.append({
                'rule_name': rule['name'],
                'description': f"Trigger: {rule['trigger_description']} → Action: {rule['action_description']}",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Increment execution count
            rule['execution_count'] = rule.get('execution_count', 0) + 1


def check_trigger(manager, rule):
    """Check if trigger condition is met"""
    trigger_type = rule['trigger_type']
    condition = rule.get('trigger_condition')

    if trigger_type == "Budget-Schwellwert":
        # Check all projects
        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            budget = p.get('budget', {})
            total = budget.get('total', 0)
            spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))

            if total > 0:
                usage = (spent / total) * 100
                if usage >= condition:
                    return True

    elif trigger_type == "Projekt-Fortschritt":
        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            if p.get('progress', 0) >= condition:
                return True

    return False


def execute_action(manager, rule):
    """Execute automation action"""
    action_type = rule['action_type']
    action_value = rule.get('action_value')

    if action_type == "Status ändern":
        # Change status of matching projects
        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            manager.update_project(p['id'], {'status': action_value})

    elif action_type == "Priorität erhöhen":
        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            manager.update_project(p['id'], {'priority': action_value})

    elif action_type == "Tag hinzufügen":
        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            tags = p.get('tags', [])
            if action_value not in tags:
                tags.append(action_value)
                manager.update_project(p['id'], {'tags': tags})
