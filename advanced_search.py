"""
Advanced Search Module
Global search with filters and facets
"""

import streamlit as st
from datetime import datetime
import re


def render_advanced_search(manager):
    """Render advanced search interface"""
    st.title("🔍 Advanced Search")

    # Search input
    col1, col2 = st.columns([4, 1])

    with col1:
        search_query = st.text_input(
            "Suche in Projekten, Tasks, Dokumenten...",
            placeholder="z.B. 'Marketing' oder 'Budget' oder 'Task: Testing'",
            label_visibility="collapsed"
        )

    with col2:
        search_button = st.button("🔍 Suchen", type="primary", use_container_width=True)

    # Advanced filters
    with st.expander("🎚️ Erweiterte Filter"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            filter_category = st.multiselect(
                "Kategorie",
                ["IT", "Marketing", "HR", "R&D", "Privat", "Produktion", "Vertrieb"]
            )

        with col2:
            filter_status = st.multiselect(
                "Status",
                ["Idee", "Planung", "In Arbeit", "Review", "Abgeschlossen"]
            )

        with col3:
            filter_priority = st.multiselect(
                "Priorität",
                ["Low", "Med", "High", "Critical"]
            )

        with col4:
            filter_tags = st.multiselect(
                "Tags",
                list(set(tag for p in manager.projects for tag in p.get('tags', [])))
            )

        col1, col2 = st.columns(2)

        with col1:
            include_archived = st.checkbox("Archivierte einbeziehen")

        with col2:
            include_deleted = st.checkbox("Gelöschte einbeziehen")

    if not search_query and not any([filter_category, filter_status, filter_priority, filter_tags]):
        st.info("💡 Gib einen Suchbegriff ein oder wähle Filter aus")
        return

    # Perform search
    results = perform_search(
        manager,
        search_query,
        filter_category,
        filter_status,
        filter_priority,
        filter_tags,
        include_archived,
        include_deleted
    )

    # Display results
    display_search_results(results, manager)


def perform_search(manager, query, categories, statuses, priorities, tags, include_archived, include_deleted):
    """Perform comprehensive search"""
    results = {
        'projects': [],
        'tasks': [],
        'documents': [],
        'wiki': [],
        'decisions': []
    }

    query_lower = query.lower() if query else ""

    for project in manager.projects:
        # Apply filters
        if not include_deleted and project.get('is_deleted'):
            continue

        if not include_archived and project.get('is_archived'):
            continue

        if categories and project.get('category') not in categories:
            continue

        if statuses and project.get('status') not in statuses:
            continue

        if priorities and project.get('priority') not in priorities:
            continue

        if tags and not any(tag in project.get('tags', []) for tag in tags):
            continue

        # Search in project
        if not query or matches_query(project, query_lower, 'project'):
            results['projects'].append({
                'type': 'project',
                'project': project,
                'score': calculate_relevance(project, query_lower, 'project')
            })

        # Search in tasks
        for task in project.get('tasks', []):
            if matches_query(task, query_lower, 'task'):
                results['tasks'].append({
                    'type': 'task',
                    'task': task,
                    'project': project,
                    'score': calculate_relevance(task, query_lower, 'task')
                })

        # Search in documents
        for doc in project.get('documents', []):
            if matches_query(doc, query_lower, 'document'):
                results['documents'].append({
                    'type': 'document',
                    'document': doc,
                    'project': project,
                    'score': calculate_relevance(doc, query_lower, 'document')
                })

        # Search in wiki
        for page in project.get('wiki_pages', []):
            if matches_query(page, query_lower, 'wiki'):
                results['wiki'].append({
                    'type': 'wiki',
                    'page': page,
                    'project': project,
                    'score': calculate_relevance(page, query_lower, 'wiki')
                })

        # Search in decisions
        for decision in project.get('decisions', []):
            if matches_query(decision, query_lower, 'decision'):
                results['decisions'].append({
                    'type': 'decision',
                    'decision': decision,
                    'project': project,
                    'score': calculate_relevance(decision, query_lower, 'decision')
                })

    # Sort by relevance
    for key in results:
        results[key].sort(key=lambda x: x['score'], reverse=True)

    return results


def matches_query(item, query, item_type):
    """Check if item matches search query"""
    if not query:
        return True

    if item_type == 'project':
        searchable = f"{item.get('title', '')} {item.get('description', '')} {item.get('category', '')} {' '.join(item.get('tags', []))}"
    elif item_type == 'task':
        searchable = f"{item.get('text', '')} {item.get('assignee', '')}"
    elif item_type == 'document':
        searchable = item.get('name', '')
    elif item_type == 'wiki':
        searchable = f"{item.get('title', '')} {item.get('content', '')}"
    elif item_type == 'decision':
        searchable = f"{item.get('title', '')} {item.get('rationale', '')}"
    else:
        searchable = str(item)

    return query in searchable.lower()


def calculate_relevance(item, query, item_type):
    """Calculate relevance score"""
    if not query:
        return 1

    score = 0

    if item_type == 'project':
        if query in item.get('title', '').lower():
            score += 10
        if query in item.get('description', '').lower():
            score += 5
        if query in ' '.join(item.get('tags', [])).lower():
            score += 3
    elif item_type == 'task':
        if query in item.get('text', '').lower():
            score += 10
    elif item_type == 'wiki':
        if query in item.get('title', '').lower():
            score += 10
        if query in item.get('content', '').lower():
            score += 2

    return score


def display_search_results(results, manager):
    """Display search results"""
    total_results = sum(len(v) for v in results.values())

    st.markdown(f"### 🎯 {total_results} Ergebnisse gefunden")

    # Results tabs
    tabs = st.tabs([
        f"📁 Projekte ({len(results['projects'])})",
        f"✅ Tasks ({len(results['tasks'])})",
        f"📄 Dokumente ({len(results['documents'])})",
        f"📚 Wiki ({len(results['wiki'])})",
        f"⚖️ Entscheidungen ({len(results['decisions'])})"
    ])

    with tabs[0]:  # Projects
        for result in results['projects'][:20]:
            project = result['project']
            render_project_result(project, manager)

    with tabs[1]:  # Tasks
        for result in results['tasks'][:50]:
            render_task_result(result['task'], result['project'], manager)

    with tabs[2]:  # Documents
        for result in results['documents'][:50]:
            render_document_result(result['document'], result['project'], manager)

    with tabs[3]:  # Wiki
        for result in results['wiki'][:50]:
            render_wiki_result(result['page'], result['project'], manager)

    with tabs[4]:  # Decisions
        for result in results['decisions'][:50]:
            render_decision_result(result['decision'], result['project'], manager)


def render_project_result(project, manager):
    """Render project search result"""
    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"### {project['title']}")
            st.caption(f"{project.get('category', 'N/A')} | {project.get('status', 'N/A')} | Progress: {project.get('progress', 0)}%")
            st.write(project.get('description', '')[:150] + "...")

        with col2:
            if st.button("Öffnen", key=f"open_p_{project['id']}"):
                st.session_state.view = 'details'
                st.session_state.selected_project_id = project['id']
                st.rerun()

        st.divider()


