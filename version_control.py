"""
Version Control System
Track and manage project versions, changes, and history
"""

import streamlit as st
from datetime import datetime
import uuid
import json
from typing import Dict, List
import copy


class VersionControl:
    """Version control for projects"""

    @staticmethod
    def initialize_session_state():
        """Initialize version control in session state"""
        if 'project_versions' not in st.session_state:
            st.session_state.project_versions = {}

    @staticmethod
    def create_snapshot(project: Dict, user: str, message: str) -> str:
        """Create project snapshot/version"""
        VersionControl.initialize_session_state()

        project_id = project['id']

        if project_id not in st.session_state.project_versions:
            st.session_state.project_versions[project_id] = []

        # Create deep copy of project
        snapshot = {
            'id': str(uuid.uuid4()),
            'version_number': len(st.session_state.project_versions[project_id]) + 1,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user,
            'message': message,
            'data': copy.deepcopy(project),
            'changes': VersionControl._calculate_changes(project_id, project)
        }

        st.session_state.project_versions[project_id].append(snapshot)

        return snapshot['id']

    @staticmethod
    def _calculate_changes(project_id: str, current_project: Dict) -> Dict:
        """Calculate what changed since last version"""
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }

        if project_id not in st.session_state.project_versions:
            changes['added'].append("Initial version")
            return changes

        versions = st.session_state.project_versions[project_id]

        if not versions:
            changes['added'].append("Initial version")
            return changes

        last_version = versions[-1]['data']

        # Compare tasks
        last_tasks = {t.get('text'): t for t in last_version.get('tasks', [])}
        current_tasks = {t.get('text'): t for t in current_project.get('tasks', [])}

        for task_text in current_tasks:
            if task_text not in last_tasks:
                changes['added'].append(f"Task: {task_text}")
            elif current_tasks[task_text] != last_tasks.get(task_text):
                changes['modified'].append(f"Task: {task_text}")

        for task_text in last_tasks:
            if task_text not in current_tasks:
                changes['deleted'].append(f"Task: {task_text}")

        # Compare other fields
        if current_project.get('status') != last_version.get('status'):
            changes['modified'].append(f"Status: {last_version.get('status')} → {current_project.get('status')}")

        if current_project.get('progress') != last_version.get('progress'):
            changes['modified'].append(f"Progress: {last_version.get('progress')}% → {current_project.get('progress')}%")

        return changes

    @staticmethod
    def get_versions(project_id: str) -> List[Dict]:
        """Get all versions for a project"""
        VersionControl.initialize_session_state()

        return st.session_state.project_versions.get(project_id, [])

    @staticmethod
    def restore_version(project_id: str, version_id: str, manager) -> bool:
        """Restore project to specific version"""
        versions = VersionControl.get_versions(project_id)

        version = next((v for v in versions if v['id'] == version_id), None)

        if not version:
            return False

        # Restore project data
        restored_data = copy.deepcopy(version['data'])

        # Update in manager
        for idx, project in enumerate(manager.projects):
            if project['id'] == project_id:
                # Keep ID and merge restored data
                restored_data['id'] = project_id
                restored_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                manager.projects[idx] = restored_data
                manager._save_data(manager.projects)

                return True

        return False

    @staticmethod
    def compare_versions(version1: Dict, version2: Dict) -> Dict:
        """Compare two versions"""
        diff = {
            'tasks': {
                'added': [],
                'removed': [],
                'modified': []
            },
            'metadata': []
        }

        # Compare tasks
        v1_tasks = {t.get('text'): t for t in version1['data'].get('tasks', [])}
        v2_tasks = {t.get('text'): t for t in version2['data'].get('tasks', [])}

        for task_text in v2_tasks:
            if task_text not in v1_tasks:
                diff['tasks']['added'].append(task_text)
            elif v2_tasks[task_text].get('status') != v1_tasks[task_text].get('status'):
                diff['tasks']['modified'].append({
                    'task': task_text,
                    'old_status': v1_tasks[task_text].get('status'),
                    'new_status': v2_tasks[task_text].get('status')
                })

        for task_text in v1_tasks:
            if task_text not in v2_tasks:
                diff['tasks']['removed'].append(task_text)

        # Compare metadata
        if version1['data'].get('status') != version2['data'].get('status'):
            diff['metadata'].append(f"Status: {version1['data'].get('status')} → {version2['data'].get('status')}")

        if version1['data'].get('progress') != version2['data'].get('progress'):
            diff['metadata'].append(f"Progress: {version1['data'].get('progress')}% → {version2['data'].get('progress')}%")

        return diff


