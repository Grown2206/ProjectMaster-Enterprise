import streamlit as st
import os
import pandas as pd
from data_manager_v2 import get_project_manager
from auth_manager import AuthManager
from utils import calculate_days_left, save_uploaded_image, save_uploaded_doc, fetch_git_readme, parse_csv_tasks

# Existing modules
from kanban_board import render_kanban_board
from ai_assistant import render_ai_assistant
from global_dashboard import render_global_dashboard
from pdf_export import create_project_pdf
from ui_components import *
from extended_features import *
from strategy_tools import *
from knowledge_base import *
from qa_module import render_qa_dashboard
from calendar_module import render_calendar_view
from experiment_module import render_lab_dashboard, render_experiment_details

# NEW FEATURES v2.1 - 10 Amazing Additions!
from analytics_dashboard import render_analytics_dashboard
from export_import import render_export_import_center
from notification_center import render_notification_center, render_notification_badge
from templates_library import render_template_library, render_template_creation
from time_tracking_pro import render_timesheet_manager
from advanced_search import render_advanced_search
from sprint_management import render_sprint_management
from dashboard_widgets import render_custom_dashboard
from automation_engine import render_automation_center, execute_automation_rules
from theme_manager import render_theme_settings, apply_theme, get_theme_css
from experiment_templates import render_experiment_template_library, render_create_from_experiment_template

# NEW FEATURES v2.2 - 5 Game-Changing Additions!
from achievement_system import render_achievement_center, track_feature_access
from invoice_generator import render_invoice_generator
from resource_manager import render_resource_manager
from gantt_chart import render_gantt_chart_view
from comments_system import render_comment_notifications, render_comments_section, CommentsSystem

# NEW FEATURES v2.3 - 4 Advanced Additions!
from mind_map_visualizer import render_mind_map_view
from version_control import render_version_control
from dependency_manager import render_dependency_manager
from calendar_export import render_calendar_export

# NEW FEATURES v2.3.1 - Overview Dashboard with Preview Images!
from overview_dashboard import render_overview_dashboard

