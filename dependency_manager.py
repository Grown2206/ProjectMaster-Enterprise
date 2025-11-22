"""
Dependency Manager
Manage task dependencies and calculate critical paths
"""

import streamlit as st
from typing import Dict, List, Set, Tuple
import plotly.graph_objects as go


class DependencyManager:
    """Manage task dependencies"""

    @staticmethod
    def initialize_session_state():
        """Initialize dependencies in session state"""
        if 'task_dependencies' not in st.session_state:
            st.session_state.task_dependencies = {}

    @staticmethod
    def add_dependency(project_id: str, task_index: int, depends_on_index: int):
        """Add dependency: task depends on another task"""
        DependencyManager.initialize_session_state()

        if project_id not in st.session_state.task_dependencies:
            st.session_state.task_dependencies[project_id] = {}

        if task_index not in st.session_state.task_dependencies[project_id]:
            st.session_state.task_dependencies[project_id][task_index] = []

        if depends_on_index not in st.session_state.task_dependencies[project_id][task_index]:
            st.session_state.task_dependencies[project_id][task_index].append(depends_on_index)

    @staticmethod
    def remove_dependency(project_id: str, task_index: int, depends_on_index: int):
        """Remove dependency"""
        DependencyManager.initialize_session_state()

        if project_id in st.session_state.task_dependencies:
            if task_index in st.session_state.task_dependencies[project_id]:
                if depends_on_index in st.session_state.task_dependencies[project_id][task_index]:
                    st.session_state.task_dependencies[project_id][task_index].remove(depends_on_index)

    @staticmethod
    def get_dependencies(project_id: str, task_index: int) -> List[int]:
        """Get list of task indices this task depends on"""
        DependencyManager.initialize_session_state()

        if project_id in st.session_state.task_dependencies:
            return st.session_state.task_dependencies[project_id].get(task_index, [])

        return []

    @staticmethod
    def get_dependent_tasks(project_id: str, task_index: int) -> List[int]:
        """Get list of task indices that depend on this task"""
        DependencyManager.initialize_session_state()

        dependent = []

        if project_id in st.session_state.task_dependencies:
            for task_idx, deps in st.session_state.task_dependencies[project_id].items():
                if task_index in deps:
                    dependent.append(task_idx)

        return dependent

    @staticmethod
    def check_circular_dependency(project_id: str, task_index: int, depends_on_index: int) -> bool:
        """Check if adding this dependency would create a circular dependency"""

        def has_path(from_idx: int, to_idx: int, visited: Set[int] = None) -> bool:
            """Check if there's a path from from_idx to to_idx"""
            if visited is None:
                visited = set()

            if from_idx == to_idx:
                return True

            if from_idx in visited:
                return False

            visited.add(from_idx)

            # Get dependencies of from_idx
            deps = DependencyManager.get_dependencies(project_id, from_idx)

            for dep in deps:
                if has_path(dep, to_idx, visited):
                    return True

            return False

        # Check if depends_on_index has a path to task_index
        return has_path(depends_on_index, task_index)

    @staticmethod
    def calculate_critical_path(project_id: str, tasks: List[Dict]) -> List[int]:
        """Calculate critical path through tasks"""
        DependencyManager.initialize_session_state()

        if not tasks:
            return []

        # Build adjacency list
        n = len(tasks)
        graph = [[] for _ in range(n)]

        if project_id in st.session_state.task_dependencies:
            for task_idx, deps in st.session_state.task_dependencies[project_id].items():
                for dep in deps:
                    if dep < n and task_idx < n:
                        graph[dep].append(task_idx)

        # Find tasks with no dependencies (start tasks)
        start_tasks = []
        for i in range(n):
            if not DependencyManager.get_dependencies(project_id, i):
                start_tasks.append(i)

        if not start_tasks:
            # If all tasks have dependencies, something is wrong
            # Return first task as start
            start_tasks = [0]

        # Calculate longest path using topological sort + DP
        # Simplified: just count dependencies
        max_path = []
        max_length = 0

        def dfs(task_idx: int, path: List[int], visited: Set[int]):
            nonlocal max_path, max_length

            if task_idx in visited:
                return

            visited.add(task_idx)
            path.append(task_idx)

            # If this is a longer path, update
            if len(path) > max_length:
                max_length = len(path)
                max_path = path.copy()

            # Visit dependent tasks
            dependent = DependencyManager.get_dependent_tasks(project_id, task_idx)

            for dep_idx in dependent:
                dfs(dep_idx, path.copy(), visited.copy())

        # Start DFS from each start task
        for start in start_tasks:
            dfs(start, [], set())

        return max_path

    @staticmethod
    def can_start_task(project_id: str, task_index: int, tasks: List[Dict]) -> Tuple[bool, List[str]]:
        """Check if a task can be started (all dependencies completed)"""
        deps = DependencyManager.get_dependencies(project_id, task_index)

        if not deps:
            return True, []

        blocking = []

        for dep_idx in deps:
            if dep_idx < len(tasks):
                dep_task = tasks[dep_idx]

                if dep_task.get('status') != 'Done':
                    blocking.append(dep_task.get('text', f'Task {dep_idx}'))

        if blocking:
            return False, blocking
        else:
            return True, []