def render_version_control(manager, current_user: str):
    """Render version control interface"""
    st.title("📜 Version Control")

    VersionControl.initialize_session_state()

    st.markdown("""
    Verwalte Projekt-Versionen, tracke Änderungen und stelle frühere Zustände wieder her.
    """)

    # Project selection
    active_projects = [p for p in manager.projects if not p.get('is_deleted')]

    if not active_projects:
        st.info("Keine Projekte vorhanden")
        return

    tabs = st.tabs(["📋 Versionen", "📸 Snapshot erstellen", "🔄 Vergleichen"])

    # Tab 1: Version List
    with tabs[0]:
        st.subheader("📋 Projekt-Versionen")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()), key="version_list_project")
        project_id = project_options[selected_project_name]

        versions = VersionControl.get_versions(project_id)

        if not versions:
            st.info("Noch keine Versionen gespeichert. Erstelle den ersten Snapshot!")
        else:
            st.markdown(f"**{len(versions)} Version(en)**")

            # Sort by version number (newest first)
            versions_sorted = sorted(versions, key=lambda x: x['version_number'], reverse=True)

            for version in versions_sorted:
                with st.expander(f"v{version['version_number']} - {version['message']}", expanded=False):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Version:** {version['version_number']}")
                        st.markdown(f"**Zeitstempel:** {version['timestamp']}")
                        st.markdown(f"**Benutzer:** {version['user']}")
                        st.markdown(f"**Nachricht:** {version['message']}")

                    with col2:
                        st.metric("Tasks", len(version['data'].get('tasks', [])))
                        st.metric("Team", len(version['data'].get('team', [])))

                    # Show changes
                    if version['changes']:
                        st.markdown("#### 📝 Änderungen")

                        if version['changes'].get('added'):
                            st.success("**Hinzugefügt:**")
                            for item in version['changes']['added']:
                                st.write(f"  + {item}")

                        if version['changes'].get('modified'):
                            st.info("**Geändert:**")
                            for item in version['changes']['modified']:
                                st.write(f"  ~ {item}")

                        if version['changes'].get('deleted'):
                            st.error("**Gelöscht:**")
                            for item in version['changes']['deleted']:
                                st.write(f"  - {item}")

                    # Actions
                    st.divider()

                    col1, col2 = st.columns(2)

                    if col1.button("🔄 Wiederherstellen", key=f"restore_{version['id']}"):
                        if VersionControl.restore_version(project_id, version['id'], manager):
                            st.success(f"✅ Projekt auf Version {version['version_number']} wiederhergestellt!")
                            st.rerun()
                        else:
                            st.error("Fehler beim Wiederherstellen")

                    if col2.button("📄 Details", key=f"details_{version['id']}"):
                        st.json(version['data'])

    # Tab 2: Create Snapshot
    with tabs[1]:
        st.subheader("📸 Snapshot erstellen")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()), key="snapshot_project")
        project_id = project_options[selected_project_name]

        project = manager.get_project(project_id)

        if not project:
            st.error("Projekt nicht gefunden")
            return

        # Current version info
        current_versions = VersionControl.get_versions(project_id)
        next_version = len(current_versions) + 1

        st.info(f"📌 Dies wird Version **v{next_version}** sein")

        # Form
        with st.form("create_snapshot"):
            message = st.text_area(
                "Version Message / Changelog",
                placeholder="z.B. 'Added 5 new tasks', 'Updated budget', 'Sprint 1 completed'",
                help="Beschreibe was sich in dieser Version geändert hat"
            )

            # Show what will be saved
            st.markdown("### 📦 Gespeichert wird:")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Tasks", len(project.get('tasks', [])))
            col2.metric("Team", len(project.get('team', [])))
            col3.metric("Progress", f"{project.get('progress', 0)}%")
            col4.metric("Status", project.get('status', 'N/A'))

            submitted = st.form_submit_button("📸 Snapshot erstellen", type="primary", use_container_width=True)

            if submitted:
                if not message.strip():
                    st.error("Bitte Version Message eingeben")
                else:
                    version_id = VersionControl.create_snapshot(project, current_user, message)

                    st.success(f"✅ Version v{next_version} erstellt!")
                    st.balloons()
                    st.rerun()

    # Tab 3: Compare Versions
    with tabs[2]:
        st.subheader("🔄 Versionen vergleichen")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()), key="compare_project")
        project_id = project_options[selected_project_name]

        versions = VersionControl.get_versions(project_id)

        if len(versions) < 2:
            st.warning("Mindestens 2 Versionen erforderlich zum Vergleichen")
        else:
            version_options = {f"v{v['version_number']} - {v['message']} ({v['timestamp']})": v for v in versions}

            col1, col2 = st.columns(2)

            with col1:
                version1_name = st.selectbox("Version 1", list(version_options.keys()))
                version1 = version_options[version1_name]

            with col2:
                version2_name = st.selectbox("Version 2", list(version_options.keys()))
                version2 = version_options[version2_name]

            if st.button("🔍 Vergleichen", type="primary"):
                diff = VersionControl.compare_versions(version1, version2)

                st.divider()
                st.markdown("### 📊 Unterschiede")

                # Tasks
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("#### ➕ Hinzugefügt")
                    if diff['tasks']['added']:
                        for task in diff['tasks']['added']:
                            st.success(f"+ {task}")
                    else:
                        st.caption("Keine")

                with col2:
                    st.markdown("#### ~ Geändert")
                    if diff['tasks']['modified']:
                        for mod in diff['tasks']['modified']:
                            st.info(f"~ {mod['task']}: {mod['old_status']} → {mod['new_status']}")
                    else:
                        st.caption("Keine")

                with col3:
                    st.markdown("#### ➖ Entfernt")
                    if diff['tasks']['removed']:
                        for task in diff['tasks']['removed']:
                            st.error(f"- {task}")
                    else:
                        st.caption("Keine")

                # Metadata
                if diff['metadata']:
                    st.divider()
                    st.markdown("#### 📝 Metadata-Änderungen")

                    for change in diff['metadata']:
                        st.write(f"• {change}")

                # Summary
                st.divider()
                st.markdown("### 📈 Zusammenfassung")

                total_changes = (
                    len(diff['tasks']['added']) +
                    len(diff['tasks']['modified']) +
                    len(diff['tasks']['removed']) +
                    len(diff['metadata'])
                )

                if total_changes == 0:
                    st.success("✅ Keine Unterschiede zwischen den Versionen")
                else:
                    st.info(f"📊 Gesamt {total_changes} Änderung(en)")


def render_version_history_sidebar(project_id: str):
    """Render compact version history in sidebar"""
    VersionControl.initialize_session_state()

    versions = VersionControl.get_versions(project_id)

    if not versions:
        st.sidebar.caption("📜 Keine Versionen")
        return

    st.sidebar.markdown("### 📜 Version History")

    # Show last 5 versions
    recent_versions = sorted(versions, key=lambda x: x['version_number'], reverse=True)[:5]

    for version in recent_versions:
        st.sidebar.caption(f"v{version['version_number']} - {version['message'][:20]}...")

    if len(versions) > 5:
        st.sidebar.caption(f"... und {len(versions) - 5} weitere")
