import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

def render_calendar_view(manager, pid, project):
    st.subheader("📅 Monatskalender")
    
    # Simple Grid Calendar Logic
    year = datetime.now().year
    month = datetime.now().month
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.markdown(f"### {month_name} {year}")
    
    # Events sammeln
    events = {}
    
    # Deadline
    if project.get('deadline'):
        try:
            d = datetime.strptime(project['deadline'], "%Y-%m-%d")
            if d.month == month and d.year == year:
                events.setdefault(d.day, []).append("🏁 Deadline")
        except: pass
        
    # Milestones
    for m in project.get('milestones', []):
        try:
            d = datetime.strptime(m['date'], "%Y-%m-%d")
            if d.month == month and d.year == year:
                events.setdefault(d.day, []).append(f"🔹 {m['title']}")
        except: pass
        
    # Created Tasks (optional)
    # ... kann erweitert werden
    
    # Render Grid
    cols = st.columns(7)
    days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    for i, day in enumerate(days):
        cols[i].markdown(f"**{day}**")
        
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                with cols[i]:
                    st.write(f"**{day}**")
                    if day in events:
                        for e in events[day]:
                            st.markdown(f"<div style='font-size:0.7em; background:#333; padding:2px; border-radius:3px'>{e}</div>", unsafe_allow_html=True)
                    st.write("---")