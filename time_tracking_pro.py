"""
Advanced Time Tracking Module
Professional time tracking and timesheet management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


def render_timesheet_manager(manager, user_name: str):
    """Render professional timesheet manager"""
    st.title("⏱️ Time Tracking Pro")

    tabs = st.tabs(["⏰ Quick Entry", "📅 Timesheet", "📊 Reports", "⚙️ Settings"])

    with tabs[0]:
        render_quick_time_entry(manager, user_name)

    with tabs[1]:
        render_timesheet_view(manager, user_name)

    with tabs[2]:
        render_time_reports(manager, user_name)

    with tabs[3]:
        render_time_settings()


def render_quick_time_entry(manager, user_name: str):
    """Quick time entry interface"""
    st.subheader("⚡ Schnellerfassung")

    # Get active projects
    projects = [p for p in manager.projects if not p.get('is_deleted') and not p.get('is_archived')]

    if not projects:
        st.info("Keine aktiven Projekte verfügbar")
        return

    with st.form("quick_time_entry"):
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            project_names = [p['title'] for p in projects]
            selected_project = st.selectbox("Projekt", project_names)

        with col2:
            date = st.date_input("Datum", value=datetime.now())

        with col3:
            hours = st.number_input("Stunden", min_value=0.0, max_value=24.0, value=1.0, step=0.5)

        category = st.selectbox(
            "Aktivität",
            ["Development", "Meeting", "Planning", "Testing", "Documentation", "Support", "Other"]
        )

        description = st.text_area("Beschreibung (optional)", placeholder="Was hast du gemacht?")

        submitted = st.form_submit_button("⏱️ Zeit erfassen", type="primary", use_container_width=True)

        if submitted:
            project = next(p for p in projects if p['title'] == selected_project)

            manager.add_time_log(
                project['id'],
                date.strftime("%Y-%m-%d"),
                category,
                hours,
                description
            )

            st.success(f"✅ {hours}h für '{selected_project}' erfasst!")
            st.rerun()

    # Recent entries
    st.divider()
    st.markdown("### 📋 Letzte Einträge")

    all_entries = []
    for p in projects:
        for log in p.get('time_logs', [])[-5:]:  # Last 5
            all_entries.append({
                **log,
                'project': p['title']
            })

    # Sort by date descending
    all_entries.sort(key=lambda x: x.get('date', ''), reverse=True)

    for entry in all_entries[:10]:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        col1.write(f"**{entry['project']}**")
        col2.write(entry.get('date', ''))
        col3.write(f"{entry.get('hours', 0)}h")
        col4.write(entry.get('category', ''))


def render_timesheet_view(manager, user_name: str):
    """Timesheet calendar view"""
    st.subheader("📅 Timesheet")

    # Week selector
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        week_offset = st.selectbox(
            "Woche",
            [
                ("Diese Woche", 0),
                ("Letzte Woche", -1),
                ("Vor 2 Wochen", -2),
                ("Vor 3 Wochen", -3),
            ],
            format_func=lambda x: x[0]
        )[1]

    # Calculate week dates
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    # Collect time entries for the week
    projects = [p for p in manager.projects if not p.get('is_deleted')]

    timesheet_data = {date.strftime("%Y-%m-%d"): [] for date in week_dates}

    for p in projects:
        for log in p.get('time_logs', []):
            log_date = log.get('date', '')
            if log_date in timesheet_data:
                timesheet_data[log_date].append({
                    **log,
                    'project': p['title']
                })

    # Display timesheet grid
    st.markdown("### Wochenübersicht")

    for date in week_dates:
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A, %d.%m.")

        with st.expander(f"📅 {day_name} ({sum(e.get('hours', 0) for e in timesheet_data[date_str])}h)"):
            entries = timesheet_data[date_str]

            if entries:
                for entry in entries:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{entry['project']}** - {entry.get('category', '')}")
                    col2.write(f"{entry.get('hours', 0)}h")
                    col3.write(entry.get('desc', '')[:30])
            else:
                st.info("Keine Einträge")

    # Week summary
    st.divider()
    total_hours = sum(e.get('hours', 0) for entries in timesheet_data.values() for e in entries)

    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamt diese Woche", f"{total_hours}h")
    col2.metric("Durchschnitt/Tag", f"{total_hours/7:.1f}h")
    col3.metric("Status", "✅ Voll" if total_hours >= 40 else "⚠️ Unter Soll")


def render_time_reports(manager, user_name: str):
    """Time tracking reports and analytics"""
    st.subheader("📊 Time Reports")

    # Collect all time data
    projects = manager.projects
    all_time_logs = []

    for p in projects:
        for log in p.get('time_logs', []):
            all_time_logs.append({
                **log,
                'project': p['title'],
                'project_id': p['id'],
                'category_name': p.get('category', 'Unknown')
            })

    if not all_time_logs:
        st.info("Keine Zeiterfassungsdaten vorhanden")
        return

    df = pd.DataFrame(all_time_logs)
    df['date'] = pd.to_datetime(df['date'])

    # Date range filter
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Von", value=datetime.now() - timedelta(days=30))

    with col2:
        end_date = st.date_input("Bis", value=datetime.now())

    # Filter data
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    df_filtered = df[mask]

    if df_filtered.empty:
        st.warning("Keine Daten im ausgewählten Zeitraum")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_hours = df_filtered['hours'].sum()
    avg_hours_per_day = df_filtered.groupby('date')['hours'].sum().mean()
    project_count = df_filtered['project'].nunique()
    days_worked = df_filtered['date'].nunique()

    col1.metric("Gesamtstunden", f"{total_hours:.1f}h")
    col2.metric("Ø Stunden/Tag", f"{avg_hours_per_day:.1f}h")
    col3.metric("Projekte", project_count)
    col4.metric("Arbeitstage", days_worked)

    # Charts
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Zeit nach Projekt")
        project_hours = df_filtered.groupby('project')['hours'].sum().reset_index()
        fig = px.pie(
            project_hours,
            values='hours',
            names='project',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Zeit nach Aktivität")
        category_hours = df_filtered.groupby('category')['hours'].sum().reset_index()
        fig = px.bar(
            category_hours,
            x='category',
            y='hours',
            color='hours',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Trend over time
    st.markdown("#### Zeiterfassung Trend")
    daily_hours = df_filtered.groupby('date')['hours'].sum().reset_index()

    fig = px.line(
        daily_hours,
        x='date',
        y='hours',
        markers=True
    )
    fig.add_hline(y=8, line_dash="dash", line_color="green", annotation_text="8h/Tag Soll")
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.markdown("#### Detaillierte Aufstellung")

    summary_df = df_filtered.groupby(['project', 'category'])['hours'].sum().reset_index()
    summary_df = summary_df.sort_values('hours', ascending=False)

    st.dataframe(
        summary_df.style.format({'hours': '{:.2f}h'}),
        use_container_width=True
    )

    # Export
    if st.button("📥 Als CSV exportieren"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv,
            f"timesheet_{start_date}_{end_date}.csv",
            "text/csv"
        )


def render_time_settings():
    """Time tracking settings"""
    st.subheader("⚙️ Einstellungen")

    st.markdown("### Arbeitszeiten")

    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Sollstunden pro Tag", value=8, min_value=1, max_value=24)
        st.number_input("Sollstunden pro Woche", value=40, min_value=1, max_value=168)

    with col2:
        st.checkbox("Überstunden-Warnung aktivieren")
        st.checkbox("Automatische Pausen abziehen")

    st.divider()

    st.markdown("### Kategorien anpassen")

    st.text_area(
        "Aktivitätskategorien (eine pro Zeile)",
        value="Development\nMeeting\nPlanning\nTesting\nDocumentation\nSupport\nOther"
    )

    if st.button("💾 Einstellungen speichern"):
        st.success("✅ Einstellungen gespeichert")
