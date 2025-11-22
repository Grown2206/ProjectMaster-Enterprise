import streamlit as st

def render_qa_dashboard(manager, pid, project):
    st.subheader("🧪 Quality Assurance (QA)")
    
    tab1, tab2 = st.tabs(["Test Fälle", "Test Ausführung"])
    
    # --- TEST CASES ---
    with tab1:
        with st.expander("Neuen Testfall erstellen"):
            with st.form("new_test"):
                tt = st.text_input("Titel")
                ts = st.text_area("Schritte (Steps)")
                te = st.text_area("Erwartetes Ergebnis")
                if st.form_submit_button("Speichern"):
                    manager.add_test_case(pid, tt, ts, te)
                    st.rerun()
        
        tests = project.get("test_cases", [])
        if not tests:
            st.info("Keine Testfälle definiert.")
        else:
            for i, t in enumerate(tests):
                status_color = "green" if t['status'] == "Pass" else "red" if t['status'] == "Fail" else "grey"
                with st.expander(f":{status_color}[[{t['status']}]] {t['title']}"):
                    st.write(f"**Steps:**\n{t['steps']}")
                    st.write(f"**Expected:**\n{t['expected']}")
                    if t['last_run']:
                        st.caption(f"Zuletzt geprüft: {t['last_run']}")
                    
                    if st.button("Löschen", key=f"del_tc_{i}"):
                        manager.delete_test_case(pid, i)
                        st.rerun()

    # --- EXECUTION ---
    with tab2:
        st.write("Führe Tests aus und dokumentiere das Ergebnis.")
        tests = project.get("test_cases", [])
        
        passed = len([t for t in tests if t['status'] == "Pass"])
        failed = len([t for t in tests if t['status'] == "Fail"])
        
        if tests:
            col1, col2 = st.columns(2)
            col1.metric("Pass Rate", f"{int(passed/len(tests)*100)}%")
            col2.metric("Failed", failed)
            st.progress(passed/len(tests))
        
        st.divider()
        
        for t in tests:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{t['title']}**")
            if c2.button("✅ Pass", key=f"pass_{t['id']}"):
                manager.update_test_status(pid, t['id'], "Pass")
                st.rerun()
            if c3.button("❌ Fail", key=f"fail_{t['id']}"):
                manager.update_test_status(pid, t['id'], "Fail")
                st.rerun()