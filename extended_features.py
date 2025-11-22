import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Feature 1: Decision Log (Entscheidungen)
def render_decision_log(manager, pid, project):
    st.subheader("⚖️ Entscheidungen (Decision Log)")
    
    with st.expander("Neue Entscheidung festhalten"):
        with st.form("dec_form"):
            t = st.text_input("Titel (z.B. SQL vs NoSQL)")
            s = st.selectbox("Status", ["Vorgeschlagen", "Akzeptiert", "Abgelehnt"])
            r = st.text_area("Begründung / Kontext")
            if st.form_submit_button("Speichern"):
                manager.add_decision(pid, t, s, r)
                st.rerun()

    decisions = project.get("decisions", [])
    if decisions:
        for i, d in enumerate(decisions):
            color = "green" if d['status'] == "Akzeptiert" else "red" if d['status'] == "Abgelehnt" else "orange"
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f":{color}[**{d['status']}**] - {d['title']} <small>({d['date']})</small>", unsafe_allow_html=True)
                c1.info(d['rationale'])
                if c2.button("🗑", key=f"del_dec_{i}"):
                    manager.delete_decision(pid, i)
                    st.rerun()
                st.markdown("---")
    else:
        st.info("Noch keine Architekturentscheidungen dokumentiert.")

# Feature 2: Bug Tracker
def render_bug_tracker(manager, pid, project):
    st.subheader("🐛 Bug Tracker")
    
    with st.form("bug_form"):
        c1, c2, c3 = st.columns([3, 1, 1])
        t = c1.text_input("Bug Beschreibung")
        s = c2.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        if c3.form_submit_button("Report"):
            manager.add_bug(pid, t, s)
            st.rerun()
            
    bugs = project.get("bugs", [])
    if bugs:
        # Sort by Severity custom sort
        sev_map = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_bugs = sorted(bugs, key=lambda x: sev_map.get(x['severity'], 4))
        
        for i, b in enumerate(sorted_bugs):
            # Find original index for deletion
            orig_idx = bugs.index(b)
            
            icon = "🔴" if b['severity'] in ["Critical", "High"] else "🟠"
            done = b['status'] == "Fixed"
            
            col_check, col_txt, col_del = st.columns([0.5, 4, 0.5])
            if col_check.checkbox("", value=done, key=f"bug_done_{orig_idx}"):
                 if not done: 
                     manager.toggle_bug(pid, orig_idx)
                     st.rerun()
            elif done: # Uncheck
                 manager.toggle_bug(pid, orig_idx)
                 st.rerun()

            style = "text-decoration: line-through; color:grey" if done else ""
            col_txt.markdown(f"<span style='{style}'>{icon} **[{b['severity']}]** {b['title']}</span>", unsafe_allow_html=True)
            
            if col_del.button("x", key=f"del_bug_{orig_idx}"):
                manager.delete_bug(pid, orig_idx)
                st.rerun()
    else:
        st.success("Keine Bugs reported!")

# Feature 3: Stakeholders
def render_stakeholder_view(manager, pid, project):
    st.subheader("🤝 Stakeholder Register")
    
    with st.form("stake_form"):
        c1, c2, c3, c4 = st.columns(4)
        n = c1.text_input("Name")
        o = c2.text_input("Organisation/Abteilung")
        i = c3.selectbox("Einfluss", ["High", "Medium", "Low"])
        if c4.form_submit_button("Add"):
            manager.add_stakeholder(pid, n, o, i)
            st.rerun()

    sh = project.get("stakeholders", [])
    if sh:
        # Matrix Plot
        df = pd.DataFrame(sh)
        # Dummy mapping for plot
        df['y_val'] = df['influence'].map({"High": 3, "Medium": 2, "Low": 1})
        df['x_val'] = [1] * len(df) # Simple list
        
        # Table View
        for i, s in enumerate(sh):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 0.5])
            c1.write(f"**{s['name']}**")
            c2.write(s['org'])
            c3.caption(f"Einfluss: {s['influence']}")
            if c4.button("🗑", key=f"del_sh_{i}"):
                manager.delete_stakeholder(pid, i)
                st.rerun()

# Feature 4: Meeting Minutes
def render_meeting_log(manager, pid, project):
    st.subheader("📝 Meeting Protokolle")
    
    with st.expander("Neues Protokoll"):
        with st.form("meet_form"):
            d = st.date_input("Datum")
            t = st.text_input("Thema")
            s = st.text_area("Ergebnisse / Beschlüsse")
            if st.form_submit_button("Speichern"):
                manager.add_meeting(pid, d.strftime("%Y-%m-%d"), t, s)
                st.rerun()
    
    meetings = project.get("meetings", [])
    for i, m in enumerate(meetings):
        with st.expander(f"📅 {m['date']}: {m['title']}"):
            st.write(m['summary'])
            if st.button("Löschen", key=f"del_meet_{i}"):
                manager.delete_meeting(pid, i)
                st.rerun()

# Feature 5: Secret Safe
def render_secret_safe(manager, pid, project):
    st.subheader("🔐 Secret Safe")
    st.caption("Speichere API-Keys oder Zugangsdaten lokal (Maskiert).")
    
    with st.form("sec_form"):
        c1, c2, c3 = st.columns([2, 2, 1])
        k = c1.text_input("Key (z.B. AWS_SECRET)")
        v = c2.text_input("Value", type="password")
        if c3.form_submit_button("Secure Save"):
            manager.add_secret(pid, k, v)
            st.rerun()
            
    secrets = project.get("secrets", [])
    for i, s in enumerate(secrets):
        c1, c2, c3 = st.columns([2, 2, 0.5])
        c1.code(s['key'])
        # Toggle Visibility Hack via Session State
        show_key = f"show_sec_{pid}_{i}"
        if st.session_state.get(show_key):
            c2.code(s['value'])
            if c2.button("Hide", key=f"btn_hide_{i}"):
                st.session_state[show_key] = False
                st.rerun()
        else:
            c2.text("•••••••••••••")
            if c2.button("Show", key=f"btn_show_{i}"):
                st.session_state[show_key] = True
                st.rerun()
        
        if c3.button("🗑", key=f"del_sec_{i}"):
            manager.delete_secret(pid, i)
            st.rerun()