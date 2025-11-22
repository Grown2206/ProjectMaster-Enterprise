import streamlit as st
import time

class AuthManager:
    def __init__(self, project_manager):
        self.manager = project_manager
        
    def check_login(self):
        if 'user' not in st.session_state:
            st.session_state.user = None
            
        if st.session_state.user is None:
            self.render_login_screen()
            return False
        return True

    def render_login_screen(self):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.title("🔐 PM Suite Login")
            with st.form("login"):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    found_user = next((u for u in self.manager.users if u['username'] == user and u['password'] == pw), None)
                    if found_user:
                        st.session_state.user = found_user
                        st.success(f"Willkommen zurück, {found_user['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Falsche Zugangsdaten.")
            
            st.info("Default: admin / 123")

    def logout(self):
        st.session_state.user = None
        st.rerun()

    def current_user_name(self):
        return st.session_state.user['name'] if st.session_state.user else "Gast"

    def is_admin(self):
        return st.session_state.user and st.session_state.user.get('role') == 'Admin'