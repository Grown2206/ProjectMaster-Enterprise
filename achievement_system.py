"""
Achievement System & Gamification
Badges, XP, Leaderboards and progress tracking
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px


class AchievementSystem:
    """Achievement and gamification system"""

    ACHIEVEMENTS = {
        # Project Achievements
        "first_project": {
            "name": "🎯 First Steps",
            "description": "Erstelle dein erstes Projekt",
            "category": "Projects",
            "xp": 50,
            "condition": lambda stats: stats['total_projects'] >= 1
        },
        "project_master": {
            "name": "📊 Project Master",
            "description": "Verwalte 10 Projekte gleichzeitig",
            "category": "Projects",
            "xp": 200,
            "condition": lambda stats: stats['total_projects'] >= 10
        },
        "project_legend": {
            "name": "🏆 Project Legend",
            "description": "Erstelle 50 Projekte",
            "category": "Projects",
            "xp": 500,
            "condition": lambda stats: stats['total_projects'] >= 50
        },
        "completer": {
            "name": "✅ Completer",
            "description": "Schließe 5 Projekte erfolgreich ab",
            "category": "Projects",
            "xp": 150,
            "condition": lambda stats: stats['completed_projects'] >= 5
        },
        "finisher": {
            "name": "🎊 The Finisher",
            "description": "Schließe 25 Projekte ab",
            "category": "Projects",
            "xp": 400,
            "condition": lambda stats: stats['completed_projects'] >= 25
        },

        # Task Achievements
        "task_rookie": {
            "name": "📝 Task Rookie",
            "description": "Erstelle 10 Tasks",
            "category": "Tasks",
            "xp": 50,
            "condition": lambda stats: stats['total_tasks'] >= 10
        },
        "task_warrior": {
            "name": "⚔️ Task Warrior",
            "description": "Erledige 50 Tasks",
            "category": "Tasks",
            "xp": 200,
            "condition": lambda stats: stats['completed_tasks'] >= 50
        },
        "task_legend": {
            "name": "🗡️ Task Legend",
            "description": "Erledige 200 Tasks",
            "category": "Tasks",
            "xp": 500,
            "condition": lambda stats: stats['completed_tasks'] >= 200
        },
        "daily_grind": {
            "name": "💪 Daily Grind",
            "description": "Erledige 5 Tasks an einem Tag",
            "category": "Tasks",
            "xp": 100,
            "condition": lambda stats: stats.get('tasks_today', 0) >= 5
        },

        # Time Tracking Achievements
        "time_tracker": {
            "name": "⏱️ Time Tracker",
            "description": "Erfasse 10 Stunden",
            "category": "Time",
            "xp": 75,
            "condition": lambda stats: stats.get('total_hours', 0) >= 10
        },
        "time_master": {
            "name": "⏰ Time Master",
            "description": "Erfasse 100 Stunden",
            "category": "Time",
            "xp": 250,
            "condition": lambda stats: stats.get('total_hours', 0) >= 100
        },
        "workaholic": {
            "name": "🔥 Workaholic",
            "description": "Erfasse 40+ Stunden in einer Woche",
            "category": "Time",
            "xp": 150,
            "condition": lambda stats: stats.get('hours_this_week', 0) >= 40
        },

        # Quality Achievements
        "perfectionist": {
            "name": "💎 Perfectionist",
            "description": "Erreiche 100% Gesundheit in 3 Projekten",
            "category": "Quality",
            "xp": 200,
            "condition": lambda stats: stats.get('healthy_projects', 0) >= 3
        },
        "budget_master": {
            "name": "💰 Budget Master",
            "description": "Halte 5 Projekte im Budget",
            "category": "Quality",
            "xp": 250,
            "condition": lambda stats: stats.get('on_budget_projects', 0) >= 5
        },
        "deadline_keeper": {
            "name": "📅 Deadline Keeper",
            "description": "Halte 10 Deadlines ein",
            "category": "Quality",
            "xp": 200,
            "condition": lambda stats: stats.get('deadlines_met', 0) >= 10
        },

        # Collaboration Achievements
        "team_player": {
            "name": "👥 Team Player",
            "description": "Füge 5 Team-Mitglieder hinzu",
            "category": "Team",
            "xp": 100,
            "condition": lambda stats: stats.get('team_members_added', 0) >= 5
        },
        "delegator": {
            "name": "🎯 Delegator",
            "description": "Weise 20 Tasks zu",
            "category": "Team",
            "xp": 150,
            "condition": lambda stats: stats.get('tasks_assigned', 0) >= 20
        },

        # Documentation Achievements
        "documenter": {
            "name": "📚 Documenter",
            "description": "Erstelle 10 Wiki-Seiten",
            "category": "Docs",
            "xp": 150,
            "condition": lambda stats: stats.get('wiki_pages', 0) >= 10
        },
        "knowledge_base": {
            "name": "🧠 Knowledge Base",
            "description": "Lade 20 Dokumente hoch",
            "category": "Docs",
            "xp": 100,
            "condition": lambda stats: stats.get('documents_uploaded', 0) >= 20
        },

        # Special Achievements
        "early_bird": {
            "name": "🌅 Early Bird",
            "description": "Nutze die App vor 7 Uhr morgens",
            "category": "Special",
            "xp": 50,
            "condition": lambda stats: stats.get('early_bird_login', False)
        },
        "night_owl": {
            "name": "🦉 Night Owl",
            "description": "Nutze die App nach 23 Uhr",
            "category": "Special",
            "xp": 50,
            "condition": lambda stats: stats.get('night_owl_login', False)
        },
        "speed_demon": {
            "name": "⚡ Speed Demon",
            "description": "Schließe ein Projekt in unter 24 Stunden ab",
            "category": "Special",
            "xp": 200,
            "condition": lambda stats: stats.get('fast_completion', False)
        },
        "explorer": {
            "name": "🔍 Explorer",
            "description": "Nutze alle Features mindestens einmal",
            "category": "Special",
            "xp": 300,
            "condition": lambda stats: stats.get('features_used', 0) >= 15
        }
    }

    @classmethod
    def calculate_user_stats(cls, manager, user_name: str) -> Dict:
        """Calculate user statistics for achievements"""
        stats = {
            'total_projects': 0,
            'completed_projects': 0,
            'total_tasks': 0,
            'completed_tasks': 0,
            'tasks_today': 0,
            'total_hours': 0,
            'hours_this_week': 0,
            'healthy_projects': 0,
            'on_budget_projects': 0,
            'deadlines_met': 0,
            'team_members_added': 0,
            'tasks_assigned': 0,
            'wiki_pages': 0,
            'documents_uploaded': 0,
            'features_used': 0,
            'early_bird_login': False,
            'night_owl_login': False,
            'fast_completion': False
        }

        # Count projects
        for project in manager.projects:
            if project.get('is_deleted'):
                continue

            stats['total_projects'] += 1

            if project.get('status') == 'Abgeschlossen':
                stats['completed_projects'] += 1

            # Check health
            health, _ = manager.calculate_health(project['id'])
            if health == 'Gesund':
                stats['healthy_projects'] += 1

            # Check budget
            budget = project.get('budget', {})
            total = budget.get('total', 0)
            spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))
            if total > 0 and spent <= total:
                stats['on_budget_projects'] += 1

            # Count tasks
            tasks = project.get('tasks', [])
            stats['total_tasks'] += len(tasks)
            stats['completed_tasks'] += len([t for t in tasks if t.get('status') == 'Done'])

            # Count assigned tasks
            for task in tasks:
                if task.get('assignee') and task['assignee'] != user_name:
                    stats['tasks_assigned'] += 1

            # Count team members
            stats['team_members_added'] += len(project.get('team', []))

            # Count wiki pages
            stats['wiki_pages'] += len(project.get('wiki_pages', []))

            # Count documents
            stats['documents_uploaded'] += len(project.get('documents', []))

            # Count time logs
            for log in project.get('time_logs', []):
                stats['total_hours'] += log.get('hours', 0)

        # Check current time
        current_hour = datetime.now().hour
        if current_hour < 7:
            stats['early_bird_login'] = True
        if current_hour >= 23:
            stats['night_owl_login'] = True

        # Check features used (simplified)
        if 'features_accessed' in st.session_state:
            stats['features_used'] = len(st.session_state.features_accessed)

        return stats

    @classmethod
    def check_achievements(cls, manager, user_name: str) -> Tuple[List[str], int]:
        """Check which achievements are unlocked and calculate total XP"""
        stats = cls.calculate_user_stats(manager, user_name)

        unlocked = []
        total_xp = 0

        for achievement_id, achievement in cls.ACHIEVEMENTS.items():
            if achievement['condition'](stats):
                unlocked.append(achievement_id)
                total_xp += achievement['xp']

        return unlocked, total_xp

    @classmethod
    def get_level_from_xp(cls, xp: int) -> Tuple[int, int, int]:
        """Calculate level from XP (level, current_level_xp, next_level_xp)"""
        # Level formula: level = floor(sqrt(xp / 100))
        level = int((xp / 100) ** 0.5) + 1
        current_level_xp = (level - 1) ** 2 * 100
        next_level_xp = level ** 2 * 100

        return level, current_level_xp, next_level_xp


def render_achievement_center(manager, user_name: str):
    """Render achievement and gamification center"""
    st.title("🏆 Achievement Center")

    # Initialize achievement tracking in session state
    if 'unlocked_achievements' not in st.session_state:
        st.session_state.unlocked_achievements = {}

    if user_name not in st.session_state.unlocked_achievements:
        st.session_state.unlocked_achievements[user_name] = []

    # Check achievements
    unlocked, total_xp = AchievementSystem.check_achievements(manager, user_name)

    # Update session state with newly unlocked achievements
    newly_unlocked = []
    for achievement_id in unlocked:
        if achievement_id not in st.session_state.unlocked_achievements[user_name]:
            newly_unlocked.append(achievement_id)
            st.session_state.unlocked_achievements[user_name].append(achievement_id)

    # Show newly unlocked achievements
    if newly_unlocked:
        for achievement_id in newly_unlocked:
            achievement = AchievementSystem.ACHIEVEMENTS[achievement_id]
            st.success(f"🎉 Neues Achievement freigeschaltet: **{achievement['name']}** (+{achievement['xp']} XP)")
            st.balloons()

    # Calculate level
    level, current_level_xp, next_level_xp = AchievementSystem.get_level_from_xp(total_xp)
    xp_in_level = total_xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp

    # Header with level and XP
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Level", level)
    col2.metric("Total XP", f"{total_xp:,}")
    col3.metric("Achievements", f"{len(unlocked)}/{len(AchievementSystem.ACHIEVEMENTS)}")
    col4.metric("Completion", f"{len(unlocked)/len(AchievementSystem.ACHIEVEMENTS)*100:.0f}%")

    # XP Progress bar
    st.markdown("### 📊 Level Progress")
    progress = xp_in_level / xp_needed if xp_needed > 0 else 1.0
    st.progress(progress)
    st.caption(f"{xp_in_level}/{xp_needed} XP bis Level {level + 1}")

    st.divider()

    # Tabs for different views
    tabs = st.tabs(["🏆 Meine Achievements", "🔒 Locked", "📈 Leaderboard", "📊 Statistiken"])

    # Tab 1: Unlocked Achievements
    with tabs[0]:
        st.subheader("🏆 Freigeschaltete Achievements")

        if not unlocked:
            st.info("Noch keine Achievements freigeschaltet. Starte dein erstes Projekt!")
        else:
            # Group by category
            categories = {}
            for achievement_id in unlocked:
                achievement = AchievementSystem.ACHIEVEMENTS[achievement_id]
                category = achievement['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append((achievement_id, achievement))

            # Display by category
            for category, achievements in sorted(categories.items()):
                st.markdown(f"#### {category}")

                cols = st.columns(3)
                for idx, (achievement_id, achievement) in enumerate(achievements):
                    col = cols[idx % 3]

                    with col:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #00cc9944 0%, #0099cc44 100%);
                            padding: 15px;
                            border-radius: 10px;
                            border-left: 4px solid #00cc99;
                            margin-bottom: 10px;
                        ">
                            <div style="font-size: 2em; text-align: center;">{achievement['name'].split()[0]}</div>
                            <div style="font-weight: bold; text-align: center; margin: 5px 0;">{' '.join(achievement['name'].split()[1:])}</div>
                            <div style="font-size: 0.85em; text-align: center; opacity: 0.8;">{achievement['description']}</div>
                            <div style="text-align: center; margin-top: 10px; color: #00cc99; font-weight: bold;">+{achievement['xp']} XP</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Tab 2: Locked Achievements
    with tabs[1]:
        st.subheader("🔒 Noch nicht freigeschaltet")

        locked = [aid for aid in AchievementSystem.ACHIEVEMENTS.keys() if aid not in unlocked]

        if not locked:
            st.success("🎉 Alle Achievements freigeschaltet! Du bist ein wahrer Meister!")
        else:
            # Group by category
            categories = {}
            for achievement_id in locked:
                achievement = AchievementSystem.ACHIEVEMENTS[achievement_id]
                category = achievement['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append((achievement_id, achievement))

            # Display by category
            for category, achievements in sorted(categories.items()):
                st.markdown(f"#### {category}")

                cols = st.columns(3)
                for idx, (achievement_id, achievement) in enumerate(achievements):
                    col = cols[idx % 3]

                    with col:
                        st.markdown(f"""
                        <div style="
                            background: #33333344;
                            padding: 15px;
                            border-radius: 10px;
                            border-left: 4px solid #666;
                            margin-bottom: 10px;
                            opacity: 0.6;
                        ">
                            <div style="font-size: 2em; text-align: center;">🔒</div>
                            <div style="font-weight: bold; text-align: center; margin: 5px 0;">{achievement['name']}</div>
                            <div style="font-size: 0.85em; text-align: center; opacity: 0.8;">{achievement['description']}</div>
                            <div style="text-align: center; margin-top: 10px; color: #888; font-weight: bold;">+{achievement['xp']} XP</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Tab 3: Leaderboard
    with tabs[2]:
        st.subheader("📈 Leaderboard")

        # Calculate leaderboard for all users
        leaderboard_data = []

        # Get all unique users from session state
        all_users = set([user_name])
        if 'unlocked_achievements' in st.session_state:
            all_users.update(st.session_state.unlocked_achievements.keys())

        for user in all_users:
            user_unlocked, user_xp = AchievementSystem.check_achievements(manager, user)
            user_level, _, _ = AchievementSystem.get_level_from_xp(user_xp)

            leaderboard_data.append({
                'User': user,
                'Level': user_level,
                'XP': user_xp,
                'Achievements': len(user_unlocked)
            })

        # Sort by XP
        leaderboard_data.sort(key=lambda x: x['XP'], reverse=True)

        # Display leaderboard
        for idx, entry in enumerate(leaderboard_data):
            rank_icon = {0: "🥇", 1: "🥈", 2: "🥉"}.get(idx, f"{idx+1}.")

            is_current_user = entry['User'] == user_name
            bg_color = "#00cc9922" if is_current_user else "#22222244"

            st.markdown(f"""
            <div style="
                background: {bg_color};
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                border-left: 4px solid {'#00cc99' if is_current_user else '#666'};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.5em;">{rank_icon}</div>
                    <div style="flex: 1; margin-left: 20px;">
                        <div style="font-weight: bold; font-size: 1.2em;">{entry['User']}</div>
                        <div style="font-size: 0.9em; opacity: 0.8;">Level {entry['Level']} • {entry['Achievements']} Achievements</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5em; font-weight: bold; color: #00cc99;">{entry['XP']:,}</div>
                        <div style="font-size: 0.8em; opacity: 0.8;">XP</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Tab 4: Statistics
    with tabs[3]:
        st.subheader("📊 Deine Statistiken")

        stats = AchievementSystem.calculate_user_stats(manager, user_name)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Projekte")
            st.metric("Gesamt Projekte", stats['total_projects'])
            st.metric("Abgeschlossene Projekte", stats['completed_projects'])
            st.metric("Gesunde Projekte", stats['healthy_projects'])
            st.metric("Im Budget", stats['on_budget_projects'])

            st.markdown("#### ⏱️ Zeit")
            st.metric("Erfasste Stunden", f"{stats['total_hours']:.1f}h")
            st.metric("Diese Woche", f"{stats['hours_this_week']:.1f}h")

        with col2:
            st.markdown("#### ✅ Tasks")
            st.metric("Gesamt Tasks", stats['total_tasks'])
            st.metric("Erledigte Tasks", stats['completed_tasks'])
            st.metric("Zugewiesene Tasks", stats['tasks_assigned'])

            st.markdown("#### 📚 Dokumentation")
            st.metric("Wiki-Seiten", stats['wiki_pages'])
            st.metric("Dokumente", stats['documents_uploaded'])

        # Achievement distribution pie chart
        st.markdown("#### 🎯 Achievement Verteilung")

        category_counts = {}
        for achievement_id in unlocked:
            achievement = AchievementSystem.ACHIEVEMENTS[achievement_id]
            category = achievement['category']
            category_counts[category] = category_counts.get(category, 0) + 1

        if category_counts:
            fig = go.Figure(data=[go.Pie(
                labels=list(category_counts.keys()),
                values=list(category_counts.values()),
                hole=0.4
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)


def track_feature_access(feature_name: str):
    """Track feature access for Explorer achievement"""
    if 'features_accessed' not in st.session_state:
        st.session_state.features_accessed = set()

    st.session_state.features_accessed.add(feature_name)
