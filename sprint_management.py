"""
Sprint Management Module
Agile sprint planning and tracking
"""

import streamlit as st
from datetime import datetime, timedelta
import uuid


def render_sprint_management(manager):
    """Render sprint management interface"""
    st.title("⚡ Sprint Management")

    # Initialize sprints in session state if not exists
    if 'sprints' not in st.session_state:
        st.session_state.sprints = []

    tabs = st.tabs(["🏃 Active Sprints", "📋 Backlog", "➕ New Sprint", "📊 Sprint Analytics"])

    with tabs[0]:
        render_active_sprints(manager)

    with tabs[1]:
        render_sprint_backlog(manager)

    with tabs[2]:
        render_create_sprint(manager)

    with tabs[3]:
        render_sprint_analytics()


def render_active_sprints(manager):
    """Display active sprints"""
    st.subheader("🏃 Aktive Sprints")

    active_sprints = [s for s in st.session_state.sprints if s.get('status') == 'active']

    if not active_sprints:
        st.info("Keine aktiven Sprints. Erstelle einen neuen Sprint im Tab 'New Sprint'")
        return

    for sprint in active_sprints:
        render_sprint_card(sprint, manager)


def render_sprint_card(sprint, manager):
    """Render a sprint card"""
    with st.expander(f"⚡ {sprint['name']}", expanded=True):
        # Sprint info
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Dauer", f"{sprint['duration']} Tage")
        col2.metric("Story Points", sprint.get('total_points', 0))

        # Calculate progress
        completed_stories = len([s for s in sprint.get('stories', []) if s.get('status') == 'Done'])
        total_stories = len(sprint.get('stories', []))

        col3.metric("Fortschritt", f"{completed_stories}/{total_stories} Stories")

        # Days remaining
        end_date = datetime.strptime(sprint['end_date'], "%Y-%m-%d")
        days_left = (end_date - datetime.now()).days

        col4.metric("Verbleibend", f"{max(0, days_left)} Tage")

        # Progress bar
        progress = (completed_stories / total_stories * 100) if total_stories > 0 else 0
        st.progress(progress / 100)

        st.divider()

        # User stories
        st.markdown("#### 📝 User Stories")

        for story in sprint.get('stories', []):
            render_story_item(story, sprint)

        # Add story
        with st.form(f"add_story_{sprint['id']}"):
            col1, col2, col3 = st.columns([3, 1, 1])

            story_text = col1.text_input("User Story", placeholder="Als... möchte ich... damit...")
            points = col2.number_input("Points", min_value=1, max_value=13, value=3)

            if col3.form_submit_button("➕ Add"):
                sprint['stories'].append({
                    'id': str(uuid.uuid4()),
                    'text': story_text,
                    'points': points,
                    'status': 'To Do',
                    'assignee': None
                })
                st.rerun()

        # Sprint actions
        st.divider()

        col1, col2 = st.columns(2)

        if col1.button("✅ Sprint abschließen", key=f"complete_{sprint['id']}"):
            sprint['status'] = 'completed'
            sprint['completed_at'] = datetime.now().strftime("%Y-%m-%d")
            st.success("Sprint abgeschlossen!")
            st.rerun()

        if col2.button("🗑 Sprint löschen", key=f"delete_{sprint['id']}"):
            st.session_state.sprints.remove(sprint)
            st.rerun()


def render_story_item(story, sprint):
    """Render a user story item"""
    status_icons = {
        'To Do': '⚪',
        'In Progress': '🟡',
        'Done': '✅'
    }

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    col1.write(f"{status_icons.get(story['status'], '⚪')} {story['text']}")
    col2.write(f"{story['points']} pts")
    col3.write(story.get('assignee', 'Unassigned'))

    # Status change
    new_status = col4.selectbox(
        "Status",
        ['To Do', 'In Progress', 'Done'],
        index=['To Do', 'In Progress', 'Done'].index(story['status']),
        key=f"status_{story['id']}",
        label_visibility="collapsed"
    )

    if new_status != story['status']:
        story['status'] = new_status
        st.rerun()


