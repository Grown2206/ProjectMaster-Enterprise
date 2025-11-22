import streamlit as st

def render_wiki(manager, pid, project):
    st.subheader("🧠 Projekt Wiki")
    
    pages = project.get("wiki_pages", [])
    
    # Sidebar Navigation für Wiki (innerhalb des Tabs)
    page_titles = ["Startseite"] + [p['title'] for p in pages]
    selection = st.radio("Seite wählen", page_titles, horizontal=True)
    
    st.divider()
    
    if selection == "Startseite":
        st.markdown(f"# Willkommen im Wiki von {project['title']}")
        st.write("Nutze dieses Wiki für Dokumentation, Konzepte und Onboarding-Guides.")
        
        with st.expander("Neue Seite erstellen", expanded=True):
            with st.form("new_page"):
                pt = st.text_input("Seitentitel")
                pc = st.text_area("Inhalt (Markdown)")
                if st.form_submit_button("Seite speichern"):
                    manager.add_wiki_page(pid, pt, pc); st.rerun()
    else:
        # Find page
        page_idx = next((i for i, p in enumerate(pages) if p['title'] == selection), None)
        if page_idx is not None:
            page = pages[page_idx]
            st.markdown(f"## {page['title']}")
            st.markdown(page['content'])
            
            with st.expander("Seite bearbeiten"):
                new_content = st.text_area("Inhalt bearbeiten", value=page['content'], height=300)
                if st.button("Änderungen speichern"):
                    manager.update_wiki_page(pid, page_idx, page['title'], new_content); st.rerun()
                if st.button("Seite löschen", type="primary"):
                    manager.delete_wiki_page(pid, page_idx); st.rerun()

def render_backlog(manager, pid, project):
    st.subheader("💡 Ideen-Backlog (Icebox)")
    st.caption("Ideen sammeln, die noch keine konkreten Tasks sind.")
    
    with st.form("backlog_add"):
        c1, c2, c3 = st.columns([3, 1, 1])
        bt = c1.text_input("Idee")
        bp = c2.selectbox("Prio", ["Low", "Mid", "High"])
        if c3.form_submit_button("Hinzufügen"):
            manager.add_backlog_item(pid, bt, bp, ""); st.rerun()
            
    items = project.get("backlog", [])
    if items:
        for i, item in enumerate(items):
            prio_color = "red" if item['priority']=="High" else "orange" if item['priority']=="Mid" else "green"
            with st.container():
                c1, c2, c3 = st.columns([0.5, 4, 1])
                c1.markdown(f":{prio_color}[●]")
                c2.write(item['title'])
                
                # Button um Idee zu Task zu machen
                if c3.button("➡ Task", key=f"conv_{i}", help="In Task umwandeln"):
                    manager.add_task(pid, item['title'])
                    manager.delete_backlog_item(pid, i)
                    st.success("In Task umgewandelt!")
                    st.rerun()
                    
                if c3.button("🗑", key=f"del_bl_{i}"):
                    manager.delete_backlog_item(pid, i); st.rerun()
    else:
        st.info("Das Backlog ist leer. Sei kreativ!")