def render_task_result(task, project, manager):
    """Render task search result"""
    status_color = {'To Do': '⚪', 'In Progress': '🟡', 'Done': '✅'}[task.get('status', 'To Do')]

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"{status_color} **{task['text']}**")
        st.caption(f"Projekt: {project['title']} | Assignee: {task.get('assignee', 'Unassigned')}")

    with col2:
        if st.button("Öffnen", key=f"open_t_{task['id']}"):
            st.session_state.view = 'details'
            st.session_state.selected_project_id = project['id']
            st.rerun()


def render_document_result(doc, project, manager):
    """Render document search result"""
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"📄 **{doc['name']}**")
        st.caption(f"Projekt: {project['title']}")

    with col2:
        if st.button("Öffnen", key=f"open_d_{doc['path']}"):
            st.session_state.view = 'details'
            st.session_state.selected_project_id = project['id']
            st.rerun()


def render_wiki_result(page, project, manager):
    """Render wiki search result"""
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"📚 **{page['title']}**")
        st.caption(f"Projekt: {project['title']}")
        st.write(page.get('content', '')[:100] + "...")

    with col2:
        if st.button("Öffnen", key=f"open_w_{page['title']}_{project['id']}"):
            st.session_state.view = 'details'
            st.session_state.selected_project_id = project['id']
            st.rerun()


def render_decision_result(decision, project, manager):
    """Render decision search result"""
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"⚖️ **{decision['title']}**")
        st.caption(f"Projekt: {project['title']} | Status: {decision.get('status', 'N/A')}")
        st.write(decision.get('rationale', '')[:100] + "...")

    with col2:
        if st.button("Öffnen", key=f"open_dec_{decision['title']}_{project['id']}"):
            st.session_state.view = 'details'
            st.session_state.selected_project_id = project['id']
            st.rerun()
