"""
Theme Manager Module
Dark/Light mode and theme customization
"""

import streamlit as st


def render_theme_settings():
    """Render theme settings interface"""
    st.title("🎨 Theme Manager")

    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    if 'accent_color' not in st.session_state:
        st.session_state.accent_color = '#00cc99'

    # Theme selector
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Basis-Theme")

        theme = st.radio(
            "Wähle Theme",
            ['dark', 'light'],
            index=0 if st.session_state.theme == 'dark' else 1,
            format_func=lambda x: '🌙 Dark Mode' if x == 'dark' else '☀️ Light Mode'
        )

        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()

    with col2:
        st.markdown("### Akzentfarbe")

        accent_color = st.color_picker(
            "Hauptfarbe",
            value=st.session_state.accent_color
        )

        if accent_color != st.session_state.accent_color:
            st.session_state.accent_color = accent_color

    # Preview
    st.divider()
    st.markdown("### 👀 Vorschau")

    render_theme_preview(theme, accent_color)

    # Save button
    if st.button("💾 Theme übernehmen", type="primary", use_container_width=True):
        st.session_state.theme = theme
        st.session_state.accent_color = accent_color
        st.success("✅ Theme gespeichert!")
        st.balloons()
        st.rerun()


def render_theme_preview(theme, accent_color):
    """Render theme preview"""
    if theme == 'dark':
        bg_color = '#0e1117'
        text_color = '#fafafa'
        card_bg = '#262730'
    else:
        bg_color = '#ffffff'
        text_color = '#31333F'
        card_bg = '#f0f2f6'

    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            padding: 30px;
            border-radius: 10px;
            color: {text_color};
        ">
            <h2>Projekt Dashboard</h2>
            <p>Dies ist eine Vorschau des gewählten Themes.</p>

            <div style="
                background-color: {card_bg};
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                border-left: 4px solid {accent_color};
            ">
                <h3 style="color: {accent_color};">Beispiel-Projekt</h3>
                <p>Projektstatus: In Arbeit</p>
                <p>Progress: 75%</p>

                <div style="
                    background-color: {accent_color};
                    height: 10px;
                    width: 75%;
                    border-radius: 5px;
                    margin-top: 10px;
                "></div>
            </div>

            <button style="
                background-color: {accent_color};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                margin-top: 20px;
                cursor: pointer;
            ">
                Beispiel-Button
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )


def apply_theme():
    """Apply current theme to the app"""
    theme = st.session_state.get('theme', 'dark')
    accent_color = st.session_state.get('accent_color', '#00cc99')

    if theme == 'dark':
        st.markdown(
            f"""
            <style>
            :root {{
                --primary-color: {accent_color};
                --background-color: #0e1117;
                --secondary-background-color: #262730;
                --text-color: #fafafa;
            }}

            .stButton>button {{
                background-color: {accent_color};
                color: white;
            }}

            .stButton>button:hover {{
                background-color: {accent_color}dd;
                border-color: {accent_color};
            }}

            .stProgress > div > div > div > div {{
                background-color: {accent_color};
            }}

            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
                background-color: {accent_color};
            }}

            a {{
                color: {accent_color};
            }}

            .reportview-container .markdown-text-container {{
                color: #fafafa;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <style>
            :root {{
                --primary-color: {accent_color};
                --background-color: #ffffff;
                --secondary-background-color: #f0f2f6;
                --text-color: #31333F;
            }}

            .stApp {{
                background-color: #ffffff;
                color: #31333F;
            }}

            .stButton>button {{
                background-color: {accent_color};
                color: white;
            }}

            .stProgress > div > div > div > div {{
                background-color: {accent_color};
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


def get_theme_css():
    """Get CSS for current theme"""
    theme = st.session_state.get('theme', 'dark')
    accent_color = st.session_state.get('accent_color', '#00cc99')

    return f"""
    <style>
    /* Custom theme CSS */
    .metric-card {{
        background: linear-gradient(135deg, {accent_color}22 0%, {accent_color}11 100%);
        border-left: 4px solid {accent_color};
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }}

    .success-badge {{
        background-color: {accent_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
    }}

    .card-hover {{
        transition: transform 0.2s, box-shadow 0.2s;
    }}

    .card-hover:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px {accent_color}44;
    }}

    .accent-border {{
        border-left: 3px solid {accent_color};
    }}

    .accent-text {{
        color: {accent_color};
    }}

    .accent-bg {{
        background-color: {accent_color}22;
    }}
    </style>
    """