def render_sprint_backlog(manager):
    """Display sprint backlog"""
    st.subheader("📋 Product Backlog")

    st.info("💡 Der Backlog enthält alle User Stories, die noch nicht in einem Sprint sind.")

    # Get all stories from projects' backlogs
    all_backlog_items = []

    for project in manager.projects:
        if not project.get('is_deleted'):
            for item in project.get('backlog', []):
                all_backlog_items.append({
                    **item,
                    'project': project['title'],
                    'project_id': project['id']
                })

    if not all_backlog_items:
        st.info("Backlog ist leer")
        return

    # Sort by priority
    priority_order = {'High': 0, 'Mid': 1, 'Low': 2}
    all_backlog_items.sort(key=lambda x: priority_order.get(x.get('priority', 'Mid'), 1))

    # Display items
    for item in all_backlog_items:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        priority_color = {'High': '🔴', 'Mid': '🟠', 'Low': '🟢'}[item.get('priority', 'Mid')]

        col1.write(f"{priority_color} {item['title']}")
        col2.write(item.get('project', 'N/A'))
        col3.write(item.get('priority', 'Mid'))

        if col4.button("→ Sprint", key=f"to_sprint_{item['title']}_{item.get('project_id', '')}"):
            st.info("Wähle einen aktiven Sprint im Tab 'Active Sprints' um Stories hinzuzufügen")


def render_create_sprint(manager):
    """Create new sprint"""
    st.subheader("➕ Neuen Sprint erstellen")

    with st.form("create_sprint"):
        sprint_name = st.text_input("Sprint Name", placeholder="z.B. Sprint 12 - Feature X")

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Startdatum", value=datetime.now())

        with col2:
            duration = st.number_input("Dauer (Tage)", min_value=1, max_value=30, value=14)

        goal = st.text_area("Sprint Ziel", placeholder="Was soll in diesem Sprint erreicht werden?")

        submitted = st.form_submit_button("🚀 Sprint starten", type="primary", use_container_width=True)

        if submitted:
            if not sprint_name:
                st.error("Bitte Sprint-Namen eingeben")
            else:
                end_date = start_date + timedelta(days=duration)

                new_sprint = {
                    'id': str(uuid.uuid4()),
                    'name': sprint_name,
                    'goal': goal,
                    'start_date': start_date.strftime("%Y-%m-%d"),
                    'end_date': end_date.strftime("%Y-%m-%d"),
                    'duration': duration,
                    'status': 'active',
                    'stories': [],
                    'total_points': 0,
                    'completed_points': 0
                }

                st.session_state.sprints.append(new_sprint)

                st.success(f"✅ Sprint '{sprint_name}' erstellt!")
                st.balloons()
                st.rerun()


def render_sprint_analytics():
    """Sprint analytics and metrics"""
    st.subheader("📊 Sprint Analytics")

    completed_sprints = [s for s in st.session_state.sprints if s.get('status') == 'completed']

    if not completed_sprints:
        st.info("Noch keine abgeschlossenen Sprints für Analytics")
        return

    # Velocity chart
    st.markdown("#### 📈 Team Velocity")

    velocity_data = []
    for sprint in completed_sprints[-10:]:  # Last 10 sprints
        completed_points = sum(s['points'] for s in sprint.get('stories', []) if s.get('status') == 'Done')
        velocity_data.append({
            'Sprint': sprint['name'],
            'Points': completed_points
        })

    import plotly.express as px
    import pandas as pd

    df = pd.DataFrame(velocity_data)

    fig = px.bar(df, x='Sprint', y='Points', color='Points', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

    # Average velocity
    avg_velocity = sum(d['Points'] for d in velocity_data) / len(velocity_data) if velocity_data else 0
    st.metric("Durchschnittliche Velocity", f"{avg_velocity:.1f} Points/Sprint")

    # Sprint statistics
    st.markdown("#### 📋 Sprint-Statistiken")

    for sprint in completed_sprints[-5:]:
        with st.expander(sprint['name']):
            col1, col2, col3 = st.columns(3)

            total_stories = len(sprint.get('stories', []))
            completed_stories = len([s for s in sprint.get('stories', []) if s.get('status') == 'Done'])
            completion_rate = (completed_stories / total_stories * 100) if total_stories > 0 else 0

            col1.metric("Stories", f"{completed_stories}/{total_stories}")
            col2.metric("Completion Rate", f"{completion_rate:.0f}%")
            col3.metric("Dauer", f"{sprint['duration']} Tage")
