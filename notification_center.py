"""
Notification Center Module
Smart notifications and alerts system
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict


class NotificationEngine:
    """Generate smart notifications based on project data"""

    @staticmethod
    def generate_notifications(manager, user_name: str) -> List[Dict]:
        """Generate all notifications for a user"""
        notifications = []

        # Deadline notifications
        notifications.extend(NotificationEngine._check_deadlines(manager))

        # Budget alerts
        notifications.extend(NotificationEngine._check_budgets(manager))

        # Task assignments
        notifications.extend(NotificationEngine._check_assignments(manager, user_name))

        # Overdue tasks
        notifications.extend(NotificationEngine._check_overdue_tasks(manager, user_name))

        # Project health warnings
        notifications.extend(NotificationEngine._check_project_health(manager))

        # Milestone achievements
        notifications.extend(NotificationEngine._check_milestones(manager))

        # Sort by priority
        notifications.sort(key=lambda x: {'critical': 0, 'warning': 1, 'info': 2, 'success': 3}.get(x['type'], 4))

        return notifications

    @staticmethod
    def _check_deadlines(manager) -> List[Dict]:
        """Check for upcoming and overdue deadlines"""
        notifications = []
        today = datetime.now()

        for p in manager.projects:
            if p.get('is_deleted') or p.get('is_archived'):
                continue

            deadline_str = p.get('deadline')
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                    days_left = (deadline - today).days

                    if days_left < 0:
                        notifications.append({
                            'type': 'critical',
                            'icon': '🚨',
                            'title': 'Überfälliges Projekt',
                            'message': f"Projekt '{p['title']}' ist {abs(days_left)} Tage überfällig!",
                            'project_id': p['id'],
                            'timestamp': datetime.now().isoformat()
                        })
                    elif days_left <= 3:
                        notifications.append({
                            'type': 'critical',
                            'icon': '⏰',
                            'title': 'Deadline in Kürze',
                            'message': f"Projekt '{p['title']}' endet in {days_left} Tagen!",
                            'project_id': p['id'],
                            'timestamp': datetime.now().isoformat()
                        })
                    elif days_left <= 7:
                        notifications.append({
                            'type': 'warning',
                            'icon': '⚠️',
                            'title': 'Deadline diese Woche',
                            'message': f"Projekt '{p['title']}' endet in {days_left} Tagen",
                            'project_id': p['id'],
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    pass

        return notifications

    @staticmethod
    def _check_budgets(manager) -> List[Dict]:
        """Check for budget issues"""
        notifications = []

        for p in manager.projects:
            if p.get('is_deleted') or p.get('is_archived'):
                continue

            budget = p.get('budget', {})
            total = budget.get('total', 0)
            spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))

            if total > 0:
                usage_percent = (spent / total) * 100

                if usage_percent > 100:
                    notifications.append({
                        'type': 'critical',
                        'icon': '💸',
                        'title': 'Budget überschritten',
                        'message': f"Projekt '{p['title']}' hat Budget um {usage_percent - 100:.1f}% überschritten!",
                        'project_id': p['id'],
                        'timestamp': datetime.now().isoformat()
                    })
                elif usage_percent > 90:
                    notifications.append({
                        'type': 'warning',
                        'icon': '💰',
                        'title': 'Budget kritisch',
                        'message': f"Projekt '{p['title']}' hat {usage_percent:.1f}% des Budgets verbraucht",
                        'project_id': p['id'],
                        'timestamp': datetime.now().isoformat()
                    })
                elif usage_percent > 75:
                    notifications.append({
                        'type': 'info',
                        'icon': '📊',
                        'title': 'Budget-Update',
                        'message': f"Projekt '{p['title']}' hat {usage_percent:.1f}% des Budgets verbraucht",
                        'project_id': p['id'],
                        'timestamp': datetime.now().isoformat()
                    })

        return notifications

    @staticmethod
    def _check_assignments(manager, user_name: str) -> List[Dict]:
        """Check for new task assignments"""
        notifications = []

        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            for task in p.get('tasks', []):
                if task.get('assignee') == user_name and task.get('status') != 'Done':
                    # Check if created recently (last 24h)
                    created_str = task.get('created_at')
                    if created_str:
                        try:
                            created = datetime.strptime(created_str, "%Y-%m-%d")
                            if (datetime.now() - created).days <= 1:
                                notifications.append({
                                    'type': 'info',
                                    'icon': '📋',
                                    'title': 'Neue Aufgabe',
                                    'message': f"Du wurdest '{task['text']}' in '{p['title']}' zugewiesen",
                                    'project_id': p['id'],
                                    'timestamp': datetime.now().isoformat()
                                })
                        except:
                            pass

        return notifications

    @staticmethod
    def _check_overdue_tasks(manager, user_name: str) -> List[Dict]:
        """Check for overdue tasks"""
        notifications = []

        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            # Check if project is overdue and has incomplete tasks
            deadline_str = p.get('deadline')
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                    if deadline < datetime.now():
                        incomplete_tasks = [t for t in p.get('tasks', []) if t.get('status') != 'Done']

                        if incomplete_tasks and any(t.get('assignee') == user_name for t in incomplete_tasks):
                            notifications.append({
                                'type': 'warning',
                                'icon': '⏰',
                                'title': 'Überfällige Tasks',
                                'message': f"Du hast {len([t for t in incomplete_tasks if t.get('assignee') == user_name])} überfällige Tasks in '{p['title']}'",
                                'project_id': p['id'],
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass

        return notifications

    @staticmethod
    def _check_project_health(manager) -> List[Dict]:
        """Check project health status"""
        notifications = []

        for p in manager.projects:
            if p.get('is_deleted') or p.get('is_archived'):
                continue

            health, color = manager.calculate_health(p['id'])

            if health == "Kritisch":
                notifications.append({
                    'type': 'critical',
                    'icon': '🔴',
                    'title': 'Projekt in kritischem Zustand',
                    'message': f"Projekt '{p['title']}' benötigt dringende Aufmerksamkeit!",
                    'project_id': p['id'],
                    'timestamp': datetime.now().isoformat()
                })
            elif health == "Gefährdet":
                notifications.append({
                    'type': 'warning',
                    'icon': '🟠',
                    'title': 'Projekt gefährdet',
                    'message': f"Projekt '{p['title']}' zeigt Warnsignale",
                    'project_id': p['id'],
                    'timestamp': datetime.now().isoformat()
                })

        return notifications

    @staticmethod
    def _check_milestones(manager) -> List[Dict]:
        """Check for completed milestones"""
        notifications = []

        for p in manager.projects:
            if p.get('is_deleted'):
                continue

            for milestone in p.get('milestones', []):
                if milestone.get('done'):
                    # Check if completed recently
                    # For now, just notify on done milestones
                    notifications.append({
                        'type': 'success',
                        'icon': '🎉',
                        'title': 'Meilenstein erreicht',
                        'message': f"Meilenstein '{milestone['title']}' in '{p['title']}' abgeschlossen!",
                        'project_id': p['id'],
                        'timestamp': datetime.now().isoformat()
                    })

        return notifications[:5]  # Limit success notifications


def render_notification_center(manager, user_name: str):
    """Render notification center UI"""
    st.title("🔔 Notification Center")

    # Generate notifications
    notifications = NotificationEngine.generate_notifications(manager, user_name)

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    critical_count = len([n for n in notifications if n['type'] == 'critical'])
    warning_count = len([n for n in notifications if n['type'] == 'warning'])
    info_count = len([n for n in notifications if n['type'] == 'info'])
    success_count = len([n for n in notifications if n['type'] == 'success'])

    col1.metric("🚨 Kritisch", critical_count)
    col2.metric("⚠️ Warnungen", warning_count)
    col3.metric("ℹ️ Info", info_count)
    col4.metric("✅ Erfolg", success_count)

    st.divider()

    # Filter
    filter_type = st.multiselect(
        "Filter nach Typ",
        ['critical', 'warning', 'info', 'success'],
        default=['critical', 'warning']
    )

    # Display notifications
    if not notifications:
        st.success("🎉 Keine Benachrichtigungen! Alles im grünen Bereich.")
        return

    filtered_notifications = [n for n in notifications if n['type'] in filter_type]

    if not filtered_notifications:
        st.info("Keine Benachrichtigungen mit den ausgewählten Filtern.")
        return

    st.markdown(f"### {len(filtered_notifications)} Benachrichtigungen")

    for notif in filtered_notifications:
        render_notification_card(notif, manager)


def render_notification_card(notification: Dict, manager):
    """Render a single notification card"""
    type_colors = {
        'critical': '#ff4b4b',
        'warning': '#ffa500',
        'info': '#4b9eff',
        'success': '#00cc99'
    }

    color = type_colors.get(notification['type'], '#666666')

    with st.container():
        st.markdown(
            f"""
            <div style="
                border-left: 5px solid {color};
                background-color: rgba(255,255,255,0.05);
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 5px;
            ">
                <div style="font-size: 1.2em;">
                    {notification['icon']} <strong>{notification['title']}</strong>
                </div>
                <div style="margin-top: 5px; color: #ccc;">
                    {notification['message']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Action button
        if notification.get('project_id'):
            if st.button(f"Zum Projekt →", key=f"notif_{notification['timestamp']}_{notification['project_id'][:8]}"):
                st.session_state.view = 'details'
                st.session_state.selected_project_id = notification['project_id']
                st.rerun()


def render_notification_badge(manager, user_name: str):
    """Render notification badge for sidebar"""
    notifications = NotificationEngine.generate_notifications(manager, user_name)

    critical_count = len([n for n in notifications if n['type'] in ['critical', 'warning']])

    if critical_count > 0:
        st.sidebar.markdown(
            f"""
            <div style="
                background-color: #ff4b4b;
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 10px;
            ">
                🔔 {critical_count} wichtige Benachrichtigungen
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.sidebar.button("🔔 Benachrichtigungen anzeigen", use_container_width=True):
            st.session_state.view = 'notifications'
            st.rerun()
