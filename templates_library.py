"""
Project Templates Library
Pre-configured templates for different industries and use cases
"""

import streamlit as st
from typing import Dict, List


class TemplateLibrary:
    """Library of project templates"""

    TEMPLATES = {
        "Software Development": {
            "icon": "💻",
            "description": "Komplett-Template für Software-Projekte",
            "data": {
                "category": "IT",
                "priority": "High",
                "tasks": [
                    {"text": "Requirements gathering", "status": "To Do"},
                    {"text": "System architecture design", "status": "To Do"},
                    {"text": "Database schema design", "status": "To Do"},
                    {"text": "Frontend development", "status": "To Do"},
                    {"text": "Backend API development", "status": "To Do"},
                    {"text": "Unit testing", "status": "To Do"},
                    {"text": "Integration testing", "status": "To Do"},
                    {"text": "User acceptance testing", "status": "To Do"},
                    {"text": "Deployment setup", "status": "To Do"},
                    {"text": "Documentation", "status": "To Do"}
                ],
                "milestones": [
                    {"title": "MVP Release", "date": "", "done": False},
                    {"title": "Beta Testing", "date": "", "done": False},
                    {"title": "Production Launch", "date": "", "done": False}
                ],
                "test_cases": [
                    {"title": "User Login", "steps": "1. Navigate to login\n2. Enter credentials\n3. Click login", "expected": "User is authenticated and redirected", "status": "Untested"},
                    {"title": "API Performance", "steps": "1. Send 1000 requests\n2. Measure response time", "expected": "Response time < 200ms", "status": "Untested"}
                ],
                "tags": ["Software", "Development", "IT"]
            }
        },
        "Marketing Campaign": {
            "icon": "📢",
            "description": "Marketing-Kampagne von Planung bis Launch",
            "data": {
                "category": "Marketing",
                "priority": "High",
                "tasks": [
                    {"text": "Target audience research", "status": "To Do"},
                    {"text": "Competitor analysis", "status": "To Do"},
                    {"text": "Campaign strategy development", "status": "To Do"},
                    {"text": "Content creation", "status": "To Do"},
                    {"text": "Design assets", "status": "To Do"},
                    {"text": "Social media setup", "status": "To Do"},
                    {"text": "Ad campaign launch", "status": "To Do"},
                    {"text": "Performance monitoring", "status": "To Do"},
                    {"text": "A/B testing", "status": "To Do"},
                    {"text": "ROI analysis", "status": "To Do"}
                ],
                "budget": {
                    "total": 50000,
                    "currency": "EUR",
                    "expenses": [
                        {"title": "Ad Budget", "amount": 30000, "category": "Marketing"},
                        {"title": "Design Tools", "amount": 2000, "category": "Services"}
                    ]
                },
                "tags": ["Marketing", "Campaign", "Digital"]
            }
        },
        "Product Launch": {
            "icon": "🚀",
            "description": "Produkteinführung mit allen Phasen",
            "data": {
                "category": "Produktion",
                "priority": "Critical",
                "tasks": [
                    {"text": "Market research", "status": "To Do"},
                    {"text": "Product specification", "status": "To Do"},
                    {"text": "Prototype development", "status": "To Do"},
                    {"text": "Testing & validation", "status": "To Do"},
                    {"text": "Manufacturing setup", "status": "To Do"},
                    {"text": "Quality control", "status": "To Do"},
                    {"text": "Packaging design", "status": "To Do"},
                    {"text": "Marketing materials", "status": "To Do"},
                    {"text": "Distribution planning", "status": "To Do"},
                    {"text": "Launch event", "status": "To Do"}
                ],
                "milestones": [
                    {"title": "Prototype Complete", "date": "", "done": False},
                    {"title": "Production Ready", "date": "", "done": False},
                    {"title": "Public Launch", "date": "", "done": False}
                ],
                "stakeholders": [
                    {"name": "Product Manager", "org": "Internal", "influence": "High"},
                    {"name": "Manufacturing Partner", "org": "External", "influence": "High"}
                ],
                "tags": ["Product", "Launch", "Innovation"]
            }
        },
        "Event Planning": {
            "icon": "🎉",
            "description": "Event-Organisation von A-Z",
            "data": {
                "category": "Marketing",
                "priority": "Med",
                "tasks": [
                    {"text": "Define event objectives", "status": "To Do"},
                    {"text": "Budget planning", "status": "To Do"},
                    {"text": "Venue selection", "status": "To Do"},
                    {"text": "Catering arrangements", "status": "To Do"},
                    {"text": "Speaker invitations", "status": "To Do"},
                    {"text": "Marketing & promotion", "status": "To Do"},
                    {"text": "Registration system", "status": "To Do"},
                    {"text": "Technical setup", "status": "To Do"},
                    {"text": "Event execution", "status": "To Do"},
                    {"text": "Post-event follow-up", "status": "To Do"}
                ],
                "budget": {
                    "total": 25000,
                    "currency": "EUR",
                    "expenses": []
                },
                "tags": ["Event", "Organization"]
            }
        },
        "Research Project": {
            "icon": "🔬",
            "description": "Wissenschaftliches Forschungsprojekt",
            "data": {
                "category": "R&D",
                "priority": "High",
                "tasks": [
                    {"text": "Literature review", "status": "To Do"},
                    {"text": "Hypothesis formulation", "status": "To Do"},
                    {"text": "Methodology design", "status": "To Do"},
                    {"text": "Ethics approval", "status": "To Do"},
                    {"text": "Data collection", "status": "To Do"},
                    {"text": "Data analysis", "status": "To Do"},
                    {"text": "Results interpretation", "status": "To Do"},
                    {"text": "Paper writing", "status": "To Do"},
                    {"text": "Peer review", "status": "To Do"},
                    {"text": "Publication", "status": "To Do"}
                ],
                "wiki_pages": [
                    {"title": "Research Protocol", "content": "# Research Protocol\n\nDetailed methodology and procedures..."},
                    {"title": "Data Collection Guidelines", "content": "# Data Collection\n\nStandards and procedures..."}
                ],
                "tags": ["Research", "Science", "Academic"]
            }
        },
        "Construction Project": {
            "icon": "🏗️",
            "description": "Bauprojekt mit Phasen",
            "data": {
                "category": "Produktion",
                "priority": "High",
                "tasks": [
                    {"text": "Site survey", "status": "To Do"},
                    {"text": "Architectural design", "status": "To Do"},
                    {"text": "Permit applications", "status": "To Do"},
                    {"text": "Contractor selection", "status": "To Do"},
                    {"text": "Foundation work", "status": "To Do"},
                    {"text": "Structural construction", "status": "To Do"},
                    {"text": "MEP installation", "status": "To Do"},
                    {"text": "Interior finishing", "status": "To Do"},
                    {"text": "Quality inspection", "status": "To Do"},
                    {"text": "Handover", "status": "To Do"}
                ],
                "risks": [
                    {"desc": "Weather delays", "prob": 7, "impact": 6},
                    {"desc": "Material shortage", "prob": 5, "impact": 8},
                    {"desc": "Budget overrun", "prob": 6, "impact": 9}
                ],
                "budget": {
                    "total": 500000,
                    "currency": "EUR",
                    "expenses": []
                },
                "tags": ["Construction", "Building", "Infrastructure"]
            }
        },
        "HR Onboarding": {
            "icon": "👔",
            "description": "Mitarbeiter-Onboarding-Prozess",
            "data": {
                "category": "HR",
                "priority": "Med",
                "tasks": [
                    {"text": "Prepare workstation", "status": "To Do"},
                    {"text": "IT accounts setup", "status": "To Do"},
                    {"text": "Welcome package", "status": "To Do"},
                    {"text": "Orientation session", "status": "To Do"},
                    {"text": "Company policies training", "status": "To Do"},
                    {"text": "Team introductions", "status": "To Do"},
                    {"text": "Role-specific training", "status": "To Do"},
                    {"text": "30-day check-in", "status": "To Do"},
                    {"text": "90-day review", "status": "To Do"}
                ],
                "wiki_pages": [
                    {"title": "Company Handbook", "content": "# Welcome to the Team\n\nCompany culture and values..."},
                    {"title": "IT Setup Guide", "content": "# IT Setup\n\nTools and access..."}
                ],
                "tags": ["HR", "Onboarding", "Training"]
            }
        },
        "Agile Sprint": {
            "icon": "⚡",
            "description": "2-Wochen Agile Sprint Template",
            "data": {
                "category": "IT",
                "priority": "High",
                "tasks": [
                    {"text": "Sprint planning meeting", "status": "To Do"},
                    {"text": "User story refinement", "status": "To Do"},
                    {"text": "Daily standups (10)", "status": "To Do"},
                    {"text": "Development work", "status": "To Do"},
                    {"text": "Code reviews", "status": "To Do"},
                    {"text": "Testing", "status": "To Do"},
                    {"text": "Sprint review", "status": "To Do"},
                    {"text": "Sprint retrospective", "status": "To Do"}
                ],
                "meetings": [
                    {"date": "", "title": "Sprint Planning", "summary": "Plan sprint backlog"},
                    {"date": "", "title": "Sprint Review", "summary": "Demo completed work"},
                    {"date": "", "title": "Sprint Retrospective", "summary": "Reflect and improve"}
                ],
                "tags": ["Agile", "Sprint", "Scrum"]
            }
        }
    }

    @staticmethod
    def get_template(name: str) -> Dict:
        """Get template by name"""
        return TemplateLibrary.TEMPLATES.get(name)

    @staticmethod
    def get_all_templates() -> Dict:
        """Get all templates"""
        return TemplateLibrary.TEMPLATES


