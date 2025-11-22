import streamlit as st
import pandas as pd

def render_swot_analysis(manager, pid, project):
    st.subheader("🧩 SWOT Analyse")
    swot = project.get("swot", {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []})
    
    c1, c2 = st.columns(2)
    with c1:
        render_swot_box(manager, pid, swot, "strengths", "💪 Stärken (Strengths)", "green")
        render_swot_box(manager, pid, swot, "opportunities", "🚀 Chancen (Opportunities)", "blue")
    with c2:
        render_swot_box(manager, pid, swot, "weaknesses", "🔻 Schwächen (Weaknesses)", "orange")
        render_swot_box(manager, pid, swot, "threats", "⚡ Risiken (Threats)", "red")

def render_swot_box(manager, pid, swot_data, key, title, color):
    with st.container():
        st.markdown(f"##### :{color}[{title}]")
        with st.form(f"add_{key}"):
            val = st.text_input("Eintrag", label_visibility="collapsed")
            if st.form_submit_button("➕"):
                manager.add_swot(pid, key, val); st.rerun()
        
        for i, item in enumerate(swot_data[key]):
            c_t, c_d = st.columns([5, 1])
            c_t.markdown(f"- {item}")
            if c_d.button("x", key=f"del_{key}_{i}"):
                manager.delete_swot(pid, key, i); st.rerun()
        st.markdown("---")

def render_okr_manager(manager, pid, project):
    st.subheader("🎯 OKR Manager")
    st.caption("Objectives & Key Results")
    
    with st.expander("Neues Objective anlegen"):
        with st.form("new_okr"):
            obj = st.text_input("Objective (Ziel)")
            if st.form_submit_button("Anlegen"):
                manager.add_okr(pid, obj); st.rerun()
    
    okrs = project.get("okrs", [])
    for i, o in enumerate(okrs):
        with st.container():
            st.markdown(f"### 🥅 {o['objective']}")
            
            # Key Results
            krs = o.get("key_results", [])
            if krs:
                for kr in krs:
                    st.progress(kr['progress']/100, text=f"{kr['title']} ({kr['progress']}%)")
            
            # Add KR
            with st.popover("➕ Key Result hinzufügen"):
                with st.form(f"add_kr_{o['id']}"):
                    kr_t = st.text_input("Key Result")
                    kr_p = st.slider("Fortschritt", 0, 100, 0)
                    if st.form_submit_button("Speichern"):
                        manager.add_key_result(pid, o['id'], kr_t, kr_p); st.rerun()
            
            if st.button("Objective löschen", key=f"del_okr_{i}"):
                manager.delete_okr(pid, i); st.rerun()
            st.divider()

def render_retro_board(manager, pid, project):
    st.subheader("🔄 Retrospektive")
    
    with st.form("retro_input"):
        c1, c2, c3 = st.columns([1, 3, 1])
        cat = c1.selectbox("Kategorie", ["Start", "Stop", "Continue"])
        txt = c2.text_input("Feedback")
        if c3.form_submit_button("Posten"):
            manager.add_retro(pid, cat, txt); st.rerun()
            
    retros = project.get("retros", [])
    c_start, c_stop, c_cont = st.columns(3)
    
    with c_start:
        st.markdown("### 🟢 Start")
        for i, r in enumerate(retros):
            if r['category'] == "Start":
                st.info(r['text'])
                if st.button("x", key=f"dr_{i}"): manager.delete_retro(pid, i); st.rerun()
                
    with c_stop:
        st.markdown("### 🔴 Stop")
        for i, r in enumerate(retros):
            if r['category'] == "Stop":
                st.error(r['text'])
                if st.button("x", key=f"dr_{i}"): manager.delete_retro(pid, i); st.rerun()

    with c_cont:
        st.markdown("### 🔵 Continue")
        for i, r in enumerate(retros):
            if r['category'] == "Continue":
                st.success(r['text'])
                if st.button("x", key=f"dr_{i}"): manager.delete_retro(pid, i); st.rerun()