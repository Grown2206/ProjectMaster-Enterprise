import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

def render_global_dashboard(manager):
    st.title("🌍 Global Project View")
    
    # Tabs für Global Views
    tabs = st.tabs(["📊 Overview", "📰 Activity Feed", "🏷️ Tag Manager", "👥 Resources"])
    
    projects = [p for p in manager.projects if not p.get('is_archived') and not p.get('is_deleted')]
    
    if not projects:
        st.info("Keine aktiven Projekte.")
        return

    # --- TAB 1: Overview ---
    with tabs[0]:
        st.subheader("📅 Multi-Projekt Timeline")
        gantt_data = []
        for p in projects:
            if p['start_date'] and p['deadline']:
                gantt_data.append(dict(
                    Project=p['title'], Start=p['start_date'], Finish=p['deadline'], 
                    Status=p['status'], Progress=p['progress']
                ))
        if gantt_data:
            df = pd.DataFrame(gantt_data)
            fig = px.timeline(df, x_start="Start", x_end="Finish", y="Project", color="Status", text="Progress")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔥 Top Risiken (Global)")
        all_risks = []
        for p in projects:
            for r in p['risks']:
                score = r['prob'] * r['impact']
                if score >= 16: 
                    all_risks.append({"Project": p['title'], "Risk": r['desc'], "Score": score})
        
        if all_risks:
            df_risk = pd.DataFrame(all_risks).sort_values("Score", ascending=False)
            # Use simple dataframe without matplotlib styling
            st.dataframe(df_risk, use_container_width=True)
        else:
            st.success("Keine kritischen Risiken.")

    # --- TAB 2: Activity Feed ---
    with tabs[1]:
        st.subheader("📰 Live Ticker")
        all_activities = []
        for p in projects:
            for a in p.get('activity_log', []):
                # Add Project Title context if missing
                if 'project_title' not in a: a['project_title'] = p['title']
                all_activities.append(a)
        
        # Sort by Date Descending
        all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for act in all_activities[:50]: # Show last 50
            st.markdown(f"**{act['timestamp']}** | `{act.get('project_title', '?')}`: {act['action']}")
            st.divider()

    # --- TAB 3: Tag Manager ---
    with tabs[2]:
        st.subheader("🏷️ Tag Management")
        all_tags = sorted(list(set([t for p in projects for t in p.get('tags', [])])))
        st.write(f"Gefundene Tags: {', '.join(all_tags)}")
        
        with st.form("rename_tag"):
            c1, c2 = st.columns(2)
            old_t = c1.selectbox("Tag auswählen", all_tags)
            new_t = c2.text_input("Neuer Name")
            if st.form_submit_button("Umbenennen"):
                count = 0
                for p in manager.projects:
                    if old_t in p.get('tags', []):
                        p['tags'] = [new_t if x == old_t else x for x in p['tags']]
                        count += 1
                manager.save_data()
                st.success(f"Tag '{old_t}' in {count} Projekten zu '{new_t}' geändert.")
                st.rerun()

    # --- TAB 4: Resources ---
    with tabs[3]:
        st.subheader("👥 Team Auslastung")
        team_data = []
        for p in projects:
            for m in p['team']:
                team_data.append({"Name": m['name'], "Project": p['title'], "Role": m['role']})
        
        if team_data:
            df_team = pd.DataFrame(team_data)
            load = df_team['Name'].value_counts().reset_index()
            load.columns = ['Name', 'Project_Count']
            
            c1, c2 = st.columns(2)
            with c1: st.dataframe(load, use_container_width=True)
            with c2:
                fig_load = px.bar(load, x='Name', y='Project_Count', title="Projekte pro Person")
                st.plotly_chart(fig_load, use_container_width=True)