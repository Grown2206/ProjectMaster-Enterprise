"""
Dashboard Widgets Module
Customizable dashboard with widgets
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_custom_dashboard(manager, user_name: str):
    """Render customizable dashboard with widgets"""
    st.title("📊 My Dashboard")

    # Widget configuration in session state
    if 'dashboard_widgets' not in st.session_state:
        st.session_state.dashboard_widgets = [
            'my_tasks',
            'project_health',
            'time_summary',
            'budget_overview'
        ]

    # Widget customization sidebar
    with st.sidebar.expander("⚙️ Dashboard konfigurieren"):
        available_widgets = {
            'my_tasks': '✅ Meine Aufgaben',
            'project_health': '💚 Projekt-Gesundheit',
            'time_summary': '⏱️ Zeit-Übersicht',
            'budget_overview': '💰 Budget-Übersicht',
            'recent_activity': '📰 Letzte Aktivitäten',
            'deadlines': '⏰ Anstehende Deadlines',
            'team_workload': '👥 Team-Auslastung',
            'quick_stats': '📈 Schnellstatistiken'
        }

        selected_widgets = st.multiselect(
            "Widgets auswählen",
            list(available_widgets.keys()),
            default=st.session_state.dashboard_widgets,
            format_func=lambda x: available_widgets[x]
        )

        if st.button("💾 Dashboard speichern"):
            st.session_state.dashboard_widgets = selected_widgets
            st.success("Dashboard aktualisiert!")
            st.rerun()

    # Render selected widgets
    render_widgets(manager, user_name, st.session_state.dashboard_widgets)


def render_widgets(manager, user_name, widgets):
    """Render dashboard widgets"""
    # 2-column layout for widgets
    col_left, col_right = st.columns(2)

    widget_index = 0

    for widget_id in widgets:
        # Alternate between columns
        col = col_left if widget_index % 2 == 0 else col_right

        with col:
            if widget_id == 'my_tasks':
                render_my_tasks_widget(manager, user_name)
            elif widget_id == 'project_health':
                render_project_health_widget(manager)
            elif widget_id == 'time_summary':
                render_time_summary_widget(manager)
            elif widget_id == 'budget_overview':
                render_budget_overview_widget(manager)
            elif widget_id == 'recent_activity':
                render_recent_activity_widget(manager)
            elif widget_id == 'deadlines':
                render_deadlines_widget(manager)
            elif widget_id == 'team_workload':
                render_team_workload_widget(manager)
            elif widget_id == 'quick_stats':
                render_quick_stats_widget(manager)

        widget_index += 1


def render_my_tasks_widget(manager, user_name):
    """My tasks widget"""
    with st.container():
        st.markdown("### ✅ Meine Aufgaben")

        my_tasks = []
        for p in manager.projects:
            if not p.get('is_deleted'):
                for t in p.get('tasks', []):
                    if t.get('assignee') == user_name and t['status'] != 'Done':
                        my_tasks.append((t, p))

        if my_tasks:
            for task, project in my_tasks[:5]:
                col1, col2 = st.columns([4, 1])
                col1.write(f"• {task['text'][:40]}...")
                col1.caption(project['title'])

                if col2.button("✓", key=f"widget_task_{task['id']}"):
                    manager.update_task_status(project['id'], task['id'], 'Done')
                    st.rerun()

            st.caption(f"{len(my_tasks)} offene Aufgaben")
        else:
            st.success("🎉 Keine offenen Aufgaben!")

        st.divider()


def render_project_health_widget(manager):
    """Project health widget"""
    with st.container():
        st.markdown("### 💚 Projekt-Gesundheit")

        projects = [p for p in manager.projects if not p.get('is_deleted') and not p.get('is_archived')]

        health_counts = {'Gesund': 0, 'Gefährdet': 0, 'Kritisch': 0}

        for p in projects:
            health, _ = manager.calculate_health(p['id'])
            health_counts[health] = health_counts.get(health, 0) + 1

        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(health_counts.keys()),
            values=list(health_counts.values()),
            marker=dict(colors=['#00cc99', '#ffa500', '#ff4b4b']),
            hole=0.4
        )])

        fig.update_layout(
            height=250,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"{len(projects)} aktive Projekte")
        st.divider()


def render_time_summary_widget(manager):
    """Time summary widget"""
    with st.container():
        st.markdown("### ⏱️ Zeit diese Woche")

        from datetime import datetime, timedelta

        # Get this week's time logs
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())

        total_hours = 0

        for p in manager.projects:
            for log in p.get('time_logs', []):
                try:
                    log_date = datetime.strptime(log.get('date', ''), "%Y-%m-%d")
                    if log_date >= start_of_week:
                        total_hours += log.get('hours', 0)
                except:
                    pass

        # Progress bar towards 40h goal
        st.metric("Erfasste Stunden", f"{total_hours:.1f}h")
        st.progress(min(total_hours / 40, 1.0))

        st.caption(f"Ziel: 40h/Woche ({(total_hours/40*100):.0f}%)")
        st.divider()


def render_budget_overview_widget(manager):
    """Budget overview widget"""
    with st.container():
        st.markdown("### 💰 Budget-Übersicht")

        projects = [p for p in manager.projects if not p.get('is_deleted')]

        total_budget = sum(p.get('budget', {}).get('total', 0) for p in projects)
        total_spent = sum(
            sum(e.get('amount', 0) for e in p.get('budget', {}).get('expenses', []))
            for p in projects
        )

        col1, col2 = st.columns(2)
        col1.metric("Budget", f"€{total_budget:,.0f}")
        col2.metric("Ausgaben", f"€{total_spent:,.0f}")

        if total_budget > 0:
            usage = total_spent / total_budget
            st.progress(min(usage, 1.0))

            if usage > 1.0:
                st.error(f"⚠️ {(usage-1)*100:.1f}% Überbudget!")
            else:
                st.caption(f"{usage*100:.1f}% genutzt")

        st.divider()


def render_recent_activity_widget(manager):
    """Recent activity widget"""
    with st.container():
        st.markdown("### 📰 Letzte Aktivitäten")

        all_activities = []
        for p in manager.projects:
            if not p.get('is_deleted'):
                for activity in p.get('activity_log', [])[:3]:
                    all_activities.append(activity)

        all_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        for activity in all_activities[:5]:
            st.caption(f"{activity.get('timestamp', 'N/A')}")
            st.write(f"• {activity.get('action', 'N/A')}")

        st.divider()


def render_deadlines_widget(manager):
    """Upcoming deadlines widget"""
    with st.container():
        st.markdown("### ⏰ Anstehende Deadlines")

        from datetime import datetime

        deadlines = []

        for p in manager.projects:
            if not p.get('is_deleted') and not p.get('is_archived'):
                if p.get('deadline'):
                    try:
                        deadline_date = datetime.strptime(p['deadline'], "%Y-%m-%d")
                        days_left = (deadline_date - datetime.now()).days

                        deadlines.append({
                            'project': p['title'],
                            'date': p['deadline'],
                            'days': days_left
                        })
                    except:
                        pass

        deadlines.sort(key=lambda x: x['days'])

        if deadlines:
            for dl in deadlines[:5]:
                icon = "🚨" if dl['days'] < 0 else "⏰" if dl['days'] <= 3 else "📅"
                st.write(f"{icon} {dl['project']}")
                st.caption(f"{dl['date']} ({dl['days']} Tage)")
        else:
            st.info("Keine anstehenden Deadlines")

        st.divider()


def render_team_workload_widget(manager):
    """Team workload widget"""
    with st.container():
        st.markdown("### 👥 Team-Auslastung")

        team_tasks = {}

        for p in manager.projects:
            if not p.get('is_deleted'):
                for task in p.get('tasks', []):
                    assignee = task.get('assignee', 'Unassigned')
                    if assignee != 'Unassigned':
                        team_tasks[assignee] = team_tasks.get(assignee, 0) + (1 if task['status'] != 'Done' else 0)

        if team_tasks:
            for name, count in sorted(team_tasks.items(), key=lambda x: x[1], reverse=True)[:5]:
                col1, col2 = st.columns([3, 1])
                col1.write(name)
                col2.write(f"{count} Tasks")
        else:
            st.info("Keine Aufgaben zugewiesen")

        st.divider()


def render_quick_stats_widget(manager):
    """Quick statistics widget"""
    with st.container():
        st.markdown("### 📈 Schnellstatistiken")

        projects = [p for p in manager.projects if not p.get('is_deleted')]

        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') in ['In Arbeit', 'Planung']])
        completed_projects = len([p for p in projects if p.get('status') == 'Abgeschlossen'])

        col1, col2 = st.columns(2)

        col1.metric("Gesamt", total_projects)
        col1.metric("Aktiv", active_projects)

        col2.metric("Fertig", completed_projects)

        if total_projects > 0:
            col2.metric("Success Rate", f"{(completed_projects/total_projects*100):.0f}%")

        st.divider()
