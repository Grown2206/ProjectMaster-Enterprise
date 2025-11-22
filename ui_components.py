import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Bestehende Funktionen ---
# (Burndown, Gallery, Docs, Gantt, Budget, Risk, Team, Log, Milestones, Time - UNVERÄNDERT)
# Ich aktualisiere hier nur die Kanban-Card für Assignees

def render_kanban_card(manager, pid, task, possible_moves, current_status):
    bg_color = "#262730"
    if current_status == "Done": bg_color = "#1e3a2f" 
    if current_status == "In Progress": bg_color = "#3a2f1e"
    
    # Visualisierungen
    block_icon = "🔒 " if task.get("blocked_by") else ""
    block_msg = f"<div style='color:#ff4b4b; font-size:0.8em'>Wartet auf: {task['blocked_by']}</div>" if task.get("blocked_by") else ""
    
    # NEU: Assignee Anzeige
    assignee_html = ""
    if task.get("assignee"):
        assignee_html = f"<div style='background:#444; color:#ddd; padding:2px 6px; border-radius:4px; font-size:0.8em; display:inline-block; margin-top:5px'>👤 {task['assignee']}</div>"

    comm_count = len(task.get("comments", []))
    comm_icon = f"💬 {comm_count}" if comm_count > 0 else "💬"

    with st.container():
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #444;">
            <strong>{block_icon}{task['text']}</strong>
            {block_msg}
            {assignee_html}
        </div>
        """, unsafe_allow_html=True)
        
        # Actions
        c1, c2, c3 = st.columns([2, 1, 1])
        for move_to in possible_moves:
            label = "➡" if move_to == "Done" or (current_status=="To Do" and move_to=="In Progress") else "⬅"
            if c1.button(f"{label}", key=f"mv_{task['id']}_{move_to}", help=f"Move to {move_to}"):
                manager.update_task_status(pid, task['id'], move_to)
                st.rerun()

        if c3.button("🗑", key=f"del_kan_{task['id']}"):
            manager.delete_task_by_id(pid, task['id'])
            st.rerun()
            
    # Comments
    with st.expander(comm_icon):
        if task.get("comments"):
            for c in task["comments"]:
                st.markdown(f"<small style='color:#aaa'>{c['date']}</small><br>{c['text']}", unsafe_allow_html=True)
                st.markdown("---")
        new_comment = st.text_input("Kommentar...", key=f"nc_{task['id']}")
        if st.button("Senden", key=f"send_c_{task['id']}"):
            if new_comment:
                manager.add_task_comment(pid, task['id'], new_comment)
                st.rerun()

# --- Helper (muss wiederholt werden da "komplette Datei") ---
def render_burndown_chart(project):
    st.subheader("📉 Burn-Down Chart")
    tasks = project.get("tasks", [])
    if not tasks: st.info("Keine Tasks."); return
    total = len(tasks); dates = [project.get('start_date', datetime.now().strftime("%Y-%m-%d"))]; rem = [total]
    done = sorted([t for t in tasks if t.get('completed_at')], key=lambda x: x['completed_at'])
    curr = total
    for t in done: dates.append(t['completed_at']); curr -= 1; rem.append(curr)
    if dates[-1] != datetime.now().strftime("%Y-%m-%d"): dates.append(datetime.now().strftime("%Y-%m-%d")); rem.append(curr)
    st.plotly_chart(px.line(pd.DataFrame({"Date":dates,"Count":rem}), x="Date", y="Count", markers=True), use_container_width=True)

def render_gallery_view(manager, pid, project):
    st.subheader("📸 Galerie")
    images = project.get("images", [])
    if images:
        if st.button("🗑 Alle Bilder löschen", key="del_all_img", type="primary"): manager.delete_all_images(pid); st.rerun()
        cols = st.columns(3)
        for i, p in enumerate(images):
            with cols[i%3]:
                if os.path.exists(p): st.image(p, use_container_width=True)
                else: st.error("Fehlt")
                if st.button("Löschen", key=f"di_{i}"): manager.delete_image(pid, i); st.rerun()

def render_docs_view(manager, pid, project):
    st.subheader("📂 Dokumente")
    for i, d in enumerate(project.get("documents", [])):
        c1, c2, c3 = st.columns([0.5, 4, 1]); c1.write("📄"); c2.write(f"**{d['name']}**")
        if c3.button("Del", key=f"dd_{i}"): manager.delete_document(pid, i); st.rerun()

def render_gantt_view(project):
    st.subheader("📅 Roadmap")
    data = []
    if project.get('start_date') and project.get('deadline'):
        data.append(dict(Task="Projekt", Start=project['start_date'], Finish=project['deadline'], Res="Global"))
    for m in project['milestones']: data.append(dict(Task=m['title'], Start=m['date'], Finish=m['date'], Res="MS"))
    if data: st.plotly_chart(px.timeline(pd.DataFrame(data), x_start="Start", x_end="Finish", y="Task", color="Res"), use_container_width=True)

def render_budget_view(manager, pid, project):
    st.subheader("💰 Budget")
    b = project["budget"]; s = sum(x["amount"] for x in b["expenses"])
    c1, c2 = st.columns(2); c1.metric("Total", f"{b['total']}€"); c2.metric("Rest", f"{b['total']-s}€")
    if b["expenses"]: st.plotly_chart(px.pie(pd.DataFrame(b["expenses"]), values='amount', names='category', hole=0.4), use_container_width=True)
    with st.expander("Verwaltung"):
        with st.form("bf"):
            v=st.number_input("Budget", value=float(b['total']))
            if st.form_submit_button("Set"): manager.set_budget_total(pid, v); st.rerun()
        with st.form("ef"):
            t=st.text_input("Titel"); a=st.number_input("€"); c=st.selectbox("Kat", ["Personal", "Ops", "Marketing"])
            if st.form_submit_button("Add"): manager.add_expense(pid, t, a, c); st.rerun()

def render_risk_view(manager, pid, project):
    st.subheader("⚠️ Risiko-Matrix")
    with st.expander("Add Risk"):
        with st.form("rf"):
            d=st.text_input("Risk"); p=st.slider("Prob",1,10); i=st.slider("Impact",1,10)
            if st.form_submit_button("Save"): manager.add_risk(pid, d, p, i); st.rerun()
    if project['risks']: st.plotly_chart(px.scatter(pd.DataFrame(project['risks']), x="prob", y="impact", hover_name="desc", color="impact", size=[10]*len(project['risks']), range_x=[0,11], range_y=[0,11]), use_container_width=True)

def render_team_view(manager, pid, project):
    st.subheader("👥 Team")
    with st.form("tf"):
        n=st.text_input("Name"); r=st.selectbox("Rolle", ["PM", "Dev", "QA"])
        if st.form_submit_button("Add"): manager.add_team_member(pid, n, r); st.rerun()
    for i, m in enumerate(project['team']): st.write(f"👤 {m['name']} ({m['role']})")

def render_activity_log(project):
    with st.expander("Audit Log"):
        for e in project['activity_log'][:10]: st.write(f"{e['timestamp']}: {e['action']}")

def render_milestones_view(manager, pid, project):
    st.subheader("🏁 Meilensteine")
    with st.form("mf"):
        t=st.text_input("Titel"); d=st.date_input("Datum")
        if st.form_submit_button("Add"): manager.add_milestone(pid, t, d.strftime("%Y-%m-%d")); st.rerun()
    for m in project['milestones']: st.write(f"{'✅' if m['done'] else '⭕'} {m['date']}: {m['title']}")

def render_time_tracking_view(manager, pid, project):
    st.subheader("⏱ Zeiten")
    with st.expander("Log Time"):
        with st.form("ttf"):
            d=st.date_input("Date"); c=st.selectbox("Kat", ["Dev", "Plan"]); h=st.number_input("h")
            if st.form_submit_button("Log"): manager.add_time_log(pid, d.strftime("%Y-%m-%d"), c, h, ""); st.rerun()
    if project['time_logs']: st.plotly_chart(px.bar(pd.DataFrame(project['time_logs']), x='date', y='hours', color='category'), use_container_width=True)