"""
Mind Map Visualizer
Interactive mind map visualization for projects and tasks
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List
import json


class MindMapGenerator:
    """Generate interactive mind maps"""

    @staticmethod
    def create_project_mindmap(project: Dict):
        """Create mind map from project structure"""
        # Build hierarchical structure
        nodes = []
        edges = []

        # Root node (Project)
        nodes.append({
            'id': 'root',
            'label': project['title'],
            'type': 'project',
            'level': 0,
            'x': 0,
            'y': 0
        })

        # Add main categories as level 1
        categories = [
            {'id': 'tasks', 'label': f'Tasks ({len(project.get("tasks", []))})', 'color': '#00cc99'},
            {'id': 'team', 'label': f'Team ({len(project.get("team", []))})', 'color': '#0099cc'},
            {'id': 'milestones', 'label': f'Milestones ({len(project.get("milestones", []))})', 'color': '#9900cc'},
            {'id': 'risks', 'label': f'Risks ({len(project.get("risks", []))})', 'color': '#ff4b4b'},
            {'id': 'budget', 'label': 'Budget', 'color': '#ffa500'},
        ]

        angle_step = 360 / len(categories)

        for idx, cat in enumerate(categories):
            angle = (idx * angle_step) * (3.14159 / 180)  # Convert to radians
            x = 2 * np.cos(angle) if 'np' in dir() else 2
            y = 2 * np.sin(angle) if 'np' in dir() else idx - len(categories)/2

            nodes.append({
                'id': cat['id'],
                'label': cat['label'],
                'type': 'category',
                'level': 1,
                'x': x,
                'y': y,
                'color': cat['color']
            })

            edges.append({
                'from': 'root',
                'to': cat['id']
            })

        # Add tasks as level 2
        tasks = project.get('tasks', [])
        for idx, task in enumerate(tasks[:10]):  # Limit to 10 tasks for readability
            task_id = f"task_{idx}"
            status_color = {
                'To Do': '#888',
                'In Progress': '#0099cc',
                'Done': '#00cc99',
                'Blocked': '#ff4b4b'
            }.get(task.get('status', 'To Do'), '#888')

            # Position around tasks node
            angle = (idx * 36) * (3.14159 / 180)
            base_x = nodes[1]['x']  # tasks node position
            base_y = nodes[1]['y']
            x = base_x + 1.5 * (np.cos(angle) if 'np' in dir() else 1)
            y = base_y + 1.5 * (np.sin(angle) if 'np' in dir() else idx * 0.3)

            nodes.append({
                'id': task_id,
                'label': task.get('text', 'Task')[:20],
                'type': 'task',
                'level': 2,
                'x': x,
                'y': y,
                'color': status_color
            })

            edges.append({
                'from': 'tasks',
                'to': task_id
            })

        return nodes, edges

    @staticmethod
    def render_mindmap_plotly(nodes: List[Dict], edges: List[Dict]):
        """Render mind map using Plotly"""
        # Create edge traces
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=2, color='#444'),
            hoverinfo='none',
            mode='lines'
        )

        # Build node lookup
        node_lookup = {n['id']: n for n in nodes}

        for edge in edges:
            x0, y0 = node_lookup[edge['from']]['x'], node_lookup[edge['from']]['y']
            x1, y1 = node_lookup[edge['to']]['x'], node_lookup[edge['to']]['y']

            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)

        # Create node trace
        node_trace = go.Scatter(
            x=[n['x'] for n in nodes],
            y=[n['y'] for n in nodes],
            mode='markers+text',
            hoverinfo='text',
            text=[n['label'] for n in nodes],
            textposition="top center",
            marker=dict(
                showscale=False,
                color=[n.get('color', '#00cc99') for n in nodes],
                size=[30 if n['level'] == 0 else 20 if n['level'] == 1 else 15 for n in nodes],
                line=dict(width=2, color='white')
            )
        )

        node_trace.hovertext = [f"{n['label']}<br>Type: {n['type']}" for n in nodes]

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

        return fig


# Fallback for simple visualization without numpy
import math

class SimpleMindMap:
    """Simple mind map without numpy dependency"""

    @staticmethod
    def create_simple_tree(project: Dict):
        """Create simple tree structure"""
        tree = {
            'name': project['title'],
            'children': []
        }

        # Add categories
        if project.get('tasks'):
            tree['children'].append({
                'name': f"Tasks ({len(project['tasks'])})",
                'children': [{'name': t.get('text', 'Task')[:30]} for t in project['tasks'][:5]]
            })

        if project.get('team'):
            tree['children'].append({
                'name': f"Team ({len(project['team'])})",
                'children': [{'name': m.get('name', 'Member')} for m in project['team'][:5]]
            })

        if project.get('milestones'):
            tree['children'].append({
                'name': f"Milestones ({len(project['milestones'])})",
                'children': [{'name': m.get('title', 'Milestone')} for m in project['milestones'][:5]]
            })

        return tree


def render_mind_map_view(manager):
    """Render mind map visualization interface"""
    st.title("🗺️ Mind Map Visualizer")

    st.markdown("""
    Visualisiere deine Projekte als interaktive Mind Maps.
    Erkenne Strukturen, Verbindungen und Zusammenhänge auf einen Blick.
    """)

    # Project selection
    active_projects = [p for p in manager.projects if not p.get('is_deleted')]

    if not active_projects:
        st.info("Keine Projekte vorhanden")
        return

    tabs = st.tabs(["🗺️ Project Mind Map", "🌳 Task Tree", "📊 Structure Analysis"])

    # Tab 1: Mind Map
    with tabs[0]:
        st.subheader("🗺️ Projekt als Mind Map")

        project_options = {p['title']: p['id'] for p in active_projects}
        selected_project_name = st.selectbox("Projekt auswählen", list(project_options.keys()))
        project_id = project_options[selected_project_name]

        project = manager.get_project(project_id)

        if not project:
            st.error("Projekt nicht gefunden")
            return

        # Options
        col1, col2 = st.columns(2)

        with col1:
            show_tasks = st.checkbox("📝 Tasks anzeigen", value=True)
            show_team = st.checkbox("👥 Team anzeigen", value=True)

        with col2:
            show_milestones = st.checkbox("🎯 Milestones anzeigen", value=True)
            show_risks = st.checkbox("⚠️ Risks anzeigen", value=False)

        # Generate mind map
        try:
            # Try numpy-based visualization
            import numpy as np

            nodes, edges = MindMapGenerator.create_project_mindmap(project)
            fig = MindMapGenerator.render_mindmap_plotly(nodes, edges)

            st.plotly_chart(fig, use_container_width=True)

        except ImportError:
            # Fallback to simple tree
            st.info("📊 Vereinfachte Baum-Ansicht (numpy nicht verfügbar)")

            tree = SimpleMindMap.create_simple_tree(project)

            # Display as indented list
            def render_tree(node, level=0):
                indent = "&nbsp;" * (level * 4)
                st.markdown(f"{indent}• **{node['name']}**", unsafe_allow_html=True)

                for child in node.get('children', []):
                    render_tree(child, level + 1)

            render_tree(tree)

        # Project stats
        st.divider()
        st.markdown("### 📊 Projekt-Struktur")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Tasks", len(project.get('tasks', [])))
        col2.metric("Team", len(project.get('team', [])))
        col3.metric("Milestones", len(project.get('milestones', [])))
        col4.metric("Risks", len(project.get('risks', [])))

    # Tab 2: Task Tree
    with tabs[1]:
        st.subheader("🌳 Task-Baum")

        st.info("Hierarchische Darstellung aller Tasks")

        tasks = project.get('tasks', [])

        if not tasks:
            st.warning("Keine Tasks vorhanden")
        else:
            # Group by status
            status_groups = {}
            for task in tasks:
                status = task.get('status', 'To Do')
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(task)

            # Display grouped
            for status, tasks_in_status in status_groups.items():
                status_icons = {
                    'To Do': '⚪',
                    'In Progress': '🟡',
                    'Done': '🟢',
                    'Blocked': '🔴'
                }

                icon = status_icons.get(status, '⚪')

                with st.expander(f"{icon} {status} ({len(tasks_in_status)})", expanded=True):
                    for task in tasks_in_status:
                        col1, col2 = st.columns([3, 1])

                        col1.write(f"• {task.get('text', 'Task')}")

                        if task.get('assignee'):
                            col2.caption(f"👤 {task['assignee']}")

    # Tab 3: Structure Analysis
    with tabs[2]:
        st.subheader("📊 Struktur-Analyse")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Komplexität")

            total_elements = (
                len(project.get('tasks', [])) +
                len(project.get('team', [])) +
                len(project.get('milestones', [])) +
                len(project.get('risks', [])) +
                len(project.get('decisions', [])) +
                len(project.get('stakeholders', []))
            )

            st.metric("Gesamt Elemente", total_elements)

            # Complexity score
            if total_elements < 10:
                complexity = "Einfach"
                color = "#00cc99"
            elif total_elements < 50:
                complexity = "Mittel"
                color = "#ffa500"
            else:
                complexity = "Komplex"
                color = "#ff4b4b"

            st.markdown(f"""
            <div style="
                background: {color}33;
                color: {color};
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                margin-top: 10px;
            ">
                {complexity}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 🎯 Fokus-Bereiche")

            focus_areas = []

            if len(project.get('tasks', [])) > 20:
                focus_areas.append("📝 Task-Management optimieren")

            if len(project.get('risks', [])) > 5:
                focus_areas.append("⚠️ Risk Mitigation priorisieren")

            if len(project.get('team', [])) < 2:
                focus_areas.append("👥 Team erweitern")

            if not project.get('milestones'):
                focus_areas.append("🎯 Milestones definieren")

            if focus_areas:
                for area in focus_areas:
                    st.write(f"• {area}")
            else:
                st.success("✅ Gut strukturiert!")

        # Distribution chart
        st.markdown("#### 📊 Verteilung der Elemente")

        import plotly.express as px

        data = {
            'Category': ['Tasks', 'Team', 'Milestones', 'Risks', 'Decisions'],
            'Count': [
                len(project.get('tasks', [])),
                len(project.get('team', [])),
                len(project.get('milestones', [])),
                len(project.get('risks', [])),
                len(project.get('decisions', []))
            ]
        }

        fig = px.bar(
            data,
            x='Category',
            y='Count',
            title='',
            color='Category'
        )

        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Export options
        st.divider()
        st.markdown("### 💾 Export")

        col1, col2 = st.columns(2)

        if col1.button("📄 Export as JSON"):
            tree = SimpleMindMap.create_simple_tree(project)
            st.download_button(
                "Download JSON",
                data=json.dumps(tree, indent=2),
                file_name=f"{project['title']}_mindmap.json",
                mime="application/json"
            )

        if col2.button("📊 Export as Text"):
            # Generate text outline
            tree = SimpleMindMap.create_simple_tree(project)

            def tree_to_text(node, level=0):
                indent = "  " * level
                lines = [f"{indent}- {node['name']}"]

                for child in node.get('children', []):
                    lines.extend(tree_to_text(child, level + 1))

                return lines

            text_output = "\n".join(tree_to_text(tree))

            st.download_button(
                "Download Text",
                data=text_output,
                file_name=f"{project['title']}_outline.txt",
                mime="text/plain"
            )
