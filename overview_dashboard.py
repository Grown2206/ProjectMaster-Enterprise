"""
Overview Dashboard with Preview Images
Displays all projects and experiments as visual cards with preview images
"""

import streamlit as st
from pathlib import Path
from PIL import Image
import io


def render_overview_dashboard(manager):
    """Render overview dashboard with preview cards for projects and experiments"""

    st.title("🎯 Übersicht Dashboard")
    st.markdown("### Alle Projekte und Experimente auf einen Blick")

    # Create tabs for Projects and Experiments
    tab1, tab2 = st.tabs(["📁 Projekte", "🧪 Experimente"])

    # --- PROJECTS TAB ---
    with tab1:
        render_projects_overview(manager)

    # --- EXPERIMENTS TAB ---
    with tab2:
        render_experiments_overview(manager)


def get_project_preview_image(project):
    """Get preview image for project (first image or default placeholder)"""
    if project.get('images') and len(project['images']) > 0:
        # Return first image path
        return project['images'][0].get('path', None)
    return None


def get_experiment_preview_image(experiment):
    """Get preview image for experiment (first image or default placeholder)"""
    if experiment.get('images') and len(experiment['images']) > 0:
        # Return first image path
        return experiment['images'][0].get('path', None)
    return None


def render_project_card(project, manager, col):
    """Render a single project card with preview image"""

    with col:
        # Create card container
        with st.container():
            # Get preview image
            preview_path = get_project_preview_image(project)

            # Display image or placeholder
            if preview_path and Path(preview_path).exists():
                try:
                    img = Image.open(preview_path)
                    st.image(img, use_container_width=True)
                except Exception:
                    # Fallback to placeholder
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    height: 200px; display: flex; align-items: center; justify-content: center;
                                    border-radius: 10px; margin-bottom: 10px;'>
                            <h2 style='color: white; font-size: 48px;'>📁</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                # Gradient placeholder with project icon
                category_colors = {
                    'IT': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'Marketing': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    'HR': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                    'R&D': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                    'Privat': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                    'Produktion': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
                    'Vertrieb': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                    'Finanzen': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
                }
                gradient = category_colors.get(project['category'], 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')

                st.markdown(
                    f"""
                    <div style='background: {gradient};
                                height: 200px; display: flex; align-items: center; justify-content: center;
                                border-radius: 10px; margin-bottom: 10px;'>
                        <h2 style='color: white; font-size: 48px;'>📁</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Project Title
            st.markdown(f"### {project['title']}")

            # Status badge
            status_colors = {
                'Idee': '🔵',
                'Planung': '🟡',
                'In Arbeit': '🟢',
                'Review': '🟠',
                'Abgeschlossen': '✅',
                'Pausiert': '⏸️'
            }
            status_icon = status_colors.get(project['status'], '⚪')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", f"{status_icon} {project['status']}")
            with col2:
                st.metric("Fortschritt", f"{project['progress']}%")
            with col3:
                priority_emoji = {'Low': '🟢', 'Med': '🟡', 'High': '🔴', 'Critical': '🚨'}
                st.metric("Priorität", f"{priority_emoji.get(project['priority'], '⚪')} {project['priority']}")

            # Description (truncated)
            desc = project['description']
            if len(desc) > 100:
                desc = desc[:100] + "..."
            st.markdown(f"*{desc}*")

            # Tags
            if project.get('tags'):
                tags_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px;">{tag}</span>' for tag in project['tags'][:3]])
                st.markdown(tags_html, unsafe_allow_html=True)

            st.markdown("---")

            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"📋 **{len(project.get('tasks', []))}** Tasks")
            with col2:
                st.markdown(f"👥 **{len(project.get('team', []))}** Team")
            with col3:
                st.markdown(f"⚠️ **{len(project.get('risks', []))}** Risiken")

            # View button
            if st.button(f"Details anzeigen", key=f"view_proj_{project['id']}", use_container_width=True):
                st.session_state.selected_project = project['id']
                st.session_state.view = 'single'
                st.rerun()


def render_experiment_card(experiment, manager, col):
    """Render a single experiment card with preview image"""

    with col:
        # Create card container
        with st.container():
            # Get preview image
            preview_path = get_experiment_preview_image(experiment)

            # Display image or placeholder
            if preview_path and Path(preview_path).exists():
                try:
                    img = Image.open(preview_path)
                    st.image(img, use_container_width=True)
                except Exception:
                    # Fallback to placeholder
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                    height: 200px; display: flex; align-items: center; justify-content: center;
                                    border-radius: 10px; margin-bottom: 10px;'>
                            <h2 style='color: white; font-size: 48px;'>🧪</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                # Gradient placeholder with experiment icon
                category_colors = {
                    'Marketing': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    'IT': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'Produkt': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                    'UX/UI': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
                }
                gradient = category_colors.get(experiment['category'], 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)')

                st.markdown(
                    f"""
                    <div style='background: {gradient};
                                height: 200px; display: flex; align-items: center; justify-content: center;
                                border-radius: 10px; margin-bottom: 10px;'>
                        <h2 style='color: white; font-size: 48px;'>🧪</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Experiment Name
            st.markdown(f"### {experiment['name']}")

            # Status badge
            status_colors = {
                'Geplant': '🔵',
                'Laufend': '🟢',
                'Analysiert': '🟡',
                'Abgeschlossen': '✅'
            }
            status_icon = status_colors.get(experiment['status'], '⚪')

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", f"{status_icon} {experiment['status']}")
            with col2:
                st.metric("Kategorie", experiment['category'])

            # Description (truncated)
            desc = experiment['description']
            if len(desc) > 100:
                desc = desc[:100] + "..."
            st.markdown(f"*{desc}*")

            # Tester
            st.markdown(f"👤 **Tester:** {experiment.get('tester', 'Unbekannt')}")

            st.markdown("---")

            # Stats
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"📊 **{len(experiment.get('samples', []))}** Samples")
            with col2:
                st.markdown(f"🖼️ **{len(experiment.get('images', []))}** Bilder")

            # View button
            if st.button(f"Details anzeigen", key=f"view_exp_{experiment['id']}", use_container_width=True):
                st.session_state.selected_experiment = experiment['id']
                st.session_state.view = 'experiments'
                st.rerun()


def render_projects_overview(manager):
    """Render projects overview with cards"""

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_status = st.multiselect(
            "Status filtern",
            options=['Idee', 'Planung', 'In Arbeit', 'Review', 'Abgeschlossen', 'Pausiert'],
            default=['Idee', 'Planung', 'In Arbeit', 'Review']
        )

    with col2:
        filter_category = st.multiselect(
            "Kategorie filtern",
            options=['IT', 'Marketing', 'HR', 'R&D', 'Privat', 'Produktion', 'Vertrieb', 'Finanzen'],
            default=[]
        )

    with col3:
        filter_priority = st.multiselect(
            "Priorität filtern",
            options=['Low', 'Med', 'High', 'Critical'],
            default=[]
        )

    st.markdown("---")

    # Get filtered projects
    projects = [p for p in manager.projects if not p.get('is_archived') and not p.get('is_deleted')]

    # Apply filters
    if filter_status:
        projects = [p for p in projects if p['status'] in filter_status]
    if filter_category:
        projects = [p for p in projects if p['category'] in filter_category]
    if filter_priority:
        projects = [p for p in projects if p['priority'] in filter_priority]

    # Sort options
    sort_by = st.selectbox(
        "Sortieren nach",
        options=['Neueste zuerst', 'Älteste zuerst', 'Fortschritt (hoch-niedrig)', 'Fortschritt (niedrig-hoch)', 'Priorität'],
        index=0
    )

    if sort_by == 'Neueste zuerst':
        projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == 'Älteste zuerst':
        projects.sort(key=lambda x: x.get('created_at', ''))
    elif sort_by == 'Fortschritt (hoch-niedrig)':
        projects.sort(key=lambda x: x.get('progress', 0), reverse=True)
    elif sort_by == 'Fortschritt (niedrig-hoch)':
        projects.sort(key=lambda x: x.get('progress', 0))
    elif sort_by == 'Priorität':
        priority_order = {'Critical': 0, 'High': 1, 'Med': 2, 'Low': 3}
        projects.sort(key=lambda x: priority_order.get(x['priority'], 4))

    st.markdown(f"**Gefundene Projekte:** {len(projects)}")
    st.markdown("---")

    # Display projects in grid (3 columns)
    if not projects:
        st.info("Keine Projekte gefunden mit den ausgewählten Filtern.")
        return

    # Create grid layout
    cols_per_row = 3
    for i in range(0, len(projects), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(projects):
                render_project_card(projects[i + j], manager, cols[j])


def render_experiments_overview(manager):
    """Render experiments overview with cards"""

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        filter_status = st.multiselect(
            "Status filtern",
            options=['Geplant', 'Laufend', 'Analysiert', 'Abgeschlossen'],
            default=['Geplant', 'Laufend'],
            key="exp_status_filter"
        )

    with col2:
        filter_category = st.multiselect(
            "Kategorie filtern",
            options=['Marketing', 'IT', 'Produkt', 'UX/UI'],
            default=[],
            key="exp_category_filter"
        )

    st.markdown("---")

    # Get filtered experiments
    experiments = manager.experiments

    # Apply filters
    if filter_status:
        experiments = [e for e in experiments if e['status'] in filter_status]
    if filter_category:
        experiments = [e for e in experiments if e['category'] in filter_category]

    # Sort options
    sort_by = st.selectbox(
        "Sortieren nach",
        options=['Neueste zuerst', 'Älteste zuerst', 'Name (A-Z)', 'Name (Z-A)'],
        index=0,
        key="exp_sort"
    )

    if sort_by == 'Neueste zuerst':
        experiments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == 'Älteste zuerst':
        experiments.sort(key=lambda x: x.get('created_at', ''))
    elif sort_by == 'Name (A-Z)':
        experiments.sort(key=lambda x: x.get('name', ''))
    elif sort_by == 'Name (Z-A)':
        experiments.sort(key=lambda x: x.get('name', ''), reverse=True)

    st.markdown(f"**Gefundene Experimente:** {len(experiments)}")
    st.markdown("---")

    # Display experiments in grid (3 columns)
    if not experiments:
        st.info("Keine Experimente gefunden mit den ausgewählten Filtern.")
        return

    # Create grid layout
    cols_per_row = 3
    for i in range(0, len(experiments), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(experiments):
                render_experiment_card(experiments[i + j], manager, cols[j])