def render_dependency_manager(manager):
    """Render dependency management interface"""
    st.title("🔗 Dependency Manager")

    DependencyManager.initialize_session_state()

    st.markdown("""
    Verwalte Task-Abhängigkeiten und visualisiere den Critical Path.
    """)

    # Project selection
    active_projects = [p for p in manager.projects if not p.get('is_deleted')]

    if not active_projects:
        st.info("Keine Projekte vorhanden")
        return

    tabs = st.tabs(["🔗 Abhängigkeiten", "📊 Dependency Graph", "🎯 Critical Path"])

    # Tab 1: Dependencies
    with tabs[0]:
        st.subheader("🔗 Task-Abhängigkeiten verwalten")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()))
        project_id = project_options[selected_project_name]

        project = manager.get_project(project_id)

        if not project:
            st.error("Projekt nicht gefunden")
            return

        tasks = project.get('tasks', [])

        if not tasks:
            st.warning("Keine Tasks vorhanden")
            return

        # Add dependency
        st.markdown("### ➕ Abhängigkeit hinzufügen")

        col1, col2 = st.columns(2)

        with col1:
            task_options = {f"{i}: {t.get('text', 'Task')[:40]}": i for i, t in enumerate(tasks)}
            selected_task = st.selectbox("Task", list(task_options.keys()), key="dep_task")
            task_idx = task_options[selected_task]

        with col2:
            depends_on_options = {f"{i}: {t.get('text', 'Task')[:40]}": i for i, t in enumerate(tasks) if i != task_idx}
            selected_depends = st.selectbox("Hängt ab von", list(depends_on_options.keys()), key="dep_depends")
            depends_idx = depends_on_options[selected_depends]

        col1, col2 = st.columns(2)

        if col1.button("➕ Abhängigkeit hinzufügen"):
            # Check for circular dependency
            if DependencyManager.check_circular_dependency(project_id, task_idx, depends_idx):
                st.error("❌ Zirkuläre Abhängigkeit! Diese Abhängigkeit würde einen Kreis erstellen.")
            else:
                DependencyManager.add_dependency(project_id, task_idx, depends_idx)
                st.success("✅ Abhängigkeit hinzugefügt!")
                st.rerun()

        # Show existing dependencies
        st.divider()
        st.markdown("### 📋 Aktuelle Abhängigkeiten")

        has_dependencies = False

        for idx, task in enumerate(tasks):
            deps = DependencyManager.get_dependencies(project_id, idx)

            if deps:
                has_dependencies = True

                with st.expander(f"📌 {task.get('text', 'Task')}"):
                    st.write("**Hängt ab von:**")

                    for dep_idx in deps:
                        if dep_idx < len(tasks):
                            dep_task = tasks[dep_idx]

                            col1, col2 = st.columns([3, 1])

                            status_icon = {
                                'Done': '✅',
                                'In Progress': '🟡',
                                'To Do': '⚪',
                                'Blocked': '🔴'
                            }.get(dep_task.get('status', 'To Do'), '⚪')

                            col1.write(f"{status_icon} {dep_task.get('text', 'Task')}")

                            if col2.button("🗑", key=f"remove_{idx}_{dep_idx}"):
                                DependencyManager.remove_dependency(project_id, idx, dep_idx)
                                st.rerun()

                    # Check if can start
                    can_start, blocking = DependencyManager.can_start_task(project_id, idx, tasks)

                    if can_start:
                        st.success("✅ Kann gestartet werden!")
                    else:
                        st.warning(f"⚠️ Wartet auf: {', '.join(blocking)}")

        if not has_dependencies:
            st.info("Keine Abhängigkeiten definiert")

    # Tab 2: Dependency Graph
    with tabs[1]:
        st.subheader("📊 Abhängigkeits-Graph")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()), key="graph_project")
        project_id = project_options[selected_project_name]

        project = manager.get_project(project_id)
        tasks = project.get('tasks', []) if project else []

        if not tasks:
            st.warning("Keine Tasks vorhanden")
        else:
            # Create graph visualization
            edge_x = []
            edge_y = []

            # Position tasks in a grid
            n = len(tasks)
            cols = min(5, n)
            rows = (n + cols - 1) // cols

            positions = {}

            for idx in range(n):
                row = idx // cols
                col = idx % cols
                positions[idx] = (col * 2, -row * 2)

            # Draw edges
            if project_id in st.session_state.task_dependencies:
                for task_idx, deps in st.session_state.task_dependencies[project_id].items():
                    if task_idx >= n:
                        continue

                    for dep_idx in deps:
                        if dep_idx >= n:
                            continue

                        x0, y0 = positions[dep_idx]
                        x1, y1 = positions[task_idx]

                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            )

            # Draw nodes
            node_x = [positions[i][0] for i in range(n)]
            node_y = [positions[i][1] for i in range(n)]

            node_colors = []

            for task in tasks:
                status = task.get('status', 'To Do')
                color = {
                    'Done': '#00cc99',
                    'In Progress': '#0099cc',
                    'To Do': '#888',
                    'Blocked': '#ff4b4b'
                }.get(status, '#888')
                node_colors.append(color)

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[f"{i}" for i in range(n)],
                textposition="middle center",
                marker=dict(
                    showscale=False,
                    color=node_colors,
                    size=40,
                    line=dict(width=2, color='white')
                ),
                showlegend=False
            )

            node_trace.hovertext = [t.get('text', 'Task')[:40] for t in tasks]

            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=0, l=0, r=0, t=0),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               plot_bgcolor='rgba(0,0,0,0)',
                               paper_bgcolor='rgba(0,0,0,0)',
                               height=600
                           ))

            st.plotly_chart(fig, use_container_width=True)

            # Legend
            st.markdown("#### 📖 Legende")

            col1, col2, col3, col4 = st.columns(4)

            col1.markdown("🟢 Done")
            col2.markdown("🔵 In Progress")
            col3.markdown("⚪ To Do")
            col4.markdown("🔴 Blocked")

    # Tab 3: Critical Path
    with tabs[2]:
        st.subheader("🎯 Critical Path Analysis")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt", list(project_options.keys()), key="critical_project")
        project_id = project_options[selected_project_name]

        project = manager.get_project(project_id)
        tasks = project.get('tasks', []) if project else []

        if not tasks:
            st.warning("Keine Tasks vorhanden")
        else:
            critical_path = DependencyManager.calculate_critical_path(project_id, tasks)

            if not critical_path:
                st.info("Kein Critical Path gefunden. Füge Abhängigkeiten hinzu!")
            else:
                st.success(f"🎯 Critical Path gefunden! Länge: {len(critical_path)} Tasks")

                st.markdown("### 📋 Critical Path Tasks")

                for idx in critical_path:
                    if idx < len(tasks):
                        task = tasks[idx]

                        status_icon = {
                            'Done': '✅',
                            'In Progress': '🟡',
                            'To Do': '⚪',
                            'Blocked': '🔴'
                        }.get(task.get('status', 'To Do'), '⚪')

                        st.write(f"{status_icon} **{idx}:** {task.get('text', 'Task')}")

                # Statistics
                st.divider()
                st.markdown("### 📊 Statistiken")

                col1, col2, col3 = st.columns(3)

                completed = sum(1 for idx in critical_path if idx < len(tasks) and tasks[idx].get('status') == 'Done')
                in_progress = sum(1 for idx in critical_path if idx < len(tasks) and tasks[idx].get('status') == 'In Progress')
                remaining = len(critical_path) - completed - in_progress

                col1.metric("Erledigt", completed)
                col2.metric("In Arbeit", in_progress)
                col3.metric("Verbleibend", remaining)

                # Progress
                if critical_path:
                    progress = (completed / len(critical_path)) * 100
                    st.markdown(f"**Critical Path Fortschritt:** {progress:.0f}%")
                    st.progress(progress / 100)

                # Warnings
                blocked_in_path = sum(1 for idx in critical_path if idx < len(tasks) and tasks[idx].get('status') == 'Blocked')

                if blocked_in_path > 0:
                    st.error(f"⚠️ WARNUNG: {blocked_in_path} blockierte Task(s) im Critical Path!")
