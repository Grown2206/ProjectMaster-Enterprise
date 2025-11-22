"""
Gantt Chart Visualization Module
Project timeline and task visualization with Gantt charts
"""

import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict


class GanttChartGenerator:
    """Generate Gantt charts for projects"""

    @staticmethod
    def calculate_task_dates(project: Dict) -> List[Dict]:
        """Calculate start and end dates for tasks"""
        tasks_with_dates = []

        project_start = project.get('created_at', datetime.now().strftime("%Y-%m-%d"))
        project_deadline = project.get('deadline', (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"))

        try:
            start_date = datetime.strptime(project_start, "%Y-%m-%d")
        except:
            start_date = datetime.now()

        try:
            end_date = datetime.strptime(project_deadline, "%Y-%m-%d")
        except:
            end_date = start_date + timedelta(days=90)

        tasks = project.get('tasks', [])

        if not tasks:
            return []

        # Calculate duration per task
        total_days = (end_date - start_date).days
        days_per_task = max(1, total_days // len(tasks))

        current_start = start_date

        for idx, task in enumerate(tasks):
            # Calculate task duration based on status
            if task.get('status') == 'Done':
                # Completed tasks get shorter duration
                duration = days_per_task * 0.8
            elif task.get('status') == 'In Progress':
                duration = days_per_task
            else:
                duration = days_per_task * 1.2

            task_end = current_start + timedelta(days=duration)

            # Ensure we don't exceed project deadline
            if task_end > end_date:
                task_end = end_date

            tasks_with_dates.append({
                'Task': task.get('text', f'Task {idx+1}'),
                'Start': current_start.strftime("%Y-%m-%d"),
                'End': task_end.strftime("%Y-%m-%d"),
                'Status': task.get('status', 'To Do'),
                'Assignee': task.get('assignee', 'Unassigned'),
                'Priority': task.get('priority', 'Medium')
            })

            current_start = task_end

        return tasks_with_dates

    @staticmethod
    def calculate_milestone_dates(project: Dict) -> List[Dict]:
        """Calculate dates for milestones"""
        milestones_with_dates = []

        project_start = project.get('created_at', datetime.now().strftime("%Y-%m-%d"))
        project_deadline = project.get('deadline', (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"))

        try:
            start_date = datetime.strptime(project_start, "%Y-%m-%d")
        except:
            start_date = datetime.now()

        try:
            end_date = datetime.strptime(project_deadline, "%Y-%m-%d")
        except:
            end_date = start_date + timedelta(days=90)

        milestones = project.get('milestones', [])

        if not milestones:
            return []

        total_days = (end_date - start_date).days
        days_per_milestone = max(1, total_days // len(milestones))

        current_date = start_date

        for milestone in milestones:
            # If milestone has a specific date, use it
            if milestone.get('date'):
                try:
                    milestone_date = datetime.strptime(milestone['date'], "%Y-%m-%d")
                except:
                    milestone_date = current_date
            else:
                milestone_date = current_date

            milestones_with_dates.append({
                'Milestone': milestone.get('title', 'Milestone'),
                'Date': milestone_date.strftime("%Y-%m-%d"),
                'Done': milestone.get('done', False)
            })

            current_date += timedelta(days=days_per_milestone)

        return milestones_with_dates


def render_gantt_chart_view(manager):
    """Render Gantt chart visualization"""
    st.title("📊 Gantt Chart View")

    st.markdown("""
    Visualisiere deine Projekte als Gantt-Chart mit Timeline,
    Tasks, Milestones und Abhängigkeiten.
    """)

    # Project selection
    active_projects = [p for p in manager.projects if not p.get('is_deleted') and not p.get('is_archived')]

    if not active_projects:
        st.info("Keine aktiven Projekte vorhanden")
        return

    tabs = st.tabs(["📊 Einzel-Projekt", "🌍 Portfolio View", "⚙️ Optionen"])

    # Tab 1: Single Project Gantt
    with tabs[0]:
        render_single_project_gantt(manager, active_projects)

    # Tab 2: Portfolio Gantt (all projects)
    with tabs[1]:
        render_portfolio_gantt(manager, active_projects)

    # Tab 3: Options
    with tabs[2]:
        render_gantt_options()


def render_single_project_gantt(manager, active_projects):
    """Render Gantt chart for a single project"""
    st.subheader("📊 Projekt-Gantt-Chart")

    # Project selector
    project_options = {p['title']: p['id'] for p in active_projects}
    selected_project_name = st.selectbox("Projekt auswählen", list(project_options.keys()))
    project_id = project_options[selected_project_name]

    project = manager.get_project(project_id)

    if not project:
        st.error("Projekt nicht gefunden")
        return

    # Display options
    col1, col2, col3 = st.columns(3)

    show_tasks = col1.checkbox("📝 Tasks anzeigen", value=True)
    show_milestones = col2.checkbox("🎯 Milestones anzeigen", value=True)
    color_by = col3.selectbox("Färbung nach", ["Status", "Assignee", "Priority"])

    # Generate Gantt data
    gantt_data = []

    if show_tasks:
        tasks_with_dates = GanttChartGenerator.calculate_task_dates(project)

        for task_data in tasks_with_dates:
            gantt_data.append({
                'Item': task_data['Task'],
                'Start': task_data['Start'],
                'End': task_data['End'],
                'Type': 'Task',
                'Status': task_data['Status'],
                'Assignee': task_data['Assignee'],
                'Priority': task_data['Priority'],
                'Color_By': task_data[color_by] if color_by in task_data else 'N/A'
            })

    if show_milestones:
        milestones_with_dates = GanttChartGenerator.calculate_milestone_dates(project)

        for milestone_data in milestones_with_dates:
            # Milestones are shown as single-day events
            gantt_data.append({
                'Item': f"🎯 {milestone_data['Milestone']}",
                'Start': milestone_data['Date'],
                'End': milestone_data['Date'],
                'Type': 'Milestone',
                'Status': 'Done' if milestone_data['Done'] else 'Pending',
                'Assignee': 'N/A',
                'Priority': 'High',
                'Color_By': 'Done' if milestone_data['Done'] else 'Pending'
            })

    if not gantt_data:
        st.info("Keine Tasks oder Milestones für Gantt-Chart vorhanden")
        return

    # Create DataFrame
    df = pd.DataFrame(gantt_data)
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])

    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start='Start',
        x_end='End',
        y='Item',
        color='Color_By',
        title=f"Gantt Chart: {project['title']}",
        labels={'Color_By': color_by},
        hover_data=['Type', 'Status', 'Assignee']
    )

    # Customize layout
    fig.update_yaxes(categoryorder='total ascending')
    fig.update_layout(
        height=max(400, len(df) * 40),
        xaxis_title="Timeline",
        yaxis_title="Tasks & Milestones"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Project statistics
    st.divider()
    st.markdown("### 📈 Projekt-Statistiken")

    col1, col2, col3, col4 = st.columns(4)

    tasks = project.get('tasks', [])
    completed_tasks = len([t for t in tasks if t.get('status') == 'Done'])

    milestones = project.get('milestones', [])
    completed_milestones = len([m for m in milestones if m.get('done')])

    col1.metric("Gesamt Tasks", len(tasks))
    col2.metric("Erledigt", completed_tasks)
    col3.metric("Gesamt Milestones", len(milestones))
    col4.metric("Erreicht", completed_milestones)

    # Progress bar
    if tasks:
        progress = (completed_tasks / len(tasks)) * 100
        st.markdown(f"**Fortschritt:** {progress:.0f}%")
        st.progress(progress / 100)

    # Critical path analysis
    st.divider()
    st.markdown("### 🎯 Critical Path Analyse")

    # Calculate critical path (simplified)
    if tasks_with_dates:
        # Find longest task chain
        total_duration = 0
        critical_tasks = []

        for task_data in tasks_with_dates:
            start = datetime.strptime(task_data['Start'], "%Y-%m-%d")
            end = datetime.strptime(task_data['End'], "%Y-%m-%d")
            duration = (end - start).days

            if task_data['Status'] != 'Done':
                total_duration += duration
                critical_tasks.append(task_data['Task'])

        col1, col2 = st.columns(2)

        col1.metric("Verbleibende Dauer", f"{total_duration} Tage")
        col2.metric("Kritische Tasks", len(critical_tasks))

        if critical_tasks:
            with st.expander("🔍 Kritische Tasks ansehen"):
                for task in critical_tasks:
                    st.write(f"• {task}")


def render_portfolio_gantt(manager, active_projects):
    """Render Gantt chart for all projects (portfolio view)"""
    st.subheader("🌍 Portfolio Gantt Chart")

    st.info("Zeigt alle aktiven Projekte in einer Timeline-Ansicht")

    # Filter options
    col1, col2 = st.columns(2)

    category_filter = col1.multiselect(
        "Kategorie Filter",
        list(set([p.get('category', 'Sonstiges') for p in active_projects])),
        default=list(set([p.get('category', 'Sonstiges') for p in active_projects]))
    )

    status_filter = col2.multiselect(
        "Status Filter",
        ['Idee', 'Planung', 'In Arbeit', 'Review', 'Abgeschlossen'],
        default=['Planung', 'In Arbeit', 'Review']
    )

    # Filter projects
    filtered_projects = [
        p for p in active_projects
        if p.get('category', 'Sonstiges') in category_filter and p.get('status', 'Planung') in status_filter
    ]

    if not filtered_projects:
        st.info("Keine Projekte entsprechen den Filterkriterien")
        return

    # Generate portfolio Gantt data
    portfolio_data = []

    for project in filtered_projects:
        # Get project dates
        start_date = project.get('created_at', datetime.now().strftime("%Y-%m-%d"))
        end_date = project.get('deadline', (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"))

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except:
            start = datetime.now()

        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            end = start + timedelta(days=90)

        portfolio_data.append({
            'Project': project['title'],
            'Start': start.strftime("%Y-%m-%d"),
            'End': end.strftime("%Y-%m-%d"),
            'Status': project.get('status', 'Planung'),
            'Category': project.get('category', 'Sonstiges'),
            'Priority': project.get('priority', 'Med'),
            'Progress': project.get('progress', 0)
        })

    # Create DataFrame
    df = pd.DataFrame(portfolio_data)
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])

    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start='Start',
        x_end='End',
        y='Project',
        color='Status',
        title='Portfolio Timeline',
        hover_data=['Category', 'Priority', 'Progress']
    )

    # Customize layout
    fig.update_yaxes(categoryorder='total ascending')
    fig.update_layout(
        height=max(500, len(df) * 50),
        xaxis_title="Timeline",
        yaxis_title="Projekte"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Portfolio statistics
    st.divider()
    st.markdown("### 📊 Portfolio-Statistiken")

    col1, col2, col3, col4 = st.columns(4)

    total_projects = len(filtered_projects)
    avg_progress = sum(p.get('progress', 0) for p in filtered_projects) / total_projects if total_projects > 0 else 0

    # Calculate time metrics
    all_start_dates = []
    all_end_dates = []

    for project in filtered_projects:
        try:
            all_start_dates.append(datetime.strptime(project.get('created_at', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
        except:
            pass

        try:
            all_end_dates.append(datetime.strptime(project.get('deadline', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"))
        except:
            pass

    if all_start_dates and all_end_dates:
        portfolio_start = min(all_start_dates)
        portfolio_end = max(all_end_dates)
        portfolio_duration = (portfolio_end - portfolio_start).days
    else:
        portfolio_duration = 0

    col1.metric("Projekte", total_projects)
    col2.metric("Ø Fortschritt", f"{avg_progress:.0f}%")
    col3.metric("Portfolio-Dauer", f"{portfolio_duration} Tage")

    # Count overdue projects
    today = datetime.now()
    overdue = sum(1 for d in all_end_dates if d < today)
    col4.metric("Überfällig", overdue)


def render_gantt_options():
    """Render Gantt chart options and settings"""
    st.subheader("⚙️ Gantt Chart Optionen")

    st.markdown("### 🎨 Anzeigeoptionen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Chart-Stil:**")
        chart_style = st.radio(
            "Stil",
            ["Modern", "Klassisch", "Minimalistisch"],
            label_visibility="collapsed"
        )

        st.markdown("**Zeitskala:**")
        time_scale = st.radio(
            "Skala",
            ["Tage", "Wochen", "Monate"],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("**Farb-Schema:**")
        color_scheme = st.selectbox(
            "Schema",
            ["Default", "Pastell", "Dunkel", "Kontrastreich"],
            label_visibility="collapsed"
        )

        st.markdown("**Grid-Linien:**")
        show_grid = st.checkbox("Grid anzeigen", value=True)

    st.divider()

    st.markdown("### 📤 Export-Optionen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export-Format:**")
        export_format = st.selectbox(
            "Format",
            ["PNG", "SVG", "PDF", "Excel"],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("**Auflösung:**")
        resolution = st.selectbox(
            "Auflösung",
            ["Standard (72 DPI)", "Hoch (150 DPI)", "Druck (300 DPI)"],
            label_visibility="collapsed"
        )

    if st.button("📥 Gantt Chart exportieren", type="primary", use_container_width=True):
        st.success(f"✅ Chart als {export_format} exportiert! (Feature in Entwicklung)")

    st.divider()

    st.markdown("### ℹ️ Über Gantt Charts")

    st.info("""
    **Gantt Charts** sind ein mächtiges Tool für Projektplanung:

    ✅ **Vorteile:**
    - Visualisiert Projekt-Timeline
    - Zeigt Task-Abhängigkeiten
    - Identifiziert kritischen Pfad
    - Erkennt Ressourcen-Konflikte
    - Überwacht Projekt-Fortschritt

    📊 **Verwendung:**
    - Wähle ein Projekt oder Portfolio-Ansicht
    - Aktiviere Tasks und/oder Milestones
    - Wähle Färbung nach Status, Assignee oder Priorität
    - Analysiere kritische Pfade und Engpässe
    """)


def render_gantt_legend():
    """Render Gantt chart legend"""
    st.markdown("### 📖 Legende")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Status:**")
        st.markdown("🟢 Done")
        st.markdown("🟡 In Progress")
        st.markdown("⚪ To Do")

    with col2:
        st.markdown("**Priorität:**")
        st.markdown("🔴 Critical")
        st.markdown("🟠 High")
        st.markdown("🟢 Med/Low")

    with col3:
        st.markdown("**Typ:**")
        st.markdown("📝 Task")
        st.markdown("🎯 Milestone")
        st.markdown("📦 Phase")
