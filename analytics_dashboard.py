"""
Advanced Analytics Dashboard
Comprehensive analytics and insights for all projects
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter


def render_analytics_dashboard(manager):
    """Render comprehensive analytics dashboard"""
    st.title("📊 Advanced Analytics Dashboard")

    # Get all active projects
    projects = [p for p in manager.projects if not p.get('is_deleted') and not p.get('is_archived')]

    if not projects:
        st.info("Keine aktiven Projekte für Analytics vorhanden.")
        return

    # Tabs for different analytics views
    tabs = st.tabs([
        "📈 Overview",
        "💰 Financial",
        "👥 Team",
        "⏱️ Time",
        "📊 Performance",
        "🔮 Predictions"
    ])

    with tabs[0]:  # Overview
        render_overview_analytics(projects)

    with tabs[1]:  # Financial
        render_financial_analytics(projects, manager)

    with tabs[2]:  # Team
        render_team_analytics(projects)

    with tabs[3]:  # Time
        render_time_analytics(projects)

    with tabs[4]:  # Performance
        render_performance_analytics(projects)

    with tabs[5]:  # Predictions
        render_predictions(projects)


def render_overview_analytics(projects):
    """Overview KPIs and charts"""
    st.subheader("📈 Portfolio Overview")

    # Top KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    total_projects = len(projects)
    total_budget = sum(p.get('budget', {}).get('total', 0) for p in projects)
    total_tasks = sum(len(p.get('tasks', [])) for p in projects)
    completed_tasks = sum(len([t for t in p.get('tasks', []) if t.get('status') == 'Done']) for p in projects)
    avg_progress = sum(p.get('progress', 0) for p in projects) / len(projects) if projects else 0

    col1.metric("Projekte", total_projects)
    col2.metric("Gesamtbudget", f"€{total_budget:,.0f}")
    col3.metric("Tasks", f"{completed_tasks}/{total_tasks}")
    col4.metric("Ø Progress", f"{avg_progress:.1f}%")
    col5.metric("Team", len(set(m['name'] for p in projects for m in p.get('team', []))))

    st.divider()

    # Project Status Distribution
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Projektstatus Verteilung")
        status_counts = Counter(p.get('status', 'Unknown') for p in projects)
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Kategorien Verteilung")
        category_counts = Counter(p.get('category', 'Unknown') for p in projects)
        fig = px.bar(
            x=list(category_counts.keys()),
            y=list(category_counts.values()),
            color=list(category_counts.keys()),
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(showlegend=False, xaxis_title="Kategorie", yaxis_title="Anzahl")
        st.plotly_chart(fig, use_container_width=True)

    # Progress Heatmap
    st.markdown("#### Projekt-Fortschritt Heatmap")
    progress_data = []
    for p in projects:
        progress_data.append({
            'Projekt': p['title'][:20],
            'Kategorie': p.get('category', 'N/A'),
            'Progress': p.get('progress', 0),
            'Priority': p.get('priority', 'Med')
        })

    if progress_data:
        df = pd.DataFrame(progress_data)
        fig = px.scatter(
            df,
            x='Kategorie',
            y='Projekt',
            size='Progress',
            color='Priority',
            color_discrete_map={'High': 'red', 'Med': 'orange', 'Low': 'green'},
            size_max=30
        )
        st.plotly_chart(fig, use_container_width=True)


def render_financial_analytics(projects, manager):
    """Financial analytics and trends"""
    st.subheader("💰 Financial Analytics")

    # Budget Overview
    budget_data = []
    for p in projects:
        budget = p.get('budget', {})
        total = budget.get('total', 0)
        spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))

        budget_data.append({
            'Projekt': p['title'],
            'Budget': total,
            'Ausgaben': spent,
            'Rest': total - spent,
            'Auslastung': (spent / total * 100) if total > 0 else 0,
            'Kategorie': p.get('category', 'N/A')
        })

    df = pd.DataFrame(budget_data)

    # Budget vs Spent
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Budget vs. Ausgaben")
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Budget', x=df['Projekt'], y=df['Budget'], marker_color='lightblue'))
        fig.add_trace(go.Bar(name='Ausgaben', x=df['Projekt'], y=df['Ausgaben'], marker_color='salmon'))
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Budget Auslastung")
        fig = px.bar(
            df,
            x='Projekt',
            y='Auslastung',
            color='Auslastung',
            color_continuous_scale=['green', 'yellow', 'red'],
            range_color=[0, 120]
        )
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="100%")
        st.plotly_chart(fig, use_container_width=True)

    # Expense Categories
    st.markdown("#### Ausgaben nach Kategorie")
    all_expenses = []
    for p in projects:
        for expense in p.get('budget', {}).get('expenses', []):
            all_expenses.append({
                'Kategorie': expense.get('category', 'Other'),
                'Betrag': expense.get('amount', 0),
                'Projekt': p['title']
            })

    if all_expenses:
        df_exp = pd.DataFrame(all_expenses)
        fig = px.sunburst(
            df_exp,
            path=['Kategorie', 'Projekt'],
            values='Betrag',
            color='Betrag',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Financial Summary Table
    st.markdown("#### Financial Summary")
    summary_df = df[['Projekt', 'Budget', 'Ausgaben', 'Rest', 'Auslastung']].copy()
    summary_df['Auslastung'] = summary_df['Auslastung'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(
        summary_df.style.format({
            'Budget': '€{:,.2f}',
            'Ausgaben': '€{:,.2f}',
            'Rest': '€{:,.2f}'
        }),
        use_container_width=True
    )


def render_team_analytics(projects):
    """Team performance and workload analytics"""
    st.subheader("👥 Team Analytics")

    # Collect team data
    team_workload = {}
    for p in projects:
        for member in p.get('team', []):
            name = member['name']
            if name not in team_workload:
                team_workload[name] = {
                    'projects': 0,
                    'roles': set(),
                    'tasks': 0,
                    'completed_tasks': 0
                }

            team_workload[name]['projects'] += 1
            team_workload[name]['roles'].add(member.get('role', 'Unknown'))

        # Count assigned tasks
        for task in p.get('tasks', []):
            assignee = task.get('assignee')
            if assignee and assignee in team_workload:
                team_workload[assignee]['tasks'] += 1
                if task.get('status') == 'Done':
                    team_workload[assignee]['completed_tasks'] += 1

    if not team_workload:
        st.info("Keine Team-Daten verfügbar.")
        return

    # Team Workload
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Team Auslastung")
        workload_df = pd.DataFrame([
            {
                'Name': name,
                'Projekte': data['projects'],
                'Tasks': data['tasks'],
                'Erledigt': data['completed_tasks']
            }
            for name, data in team_workload.items()
        ])

        fig = px.bar(
            workload_df,
            x='Name',
            y=['Projekte', 'Tasks'],
            barmode='group',
            color_discrete_sequence=['#636EFA', '#EF553B']
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Task Completion Rate")
        completion_df = workload_df.copy()
        completion_df['Rate'] = (completion_df['Erledigt'] / completion_df['Tasks'] * 100).fillna(0)

        fig = px.bar(
            completion_df,
            x='Name',
            y='Rate',
            color='Rate',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        fig.update_layout(yaxis_title="Completion Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    # Team Roles Distribution
    st.markdown("#### Rollen-Verteilung")
    all_roles = []
    for data in team_workload.values():
        all_roles.extend(list(data['roles']))

    role_counts = Counter(all_roles)
    fig = px.pie(
        values=list(role_counts.values()),
        names=list(role_counts.keys()),
        hole=0.3
    )
    st.plotly_chart(fig, use_container_width=True)


def render_time_analytics(projects):
    """Time tracking analytics"""
    st.subheader("⏱️ Time Analytics")

    # Collect time logs
    all_time_logs = []
    for p in projects:
        for log in p.get('time_logs', []):
            all_time_logs.append({
                'Projekt': p['title'],
                'Datum': log.get('date', ''),
                'Kategorie': log.get('category', 'Unknown'),
                'Stunden': log.get('hours', 0)
            })

    if not all_time_logs:
        st.info("Keine Zeiterfassungs-Daten verfügbar.")
        return

    df = pd.DataFrame(all_time_logs)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Zeitaufwand nach Projekt")
        project_time = df.groupby('Projekt')['Stunden'].sum().reset_index()
        fig = px.bar(
            project_time,
            x='Projekt',
            y='Stunden',
            color='Stunden',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Zeitaufwand nach Kategorie")
        category_time = df.groupby('Kategorie')['Stunden'].sum().reset_index()
        fig = px.pie(
            category_time,
            values='Stunden',
            names='Kategorie',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    # Time Trend
    st.markdown("#### Zeiterfassung Trend")
    df['Datum'] = pd.to_datetime(df['Datum'])
    daily_time = df.groupby('Datum')['Stunden'].sum().reset_index()

    fig = px.line(
        daily_time,
        x='Datum',
        y='Stunden',
        markers=True
    )
    fig.update_layout(xaxis_title="Datum", yaxis_title="Stunden")
    st.plotly_chart(fig, use_container_width=True)


def render_performance_analytics(projects):
    """Project performance metrics"""
    st.subheader("📊 Performance Metrics")

    # Calculate performance scores
    performance_data = []
    for p in projects:
        # Task completion rate
        tasks = p.get('tasks', [])
        task_completion = len([t for t in tasks if t.get('status') == 'Done']) / len(tasks) * 100 if tasks else 0

        # Budget efficiency
        budget = p.get('budget', {})
        total = budget.get('total', 1)
        spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))
        budget_efficiency = (1 - abs(spent - total) / total) * 100 if total > 0 else 0

        # Overall score
        progress = p.get('progress', 0)
        overall_score = (task_completion * 0.4 + budget_efficiency * 0.3 + progress * 0.3)

        performance_data.append({
            'Projekt': p['title'],
            'Task Rate': task_completion,
            'Budget Effizienz': budget_efficiency,
            'Progress': progress,
            'Overall Score': overall_score,
            'Status': p.get('status', 'Unknown')
        })

    df = pd.DataFrame(performance_data)

    # Performance Scatter
    fig = px.scatter(
        df,
        x='Budget Effizienz',
        y='Task Rate',
        size='Progress',
        color='Overall Score',
        hover_name='Projekt',
        color_continuous_scale='RdYlGn',
        size_max=30
    )
    fig.update_layout(
        xaxis_title="Budget Effizienz (%)",
        yaxis_title="Task Completion Rate (%)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Performance Ranking
    st.markdown("#### Performance Ranking")
    ranking_df = df.sort_values('Overall Score', ascending=False)
    ranking_df['Rang'] = range(1, len(ranking_df) + 1)

    st.dataframe(
        ranking_df[['Rang', 'Projekt', 'Overall Score', 'Task Rate', 'Budget Effizienz', 'Progress']].style.format({
            'Overall Score': '{:.1f}',
            'Task Rate': '{:.1f}%',
            'Budget Effizienz': '{:.1f}%',
            'Progress': '{:.1f}%'
        }).background_gradient(subset=['Overall Score'], cmap='RdYlGn'),
        use_container_width=True
    )


def render_predictions(projects):
    """Predictive analytics and forecasts"""
    st.subheader("🔮 Predictions & Forecasts")

    st.info("🚀 AI-Powered Predictions (Beta)")

    # Project completion predictions
    st.markdown("#### Geschätzte Fertigstellung")

    predictions = []
    for p in projects:
        if p.get('status') not in ['Abgeschlossen', 'Abgebrochen']:
            progress = p.get('progress', 0)

            # Simple linear prediction based on progress
            if progress > 0:
                # Estimate days to completion
                created = datetime.strptime(p.get('created_at', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
                days_elapsed = (datetime.now() - created).days

                if days_elapsed > 0:
                    days_per_percent = days_elapsed / progress if progress > 0 else 1
                    remaining_days = int(days_per_percent * (100 - progress))
                    completion_date = datetime.now() + timedelta(days=remaining_days)

                    predictions.append({
                        'Projekt': p['title'],
                        'Progress': progress,
                        'Voraussichtlich fertig': completion_date.strftime("%Y-%m-%d"),
                        'Tage verbleibend': remaining_days,
                        'Risiko': 'Hoch' if remaining_days > 90 else 'Mittel' if remaining_days > 30 else 'Niedrig'
                    })

    if predictions:
        df = pd.DataFrame(predictions)

        fig = px.scatter(
            df,
            x='Progress',
            y='Tage verbleibend',
            size='Tage verbleibend',
            color='Risiko',
            hover_name='Projekt',
            color_discrete_map={'Niedrig': 'green', 'Mittel': 'orange', 'Hoch': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)
    else:
        st.info("Keine laufenden Projekte für Vorhersagen.")

    # Budget predictions
    st.markdown("#### Budget-Prognosen")

    budget_predictions = []
    for p in projects:
        budget = p.get('budget', {})
        total = budget.get('total', 0)
        spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))
        progress = p.get('progress', 1)

        if progress > 0 and total > 0:
            projected_total = (spent / progress) * 100
            variance = projected_total - total

            budget_predictions.append({
                'Projekt': p['title'],
                'Budget': total,
                'Ausgaben': spent,
                'Projiziert': projected_total,
                'Varianz': variance,
                'Varianz %': (variance / total * 100) if total > 0 else 0
            })

    if budget_predictions:
        df_budget = pd.DataFrame(budget_predictions)

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Budget', x=df_budget['Projekt'], y=df_budget['Budget'], marker_color='lightblue'))
        fig.add_trace(go.Bar(name='Projiziert', x=df_budget['Projekt'], y=df_budget['Projiziert'], marker_color='salmon'))
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