def render_template_library(manager):
    """Render template library interface"""
    st.title("📚 Project Templates Library")

    st.markdown("""
    Wähle aus vorkonfigurierten Templates für verschiedene Branchen und Anwendungsfälle.
    Jedes Template enthält Best Practices, typische Tasks und Struktur.
    """)

    # Template grid
    cols = st.columns(3)

    templates = TemplateLibrary.get_all_templates()

    for idx, (name, template) in enumerate(templates.items()):
        with cols[idx % 3]:
            render_template_card(name, template, manager)


def render_template_card(name: str, template: Dict, manager):
    """Render a single template card"""
    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                border: 1px solid #333;
                min-height: 200px;
            ">
                <div style="font-size: 3em; text-align: center;">
                    {template['icon']}
                </div>
                <h3 style="text-align: center; margin-top: 10px;">
                    {name}
                </h3>
                <p style="text-align: center; color: #aaa; font-size: 0.9em;">
                    {template['description']}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(f"🚀 Template verwenden", key=f"use_{name}", use_container_width=True):
            st.session_state[f'selected_template'] = name
            st.session_state.view = 'template_create'
            st.rerun()


def render_template_creation(manager, template_name: str):
    """Render template creation form"""
    st.title(f"📋 Neues Projekt aus Template: {template_name}")

    template = TemplateLibrary.get_template(template_name)

    if not template:
        st.error("Template nicht gefunden")
        return

    st.info(f"ℹ️ {template['description']}")

    with st.form("create_from_template"):
        project_title = st.text_input("Projekttitel", placeholder=f"z.B. Mein {template_name}")

        description = st.text_area(
            "Beschreibung",
            placeholder="Beschreibe dein Projekt..."
        )

        col1, col2 = st.columns(2)

        with col1:
            deadline = st.date_input("Deadline")

        with col2:
            budget = st.number_input("Budget (€)", min_value=0, value=template['data'].get('budget', {}).get('total', 10000))

        # Preview template content
        with st.expander("📋 Template Vorschau"):
            task_count = len(template['data'].get('tasks', []))
            milestone_count = len(template['data'].get('milestones', []))
            test_count = len(template['data'].get('test_cases', []))

            col1, col2, col3 = st.columns(3)
            col1.metric("Tasks", task_count)
            col2.metric("Meilensteine", milestone_count)
            col3.metric("Test Cases", test_count)

        submitted = st.form_submit_button("🚀 Projekt erstellen", type="primary", use_container_width=True)

        if submitted:
            if not project_title:
                st.error("Bitte Projekttitel eingeben")
            else:
                # Create project with template data
                project_id = manager.add_project(
                    title=project_title,
                    description=description,
                    category=template['data'].get('category', 'IT'),
                    priority=template['data'].get('priority', 'Med'),
                    deadline=deadline.strftime("%Y-%m-%d") if deadline else None,
                    tags=template['data'].get('tags', [])
                )

                if project_id:
                    project = manager.get_project(project_id)

                    # Add template data
                    project['budget']['total'] = budget

                    # Add tasks
                    for task_template in template['data'].get('tasks', []):
                        manager.add_task(project_id, task_template['text'])

                    # Add milestones
                    if 'milestones' in template['data']:
                        project['milestones'] = template['data']['milestones'].copy()

                    # Add test cases
                    if 'test_cases' in template['data']:
                        project['test_cases'] = template['data']['test_cases'].copy()

                    # Add wiki pages
                    if 'wiki_pages' in template['data']:
                        project['wiki_pages'] = template['data']['wiki_pages'].copy()

                    # Add risks
                    if 'risks' in template['data']:
                        project['risks'] = template['data']['risks'].copy()

                    # Add stakeholders
                    if 'stakeholders' in template['data']:
                        project['stakeholders'] = template['data']['stakeholders'].copy()

                    # Add meetings
                    if 'meetings' in template['data']:
                        project['meetings'] = template['data']['meetings'].copy()

                    # Add budget expenses
                    if 'budget' in template['data'] and 'expenses' in template['data']['budget']:
                        project['budget']['expenses'] = template['data']['budget']['expenses'].copy()

                    manager.save()

                    st.success(f"✅ Projekt '{project_title}' erfolgreich aus Template erstellt!")
                    st.balloons()

                    # Navigate to project
                    st.session_state.view = 'details'
                    st.session_state.selected_project_id = project_id
                    st.rerun()

    if st.button("← Zurück zur Template Library"):
        st.session_state.view = 'template_library'
        st.rerun()
