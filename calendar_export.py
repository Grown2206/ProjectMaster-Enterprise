"""
Calendar Export Module
Export projects, tasks, and deadlines to iCal format
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict


class iCalGenerator:
    """Generate iCal/ICS files"""

    @staticmethod
    def generate_ical(events: List[Dict]) -> str:
        """Generate iCal file content"""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Project Master Enterprise//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Project Master Calendar",
            "X-WR-TIMEZONE:Europe/Berlin",
            "X-WR-CALDESC:Exported from Project Master Enterprise"
        ]

        for event in events:
            lines.extend(iCalGenerator._create_event(event))

        lines.append("END:VCALENDAR")

        return "\r\n".join(lines)

    @staticmethod
    def _create_event(event: Dict) -> List[str]:
        """Create VEVENT block"""
        lines = ["BEGIN:VEVENT"]

        # UID (required)
        uid = event.get('uid', f"{event['title']}-{event.get('start', '')}@projectmaster.local")
        lines.append(f"UID:{uid}")

        # DTSTAMP (required)
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        lines.append(f"DTSTAMP:{dtstamp}")

        # DTSTART (required)
        if event.get('start'):
            try:
                start_date = datetime.strptime(event['start'], "%Y-%m-%d")
                lines.append(f"DTSTART;VALUE=DATE:{start_date.strftime('%Y%m%d')}")
            except:
                pass

        # DTEND (optional)
        if event.get('end'):
            try:
                end_date = datetime.strptime(event['end'], "%Y-%m-%d")
                # Add 1 day for all-day events
                end_date += timedelta(days=1)
                lines.append(f"DTEND;VALUE=DATE:{end_date.strftime('%Y%m%d')}")
            except:
                pass

        # SUMMARY (required)
        summary = event.get('title', 'Unnamed Event')
        lines.append(f"SUMMARY:{iCalGenerator._escape_text(summary)}")

        # DESCRIPTION (optional)
        if event.get('description'):
            desc = iCalGenerator._escape_text(event['description'])
            lines.append(f"DESCRIPTION:{desc}")

        # LOCATION (optional)
        if event.get('location'):
            lines.append(f"LOCATION:{iCalGenerator._escape_text(event['location'])}")

        # STATUS (optional)
        status = event.get('status', 'TENTATIVE').upper()
        if status in ['TENTATIVE', 'CONFIRMED', 'CANCELLED']:
            lines.append(f"STATUS:{status}")

        # PRIORITY (optional)
        priority_map = {
            'Critical': '1',
            'High': '3',
            'Med': '5',
            'Low': '7'
        }
        if event.get('priority'):
            priority = priority_map.get(event['priority'], '5')
            lines.append(f"PRIORITY:{priority}")

        # CATEGORIES (optional)
        if event.get('categories'):
            categories = ','.join(event['categories'])
            lines.append(f"CATEGORIES:{categories}")

        # ALARM (optional)
        if event.get('alarm'):
            lines.extend([
                "BEGIN:VALARM",
                "TRIGGER:-PT24H",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: {iCalGenerator._escape_text(summary)}",
                "END:VALARM"
            ])

        lines.append("END:VEVENT")

        return lines

    @staticmethod
    def _escape_text(text: str) -> str:
        """Escape special characters for iCal"""
        # Replace special chars
        text = text.replace('\\', '\\\\')
        text = text.replace(',', '\\,')
        text = text.replace(';', '\\;')
        text = text.replace('\n', '\\n')

        return text


def render_calendar_export(manager):
    """Render calendar export interface"""
    st.title("📅 Calendar Export")

    st.markdown("""
    Exportiere Projekte, Tasks und Deadlines in iCal-Format (.ics)
    für Google Calendar, Outlook, Apple Calendar, etc.
    """)

    tabs = st.tabs(["📅 Export Projekte", "✅ Export Tasks", "🎯 Export Milestones"])

    # Tab 1: Export Projects
    with tabs[0]:
        st.subheader("📅 Projekt-Deadlines exportieren")

        # Filter projects
        active_projects = [p for p in manager.projects if not p.get('is_deleted') and p.get('deadline')]

        if not active_projects:
            st.info("Keine Projekte mit Deadlines vorhanden")
        else:
            st.write(f"**{len(active_projects)} Projekt(e)** mit Deadlines gefunden")

            # Options
            col1, col2 = st.columns(2)

            with col1:
                include_alarm = st.checkbox("📢 24h Erinnerung", value=True)

            with col2:
                status_filter = st.multiselect(
                    "Status Filter",
                    ['Idee', 'Planung', 'In Arbeit', 'Review', 'Abgeschlossen'],
                    default=['Planung', 'In Arbeit', 'Review']
                )

            # Filter by status
            filtered_projects = [p for p in active_projects if p.get('status', 'Idee') in status_filter]

            st.write(f"**{len(filtered_projects)} Projekt(e)** werden exportiert")

            # Preview
            if filtered_projects:
                st.markdown("#### 📋 Vorschau")

                for project in filtered_projects[:5]:
                    deadline = project.get('deadline', 'N/A')
                    priority = project.get('priority', 'Med')

                    priority_icon = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Med': '🟡',
                        'Low': '🟢'
                    }.get(priority, '⚪')

                    st.write(f"{priority_icon} {project['title']} - Deadline: {deadline}")

                if len(filtered_projects) > 5:
                    st.caption(f"... und {len(filtered_projects) - 5} weitere")

            # Generate iCal
            if st.button("📥 iCal generieren", type="primary"):
                events = []

                for project in filtered_projects:
                    event = {
                        'uid': f"project-{project['id']}@projectmaster.local",
                        'title': f"[Projekt] {project['title']}",
                        'description': project.get('description', ''),
                        'start': project.get('deadline'),
                        'end': project.get('deadline'),
                        'status': 'TENTATIVE' if project.get('status') in ['Idee', 'Planung'] else 'CONFIRMED',
                        'priority': project.get('priority', 'Med'),
                        'categories': [project.get('category', 'Sonstiges'), 'Projekt'],
                        'alarm': include_alarm
                    }

                    events.append(event)

                ical_content = iCalGenerator.generate_ical(events)

                st.download_button(
                    label="💾 Download .ics Datei",
                    data=ical_content,
                    file_name="projektmaster_projekte.ics",
                    mime="text/calendar"
                )

                st.success(f"✅ {len(events)} Event(s) generiert!")

    # Tab 2: Export Tasks
    with tabs[1]:
        st.subheader("✅ Tasks exportieren")

        # Project selection
        all_projects = [p for p in manager.projects if not p.get('is_deleted')]

        if not all_projects:
            st.info("Keine Projekte vorhanden")
        else:
            project_options = {p['title']: p['id'] for p in all_projects}
            selected_projects = st.multiselect(
                "Projekte auswählen",
                list(project_options.keys()),
                default=list(project_options.keys())[:3]
            )

            # Collect tasks
            all_tasks = []

            for project_name in selected_projects:
                project_id = project_options[project_name]
                project = manager.get_project(project_id)

                if project:
                    tasks = project.get('tasks', [])

                    for task in tasks:
                        all_tasks.append({
                            'project': project['title'],
                            'task': task,
                            'project_id': project_id
                        })

            if not all_tasks:
                st.info("Keine Tasks gefunden")
            else:
                st.write(f"**{len(all_tasks)} Task(s)** gefunden")

                # Options
                include_alarm = st.checkbox("📢 24h Erinnerung", value=True, key="tasks_alarm")

                status_filter = st.multiselect(
                    "Status Filter",
                    ['To Do', 'In Progress', 'Done', 'Blocked'],
                    default=['To Do', 'In Progress'],
                    key="tasks_status"
                )

                # Filter
                filtered_tasks = [
                    t for t in all_tasks
                    if t['task'].get('status', 'To Do') in status_filter
                ]

                st.write(f"**{len(filtered_tasks)} Task(s)** werden exportiert")

                # Generate iCal
                if st.button("📥 iCal generieren", type="primary", key="gen_tasks"):
                    events = []

                    # Use project deadline or today + 7 days as default
                    default_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

                    for item in filtered_tasks:
                        task = item['task']
                        project_title = item['project']

                        # Try to get project deadline
                        project = manager.get_project(item['project_id'])
                        deadline = project.get('deadline', default_date) if project else default_date

                        event = {
                            'uid': f"task-{item['project_id']}-{task.get('text', '')}@projectmaster.local",
                            'title': f"[Task] {task.get('text', 'Unnamed Task')}",
                            'description': f"Projekt: {project_title}\nStatus: {task.get('status', 'To Do')}",
                            'start': deadline,
                            'end': deadline,
                            'status': 'CONFIRMED' if task.get('status') == 'In Progress' else 'TENTATIVE',
                            'categories': ['Task', project_title],
                            'alarm': include_alarm
                        }

                        events.append(event)

                    ical_content = iCalGenerator.generate_ical(events)

                    st.download_button(
                        label="💾 Download .ics Datei",
                        data=ical_content,
                        file_name="projektmaster_tasks.ics",
                        mime="text/calendar"
                    )

                    st.success(f"✅ {len(events)} Event(s) generiert!")

    # Tab 3: Export Milestones
    with tabs[2]:
        st.subheader("🎯 Milestones exportieren")

        # Collect milestones from all projects
        all_milestones = []

        for project in manager.projects:
            if project.get('is_deleted'):
                continue

            milestones = project.get('milestones', [])

            for milestone in milestones:
                all_milestones.append({
                    'project': project['title'],
                    'milestone': milestone,
                    'project_id': project['id']
                })

        if not all_milestones:
            st.info("Keine Milestones definiert")
        else:
            st.write(f"**{len(all_milestones)} Milestone(s)** gefunden")

            # Options
            include_alarm = st.checkbox("📢 24h Erinnerung", value=True, key="milestones_alarm")

            only_pending = st.checkbox("Nur ausstehende Milestones", value=True)

            # Filter
            filtered_milestones = all_milestones

            if only_pending:
                filtered_milestones = [m for m in all_milestones if not m['milestone'].get('done', False)]

            st.write(f"**{len(filtered_milestones)} Milestone(s)** werden exportiert")

            # Generate iCal
            if st.button("📥 iCal generieren", type="primary", key="gen_milestones"):
                events = []

                for item in filtered_milestones:
                    milestone = item['milestone']
                    project_title = item['project']

                    # Get date or use project deadline
                    date = milestone.get('date')

                    if not date:
                        project = manager.get_project(item['project_id'])
                        date = project.get('deadline') if project else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

                    event = {
                        'uid': f"milestone-{item['project_id']}-{milestone.get('title', '')}@projectmaster.local",
                        'title': f"[Milestone] {milestone.get('title', 'Unnamed Milestone')}",
                        'description': f"Projekt: {project_title}",
                        'start': date,
                        'end': date,
                        'status': 'CONFIRMED',
                        'priority': 'High',
                        'categories': ['Milestone', project_title],
                        'alarm': include_alarm
                    }

                    events.append(event)

                ical_content = iCalGenerator.generate_ical(events)

                st.download_button(
                    label="💾 Download .ics Datei",
                    data=ical_content,
                    file_name="projektmaster_milestones.ics",
                    mime="text/calendar"
                )

                st.success(f"✅ {len(events)} Event(s) generiert!")


def generate_project_ical(project: Dict, include_tasks: bool = False, include_milestones: bool = True) -> str:
    """Generate iCal for a single project"""
    events = []

    # Add project deadline
    if project.get('deadline'):
        events.append({
            'uid': f"project-{project['id']}@projectmaster.local",
            'title': f"[Projekt] {project['title']}",
            'description': project.get('description', ''),
            'start': project['deadline'],
            'end': project['deadline'],
            'status': 'CONFIRMED',
            'priority': project.get('priority', 'Med'),
            'categories': [project.get('category', 'Sonstiges')],
            'alarm': True
        })

    # Add tasks
    if include_tasks:
        for task in project.get('tasks', []):
            if task.get('status') != 'Done':
                deadline = project.get('deadline', (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))

                events.append({
                    'uid': f"task-{project['id']}-{task.get('text', '')}@projectmaster.local",
                    'title': f"[Task] {task.get('text', 'Unnamed')}",
                    'description': f"Projekt: {project['title']}\nStatus: {task.get('status', 'To Do')}",
                    'start': deadline,
                    'end': deadline,
                    'status': 'TENTATIVE',
                    'categories': ['Task'],
                    'alarm': True
                })

    # Add milestones
    if include_milestones:
        for milestone in project.get('milestones', []):
            if not milestone.get('done'):
                date = milestone.get('date') or project.get('deadline')

                if date:
                    events.append({
                        'uid': f"milestone-{project['id']}-{milestone.get('title', '')}@projectmaster.local",
                        'title': f"[Milestone] {milestone.get('title', 'Unnamed')}",
                        'description': f"Projekt: {project['title']}",
                        'start': date,
                        'end': date,
                        'status': 'CONFIRMED',
                        'priority': 'High',
                        'categories': ['Milestone'],
                        'alarm': True
                    })

    return iCalGenerator.generate_ical(events)
