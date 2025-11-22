"""
Export/Import Module
Support for CSV, Excel, and JSON exports/imports
"""

import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from typing import List, Dict


class DataExporter:
    """Export project data to various formats"""

    @staticmethod
    def export_projects_to_csv(projects: List[Dict]) -> str:
        """Export projects to CSV"""
        data = []
        for p in projects:
            data.append({
                'ID': p['id'],
                'Titel': p['title'],
                'Beschreibung': p['description'],
                'Kategorie': p.get('category', ''),
                'Priorität': p.get('priority', ''),
                'Status': p.get('status', ''),
                'Progress': p.get('progress', 0),
                'Budget': p.get('budget', {}).get('total', 0),
                'Deadline': p.get('deadline', ''),
                'Erstellt': p.get('created_at', ''),
                'Tags': ', '.join(p.get('tags', [])),
                'Tasks (Gesamt)': len(p.get('tasks', [])),
                'Tasks (Erledigt)': len([t for t in p.get('tasks', []) if t.get('status') == 'Done'])
            })

        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @staticmethod
    def export_tasks_to_csv(projects: List[Dict]) -> str:
        """Export all tasks to CSV"""
        data = []
        for p in projects:
            for task in p.get('tasks', []):
                data.append({
                    'Projekt': p['title'],
                    'Task': task['text'],
                    'Status': task['status'],
                    'Assignee': task.get('assignee', ''),
                    'Erstellt': task.get('created_at', ''),
                    'Kommentare': len(task.get('comments', []))
                })

        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @staticmethod
    def export_budget_to_csv(projects: List[Dict]) -> str:
        """Export budget and expenses to CSV"""
        data = []
        for p in projects:
            budget = p.get('budget', {})
            for expense in budget.get('expenses', []):
                data.append({
                    'Projekt': p['title'],
                    'Ausgabe': expense.get('title', ''),
                    'Betrag': expense.get('amount', 0),
                    'Kategorie': expense.get('category', ''),
                    'Datum': expense.get('date', '')
                })

        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @staticmethod
    def export_time_logs_to_csv(projects: List[Dict]) -> str:
        """Export time logs to CSV"""
        data = []
        for p in projects:
            for log in p.get('time_logs', []):
                data.append({
                    'Projekt': p['title'],
                    'Datum': log.get('date', ''),
                    'Kategorie': log.get('category', ''),
                    'Stunden': log.get('hours', 0),
                    'Beschreibung': log.get('desc', '')
                })

        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    @staticmethod
    def export_to_excel(projects: List[Dict]) -> bytes:
        """Export to Excel with multiple sheets"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Projects sheet
            projects_data = []
            for p in projects:
                projects_data.append({
                    'Titel': p['title'],
                    'Kategorie': p.get('category', ''),
                    'Status': p.get('status', ''),
                    'Progress': p.get('progress', 0),
                    'Budget': p.get('budget', {}).get('total', 0)
                })
            pd.DataFrame(projects_data).to_excel(writer, sheet_name='Projekte', index=False)

            # Tasks sheet
            tasks_data = []
            for p in projects:
                for task in p.get('tasks', []):
                    tasks_data.append({
                        'Projekt': p['title'],
                        'Task': task['text'],
                        'Status': task['status'],
                        'Assignee': task.get('assignee', '')
                    })
            pd.DataFrame(tasks_data).to_excel(writer, sheet_name='Tasks', index=False)

            # Budget sheet
            budget_data = []
            for p in projects:
                for expense in p.get('budget', {}).get('expenses', []):
                    budget_data.append({
                        'Projekt': p['title'],
                        'Ausgabe': expense.get('title', ''),
                        'Betrag': expense.get('amount', 0),
                        'Kategorie': expense.get('category', '')
                    })
            pd.DataFrame(budget_data).to_excel(writer, sheet_name='Budget', index=False)

        return output.getvalue()

    @staticmethod
    def export_to_json(projects: List[Dict]) -> str:
        """Export to JSON"""
        return json.dumps(projects, indent=2, ensure_ascii=False)


class DataImporter:
    """Import project data from various formats"""

    @staticmethod
    def import_tasks_from_csv(file) -> List[Dict]:
        """Import tasks from CSV"""
        try:
            df = pd.read_csv(file)
            tasks = []

            for _, row in df.iterrows():
                task = {
                    'text': row.get('Task', row.get('task', '')),
                    'status': row.get('Status', row.get('status', 'To Do')),
                    'assignee': row.get('Assignee', row.get('assignee', None))
                }
                tasks.append(task)

            return tasks
        except Exception as e:
            st.error(f"Import-Fehler: {str(e)}")
            return []

    @staticmethod
    def import_expenses_from_csv(file) -> List[Dict]:
        """Import expenses from CSV"""
        try:
            df = pd.read_csv(file)
            expenses = []

            for _, row in df.iterrows():
                expense = {
                    'title': row.get('Ausgabe', row.get('title', '')),
                    'amount': float(row.get('Betrag', row.get('amount', 0))),
                    'category': row.get('Kategorie', row.get('category', 'Other')),
                    'date': row.get('Datum', row.get('date', datetime.now().strftime("%Y-%m-%d")))
                }
                expenses.append(expense)

            return expenses
        except Exception as e:
            st.error(f"Import-Fehler: {str(e)}")
            return []


def render_export_import_center(manager):
    """Render export/import interface"""
    st.title("📦 Export / Import Center")

    tabs = st.tabs(["📤 Export", "📥 Import", "🔄 Backup"])

    with tabs[0]:  # Export
        render_export_interface(manager)

    with tabs[1]:  # Import
        render_import_interface(manager)

    with tabs[2]:  # Backup
        render_backup_interface(manager)


def render_export_interface(manager):
    """Export interface"""
    st.subheader("📤 Daten exportieren")

    projects = [p for p in manager.projects if not p.get('is_deleted')]

    # Filter projects for export
    col1, col2 = st.columns(2)

    with col1:
        export_archived = st.checkbox("Archivierte Projekte einbeziehen")

    with col2:
        export_deleted = st.checkbox("Gelöschte Projekte einbeziehen")

    if not export_archived:
        projects = [p for p in projects if not p.get('is_archived')]

    if export_deleted:
        projects = manager.projects  # Include all

    st.info(f"📊 {len(projects)} Projekte werden exportiert")

    # Export formats
    st.markdown("### Export-Format wählen")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📄 CSV Export")

        if st.button("Projekte als CSV", use_container_width=True):
            csv_data = DataExporter.export_projects_to_csv(projects)
            st.download_button(
                "⬇️ Download CSV",
                csv_data,
                f"projekte_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )

        if st.button("Tasks als CSV", use_container_width=True):
            csv_data = DataExporter.export_tasks_to_csv(projects)
            st.download_button(
                "⬇️ Download CSV",
                csv_data,
                f"tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )

        if st.button("Budget als CSV", use_container_width=True):
            csv_data = DataExporter.export_budget_to_csv(projects)
            st.download_button(
                "⬇️ Download CSV",
                csv_data,
                f"budget_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )

    with col2:
        st.markdown("#### 📊 Excel Export")

        if st.button("Vollständiger Excel Export", type="primary", use_container_width=True):
            excel_data = DataExporter.export_to_excel(projects)
            st.download_button(
                "⬇️ Download Excel",
                excel_data,
                f"projectmaster_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.success("✅ Excel enthält alle Sheets: Projekte, Tasks, Budget")

    with col3:
        st.markdown("#### 🗂️ JSON Export")

        if st.button("Vollständiger JSON Export", use_container_width=True):
            json_data = DataExporter.export_to_json(projects)
            st.download_button(
                "⬇️ Download JSON",
                json_data,
                f"projectmaster_backup_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json",
                use_container_width=True
            )

        st.info("💡 JSON-Format eignet sich für Backups und Migration")


def render_import_interface(manager):
    """Import interface"""
    st.subheader("📥 Daten importieren")

    st.warning("⚠️ Import überschreibt keine bestehenden Daten, sondern fügt neue hinzu.")

    import_type = st.selectbox(
        "Was möchten Sie importieren?",
        ["Tasks (CSV)", "Ausgaben (CSV)", "Projekte (JSON Backup)"]
    )

    if import_type == "Tasks (CSV)":
        st.markdown("#### Tasks importieren")
        st.info("CSV sollte Spalten enthalten: Task, Status, Assignee")

        # Select target project
        projects = [p for p in manager.projects if not p.get('is_deleted')]
        project_names = [p['title'] for p in projects]

        target_project = st.selectbox("Zielprojekt", project_names)

        uploaded_file = st.file_uploader("CSV-Datei auswählen", type=['csv'])

        if uploaded_file and st.button("Tasks importieren"):
            tasks = DataImporter.import_tasks_from_csv(uploaded_file)

            if tasks:
                # Add tasks to selected project
                project = next(p for p in projects if p['title'] == target_project)

                for task_data in tasks:
                    manager.add_task(
                        project['id'],
                        task_data['text'],
                        assignee=task_data.get('assignee')
                    )

                st.success(f"✅ {len(tasks)} Tasks erfolgreich importiert!")
                st.rerun()

    elif import_type == "Ausgaben (CSV)":
        st.markdown("#### Ausgaben importieren")
        st.info("CSV sollte Spalten enthalten: Ausgabe, Betrag, Kategorie")

        # Select target project
        projects = [p for p in manager.projects if not p.get('is_deleted')]
        project_names = [p['title'] for p in projects]

        target_project = st.selectbox("Zielprojekt", project_names)

        uploaded_file = st.file_uploader("CSV-Datei auswählen", type=['csv'])

        if uploaded_file and st.button("Ausgaben importieren"):
            expenses = DataImporter.import_expenses_from_csv(uploaded_file)

            if expenses:
                project = next(p for p in projects if p['title'] == target_project)

                for expense in expenses:
                    manager.add_expense(
                        project['id'],
                        expense['title'],
                        expense['amount'],
                        expense['category']
                    )

                st.success(f"✅ {len(expenses)} Ausgaben erfolgreich importiert!")
                st.rerun()


def render_backup_interface(manager):
    """Backup and restore interface"""
    st.subheader("🔄 Backup & Restore")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💾 Backup erstellen")

        if st.button("🔐 Vollständiges Backup", type="primary", use_container_width=True):
            # Create complete backup
            backup_data = {
                'projects': manager.projects,
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            }

            json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)

            st.download_button(
                "⬇️ Backup herunterladen",
                json_data,
                f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json",
                use_container_width=True
            )

        st.success("✅ Backup enthält alle Projekte und Einstellungen")

    with col2:
        st.markdown("#### ♻️ Backup wiederherstellen")

        uploaded_backup = st.file_uploader("Backup-Datei auswählen", type=['json'])

        if uploaded_backup:
            st.warning("⚠️ Restore überschreibt ALLE aktuellen Daten!")

            if st.button("🔄 Backup wiederherstellen", type="primary"):
                try:
                    backup_data = json.load(uploaded_backup)

                    # Restore projects
                    manager.projects = backup_data.get('projects', [])
                    manager.save()

                    st.success("✅ Backup erfolgreich wiederhergestellt!")
                    st.info(f"Zeitstempel: {backup_data.get('timestamp', 'Unknown')}")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Restore fehlgeschlagen: {str(e)}")