# --- SETUP ---
st.set_page_config(
    page_title="Project Master Enterprise v2.1",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
apply_theme()

st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
    <style>
    .card-container { background-color: #1e1e1e; border: 1px solid #333; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; transition: all 0.3s ease; }
    .card-container:hover { border-color: #00cc99; transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0, 204, 153, 0.3); }
    .notification-box { background-color: #ff4b4b; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    .tag-span { background-color: #333; color: #eee; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px; }
    .health-badge-green { color: #00cc99; font-weight: bold; border: 1px solid #00cc99; padding: 2px 8px; border-radius: 8px; }
    .health-badge-orange { color: orange; font-weight: bold; border: 1px solid orange; padding: 2px 8px; border-radius: 8px; }
    .health-badge-red { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 8px; }

    /* Presentation Styles */
    .slide-container { padding: 40px; background: #111; border-radius: 20px; margin-bottom: 50px; border: 1px solid #333; }
    .slide-title { font-size: 3.5em; font-weight: 900; background: -webkit-linear-gradient(#eee, #555); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .slide-section { font-size: 1.8em; color: #00cc99; border-bottom: 2px solid #00cc99; margin-top: 40px; margin-bottom: 20px; padding-bottom: 10px; }
    .stat-box { background: #222; padding: 20px; border-radius: 10px; text-align: center; border-left: 5px solid #00cc99; }
    .stat-val { font-size: 2em; font-weight: bold; }
    .stat-lbl { text-transform: uppercase; font-size: 0.7em; color: #aaa; }

    /* NEW: Feature badges */
    .feature-badge { background: linear-gradient(135deg, #00cc99 0%, #0099cc 100%); color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

if 'manager' not in st.session_state: st.session_state.manager = get_project_manager()
if 'auth' not in st.session_state: st.session_state.auth = AuthManager(st.session_state.manager)
if 'view' not in st.session_state: st.session_state.view = 'dashboard'
if 'selected_project_id' not in st.session_state: st.session_state.selected_project_id = None
if 'selected_experiment_id' not in st.session_state: st.session_state.selected_experiment_id = None # NEU

def nav_to(view, pid=None):
    st.session_state.view = view
    st.session_state.selected_project_id = pid
    st.rerun()

if not st.session_state.auth.check_login():
    st.stop() 

# Execute automation rules
execute_automation_rules(st.session_state.manager)

# --- SIDEBAR ---
def render_sidebar():
    st.sidebar.title("🏢 PM Suite v2.1")
    user_name = st.session_state.auth.current_user_name()
    st.sidebar.markdown(f"👤 **{user_name}**")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.auth.logout()
    st.sidebar.markdown("---")

    # NEW: Notification Badge
    render_notification_badge(st.session_state.manager, user_name)

    # Inbox
    my_open_tasks = []
    for p in st.session_state.manager.projects:
        if not p.get('is_deleted'):
            for t in p.get('tasks', []):
                if t.get('assignee') == user_name and t['status'] != 'Done':
                    my_open_tasks.append((t, p))
    if my_open_tasks:
        with st.sidebar.expander(f"📬 {len(my_open_tasks)} Aufgaben", expanded=False):
            for task, proj in my_open_tasks[:5]:
                if st.button(f"👉 {task['text'][:15]}.. ({proj['title'][:5]}..)", key=f"nav_my_{task['id']}"):
                    nav_to('details', proj['id'])

    st.sidebar.markdown("---")

    # Main Navigation
    st.sidebar.markdown("### 📍 Navigation")
    if st.sidebar.button("🎯 Übersicht Dashboard", use_container_width=True): nav_to('overview')
    if st.sidebar.button("📊 My Dashboard", use_container_width=True): nav_to('my_dashboard')
    if st.sidebar.button("📈 Analytics", use_container_width=True): nav_to('analytics')
    if st.sidebar.button("🔍 Advanced Search", use_container_width=True): nav_to('advanced_search')

    st.sidebar.markdown("---")

    # Projects
    st.sidebar.markdown("### 📁 Projekte")
    if st.sidebar.button("➕ Projekt anlegen", use_container_width=True): nav_to('create')
    if st.sidebar.button("📚 Aus Template", use_container_width=True): nav_to('template_library')
    if st.sidebar.button("🌍 Global View", use_container_width=True): nav_to('global')

    st.sidebar.markdown("---")

    # NEW Features
    st.sidebar.markdown("### ✨ Features")
    if st.sidebar.button("⏱️ Time Tracking", use_container_width=True): nav_to('timesheet')
    if st.sidebar.button("⚡ Sprint Management", use_container_width=True): nav_to('sprints')
    if st.sidebar.button("🧪 Labor & Tests", use_container_width=True): nav_to('lab')
    if st.sidebar.button("🧬 Versuchs-Templates", use_container_width=True): nav_to('experiment_templates')
    if st.sidebar.button("🤖 Automation", use_container_width=True): nav_to('automation')

    st.sidebar.markdown("---")

    # Tools
    st.sidebar.markdown("### 🛠️ Tools")
    if st.sidebar.button("📦 Export/Import", use_container_width=True): nav_to('export_import')
    if st.sidebar.button("📊 Gantt Chart", use_container_width=True): nav_to('gantt_chart')
    if st.sidebar.button("🗺️ Mind Map", use_container_width=True): nav_to('mind_map')
    if st.sidebar.button("📜 Version Control", use_container_width=True): nav_to('version_control')
    if st.sidebar.button("🔗 Dependencies", use_container_width=True): nav_to('dependencies')
    if st.sidebar.button("📅 Calendar Export", use_container_width=True): nav_to('calendar_export')

    deleted_count = len([p for p in st.session_state.manager.projects if p.get('is_deleted')])
    if st.sidebar.button(f"🗑 Papierkorb ({deleted_count})", use_container_width=True): nav_to('trash')

    if st.sidebar.button("🎨 Theme Settings", use_container_width=True): nav_to('theme_settings')

    st.sidebar.markdown("---")

    # NEW v2.2: Business & Collaboration
    st.sidebar.markdown("### 💼 Business")
    if st.sidebar.button("💰 Invoices", use_container_width=True): nav_to('invoices')
    if st.sidebar.button("📦 Resources", use_container_width=True): nav_to('resources')
    if st.sidebar.button("💬 Comments", use_container_width=True):
        CommentsSystem.initialize_session_state()
        unread = CommentsSystem.get_unread_mentions(st.session_state.auth.current_user_name())
        nav_to('comment_notifications')
    if st.sidebar.button("🏆 Achievements", use_container_width=True): nav_to('achievements')

    st.sidebar.markdown("---")
    if st.session_state.view == 'details':
        st.sidebar.caption(f"Projekt: {st.session_state.manager.get_project(st.session_state.selected_project_id)['title']}")
        if st.sidebar.button("📢 Präsentation", type="primary", use_container_width=True):
             nav_to('presentation', st.session_state.selected_project_id)

# --- VIEWS ---

def render_search_results():
    st.title("🔍 Suchergebnisse")
    query = st.session_state.get('search_query', '').lower()
    if not query: return
    hits = 0
    for p in st.session_state.manager.projects:
        if p.get('is_deleted'): continue
        match = False
        if query in p['title'].lower() or query in p['description'].lower(): match = True
        else:
            for t in p['tasks']:
                if query in t['text'].lower(): match = True; break
        if match:
            hits += 1
            st.markdown(f"**{p['title']}**")
            if st.button("Zum Projekt", key=f"s_{p['id']}"): nav_to('details', p['id'])
            st.divider()
    if hits == 0: st.warning("Nichts gefunden.")

def render_trash_bin():
    st.title("🗑 Papierkorb")
    deleted = [p for p in st.session_state.manager.projects if p.get('is_deleted')]
    if not deleted: st.info("Leer."); return
    for p in deleted:
        c1, c2, c3 = st.columns([4,1,1])
        c1.write(f"**{p['title']}**")
        if c2.button("♻", key=f"res_{p['id']}"): st.session_state.manager.restore_project(p['id']); st.rerun()
        if c3.button("🔥", key=f"kill_{p['id']}"): st.session_state.manager.delete_project_permanent(p['id']); st.rerun()

def render_dashboard():
    st.title("Executive Dashboard")
    show_archived = st.checkbox("Zeige Archiv")
    projects = [p for p in st.session_state.manager.projects if p.get('is_archived', False) == show_archived and not p.get('is_deleted')]
    k1, k2, k3 = st.columns(3)
    k1.metric("Projekte", len(projects))
    k2.metric("Budget", f"{sum(p['budget']['total'] for p in projects):,.0f} €")
    k3.metric("Tasks", sum(len([t for t in p.get('tasks',[]) if t.get('status')!='Done']) for p in projects))
    st.divider()
    
    cols = st.columns(3)
    for idx, p in enumerate(projects):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
                if p['images'] and os.path.exists(p['images'][0]): st.image(p['images'][0], use_container_width=True)
                st.markdown(f"### {p['title']}")
                health, color = st.session_state.manager.calculate_health(p['id'])
                st.markdown(f"<span class='health-badge-{color}'>{health}</span>", unsafe_allow_html=True)
                st.caption(f"{p['category']} | {p['status']}")
                st.progress(p['progress']/100)
                if st.button("Open", key=f"b_{p['id']}", use_container_width=True): nav_to('details', p['id'])
                st.markdown('</div>', unsafe_allow_html=True)

def render_create():
    st.title("Projektstart")
    templates = [p for p in st.session_state.manager.projects if p.get('is_template') and not p.get('is_deleted')]
    tmpl_name = st.selectbox("Vorlage", ["Leer"] + [p['title'] for p in templates])
    with st.form("new_p"):
        t = st.text_input("Titel")
        if tmpl_name != "Leer":
            if st.form_submit_button("Starten"):
                src = next(p for p in templates if p['title'] == tmpl_name)
                pid = st.session_state.manager.duplicate_project(src['id'], t)
                nav_to('details', pid)
        else:
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Kat", ["IT", "Marketing", "HR", "R&D", "Privat"])
            prio = c2.select_slider("Prio", ["Low", "Med", "High"], value="Med")
            desc = st.text_area("Beschreibung")
            git = st.text_input("Git")
            dl = st.date_input("Deadline")
            tags = st.text_input("Tags")
            is_tmpl = st.checkbox("Als Vorlage?")
            if st.form_submit_button("Erstellen"):
                ts = [x.strip() for x in tags.split(",") if x.strip()]
                pid = st.session_state.manager.add_project(t, desc, cat, prio, dl, git, ts, is_tmpl)
                nav_to('details', pid)

def render_details():
    pid = st.session_state.selected_project_id
    p = st.session_state.manager.get_project(pid)
    if not p or p.get('is_deleted'): nav_to('dashboard'); return

    c1, c2, c3 = st.columns([1, 8, 2])
    c1.button("⬅", on_click=lambda: nav_to('dashboard'))
    c2.title(p['title'])
    if c3.button("📄 PDF"):
        f = create_project_pdf(p)
        if f: 
            with open(f, "rb") as file: st.download_button("Download", file, f"{p['title']}.pdf")

    tabs = st.tabs(["📋 Board", "👥 Team", "📅 Planung", "💰 Budget", "🧪 QA", "📄 Infos", "📈 Analyse", "🎯 Strat.", "🧠 Wissen", "🧩 Ext", "⚙️ Set"])

    with tabs[0]: # Board
        render_kanban_board(st.session_state.manager, pid, p)
        with st.expander("➕ Task"):
            c_t, c_a, c_b = st.columns([3, 2, 1])
            nt = c_t.text_input("Task")
            all_users = [u['name'] for u in st.session_state.manager.users]
            assignee = c_a.selectbox("Wer?", ["Keine"] + all_users)
            bb = c_b.selectbox("Blocker", ["None"] + [t['text'] for t in p['tasks']])
            if st.button("Add"):
                ass = assignee if assignee != "Keine" else None
                blk = bb if bb != "None" else None
                st.session_state.manager.add_task(pid, nt, blocked_by=blk, assignee=ass)
                st.rerun()

    with tabs[1]: render_team_view(st.session_state.manager, pid, p)
    with tabs[2]:
        render_calendar_view(st.session_state.manager, pid, p); st.divider()
        c1, c2 = st.columns(2)
        with c1: render_milestones_view(st.session_state.manager, pid, p)
        with c2: render_time_tracking_view(st.session_state.manager, pid, p)
        render_gantt_view(p)
    with tabs[3]: render_budget_view(st.session_state.manager, pid, p)
    with tabs[4]: render_qa_dashboard(st.session_state.manager, pid, p)
    with tabs[5]:
        c_g, c_s = st.columns([3, 1])
        git = c_g.text_input("Git", value=p.get('git_url', ""))
        if c_s.button("Sync"):
            c = fetch_git_readme(git)
            if c: st.session_state.manager.update_project(pid, {"git_url": git, "readme_content": c}); st.success("OK"); st.rerun()
        if p.get('readme_content'): st.markdown(p['readme_content'])
        else: st.write(p['description'])
        st.divider(); render_docs_view(st.session_state.manager, pid, p)
        st.divider()
        with st.form("iu", clear_on_submit=True):
            uf = st.file_uploader("Bilder", accept_multiple_files=True)
            if st.form_submit_button("Upload") and uf:
                for f in uf: st.session_state.manager.add_image(pid, save_uploaded_image(f, pid))
                st.rerun()
        render_gallery_view(st.session_state.manager, pid, p)
    with tabs[6]: render_ai_assistant(st.session_state.manager, pid, p); st.divider(); render_burndown_chart(p); render_risk_view(st.session_state.manager, pid, p)
    with tabs[7]: render_swot_analysis(st.session_state.manager, pid, p); st.divider(); render_okr_manager(st.session_state.manager, pid, p); st.divider(); render_retro_board(st.session_state.manager, pid, p)
    with tabs[8]: render_wiki(st.session_state.manager, pid, p); st.divider(); render_backlog(st.session_state.manager, pid, p)
    with tabs[9]: 
        t = st.tabs(["Decisions", "Bugs", "Stakeholder", "Meetings", "Secrets"])
        with t[0]: render_decision_log(st.session_state.manager, pid, p)
        with t[1]: render_bug_tracker(st.session_state.manager, pid, p)
        with t[2]: render_stakeholder_view(st.session_state.manager, pid, p)
        with t[3]: render_meeting_log(st.session_state.manager, pid, p)
        with t[4]: render_secret_safe(st.session_state.manager, pid, p)
    with tabs[10]:
        curr_tags = ", ".join(p.get('tags', []))
        nt = st.text_input("Tags", value=curr_tags)
        if st.button("Update Tags"): st.session_state.manager.update_project(pid, {"tags": [x.strip() for x in nt.split(",")]}); st.rerun()
        if st.button("Papierkorb", type="primary"): st.session_state.manager.soft_delete_project(pid); nav_to('dashboard')
        render_activity_log(p)

def render_presentation(pid):
    p = st.session_state.manager.get_project(pid)
    st.button("❌ Close", on_click=lambda: nav_to('details', pid))
    st.markdown(f'<div class="slide-title">{p["title"]}</div>', unsafe_allow_html=True)
    if p['images'] and os.path.exists(p['images'][0]): st.image(p['images'][0])
    k1, k2 = st.columns(2); k1.metric("Progress", f"{p['progress']}%"); k2.metric("Budget", f"{p['budget']['total']}€")
    render_gantt_view(p)

# --- RUN ---
render_sidebar()

# Original Views
if st.session_state.view == 'dashboard': render_dashboard()
elif st.session_state.view == 'create': render_create()
elif st.session_state.view == 'global': render_global_dashboard(st.session_state.manager)
elif st.session_state.view == 'details': render_details()
elif st.session_state.view == 'search': render_search_results()
elif st.session_state.view == 'trash': render_trash_bin()
elif st.session_state.view == 'presentation': render_presentation(st.session_state.selected_project_id)
elif st.session_state.view == 'lab': render_lab_dashboard(st.session_state.manager)
elif st.session_state.view == 'experiment_details': render_experiment_details(st.session_state.manager)
elif st.session_state.view == 'experiment_templates': render_experiment_template_library(st.session_state.manager)
elif st.session_state.view == 'create_from_experiment_template': render_create_from_experiment_template(st.session_state.manager)

# NEW v2.1 Views - 10 Amazing Features!
elif st.session_state.view == 'my_dashboard': render_custom_dashboard(st.session_state.manager, st.session_state.auth.current_user_name())
elif st.session_state.view == 'analytics': render_analytics_dashboard(st.session_state.manager)
elif st.session_state.view == 'export_import': render_export_import_center(st.session_state.manager)
elif st.session_state.view == 'notifications': render_notification_center(st.session_state.manager, st.session_state.auth.current_user_name())
elif st.session_state.view == 'template_library': render_template_library(st.session_state.manager)
elif st.session_state.view == 'template_create':
    if 'selected_template' in st.session_state:
        render_template_creation(st.session_state.manager, st.session_state['selected_template'])
elif st.session_state.view == 'timesheet': render_timesheet_manager(st.session_state.manager, st.session_state.auth.current_user_name())
elif st.session_state.view == 'advanced_search': render_advanced_search(st.session_state.manager)
elif st.session_state.view == 'sprints': render_sprint_management(st.session_state.manager)
elif st.session_state.view == 'automation': render_automation_center(st.session_state.manager)
elif st.session_state.view == 'theme_settings': render_theme_settings()

# NEW v2.2 Views - 5 Game-Changing Features!
elif st.session_state.view == 'achievements': render_achievement_center(st.session_state.manager, st.session_state.auth.current_user_name())
elif st.session_state.view == 'invoices': render_invoice_generator(st.session_state.manager)
elif st.session_state.view == 'resources': render_resource_manager(st.session_state.manager)
elif st.session_state.view == 'gantt_chart': render_gantt_chart_view(st.session_state.manager)
elif st.session_state.view == 'comment_notifications': render_comment_notifications(st.session_state.auth.current_user_name())

# NEW v2.3 Views - 4 Advanced Features!
elif st.session_state.view == 'mind_map': render_mind_map_view(st.session_state.manager)
elif st.session_state.view == 'version_control': render_version_control(st.session_state.manager, st.session_state.auth.current_user_name())
elif st.session_state.view == 'dependencies': render_dependency_manager(st.session_state.manager)
elif st.session_state.view == 'calendar_export': render_calendar_export(st.session_state.manager)

# NEW v2.3.1 Views - Overview Dashboard!
elif st.session_state.view == 'overview': render_overview_dashboard(st.session_state.manager)

# Default fallback
else: render_dashboard()

# Footer with version info
st.sidebar.markdown("---")
st.sidebar.caption("v2.3 - 19 Amazing Features!")
st.sidebar.caption("Made with ❤️ by PM Team")