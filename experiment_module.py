import streamlit as st
import pandas as pd
import os
import uuid # FIX: UUID Modul Importiert
from datetime import datetime
from utils import save_uploaded_image

def render_lab_dashboard(manager):
    st.title("🧪 Labor & Versuche")
    
    tab1, tab2 = st.tabs(["📋 Versuchsübersicht", "➕ Neuer Versuch"])
    
    with tab1:
        experiments = manager.experiments
        if not experiments:
            st.info("Keine Versuche. Erstelle den ersten!")
        else:
            # Sortierung: Neueste zuerst
            experiments.sort(key=lambda x: x['created_at'], reverse=True)
            
            for exp in experiments:
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.markdown(f"**{exp['name']}**")
                    # FIX: .get() benutzen um KeyError zu vermeiden
                    c1.caption(f"{exp.get('category', 'Sonstiges')} | Prüfer: {exp.get('tester', 'N/A')}")
                    c2.write(f"Status: `{exp.get('status', 'Geplant')}`")
                    c2.write(f"Muster: {len(exp['samples'])} Stk.")
                    if c3.button("Öffnen", key=f"open_{exp['id']}"):
                        st.session_state.selected_experiment_id = exp['id']
                        st.session_state.view = 'experiment_details'
                        st.rerun()
                    st.divider()

    with tab2:
        st.subheader("Versuchsanforderung erstellen")
        with st.form("new_exp"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Titel (z.B. Chem. Beständigkeit Edelstahl)")
            cat = c2.selectbox("Kategorie", ["Chemische Prüfung", "Mechanische Dauerprüfung", "Klimatest", "Funktionstest", "Validierung"])
            desc = st.text_area("Zielsetzung & Parameter")
            tester = st.text_input("Verantwortlicher Prüfer", value=st.session_state.auth.current_user_name())
            
            if st.form_submit_button("Versuch anlegen"):
                manager.add_experiment(name, desc, cat, tester)
                st.success("Erstellt! Wechsel jetzt in die Details, um die Matrix zu definieren.")
                st.rerun()

def render_experiment_details(manager):
    eid = st.session_state.selected_experiment_id
    exp = manager.get_experiment(eid)
    
    if not exp:
        st.error("Versuch nicht gefunden."); 
        if st.button("Zurück"): st.session_state.view = 'lab'; st.rerun()
        return

    # Header
    c_back, c_title = st.columns([1, 8])
    c_back.button("⬅ Labor", on_click=lambda: setattr(st.session_state, 'view', 'lab'))
    c_title.title(exp['name'])
    st.caption(f"Kategorie: {exp.get('category', 'N/A')} | Datum: {exp['created_at']}")

    tabs = st.tabs(["🧪 Versuchs-Setup", "📝 Datenerfassung", "📸 Fotodokumentation", "📄 Bericht & Abschluss"])

    # --- TAB 1: SETUP (Struktur definieren) ---
    with tabs[0]:
        st.info("Definiere hier deine Tabelle. Du kannst eine Vorlage laden oder Zeilen/Spalten manuell eingeben.")
        
        # NEXT LEVEL: Vorlagen aus den hochgeladenen Dokumenten
        PRESETS = {
            "Leere Vorlage": ([], []),
            "Chemische Beständigkeit (Pero Chlor)": (
                ["Blech 01 (V2A glasgeperlt)", "Blech 02 (V2A blank)", "Blech 03 (V2A geschliffen)", "Blech 04 (V4A glasgeperlt)", "Blech 05 (V4A geschliffen)", "Blech 06 (V4A blank)", "Blech 07 (V4A)", "Blech 11 (RA 1,77-1,96)"],
                ["Woche 1 (5% spülen)", "Woche 2 (15% spülen)", "Woche 3 (15% trocken)", "Woche 4 (15% trocken)", "Gesamtbewertung"]
            ),
            "Bauteil Validierung (Vergleichstest)": (
                ["Muster A (KK Metal)", "Muster B (Laswell)", "Muster C (HSM Part)"],
                ["Schweißnähte", "Teflondichtung", "Maßhaltigkeit Welle", "Funktion", "Gesamturteil"]
            ),
            "Dauertest (Pneumatik)": (
                ["Prüfling 1", "Prüfling 2", "Prüfling 3"],
                ["Zyklen", "Druck (bar)", "Schaltzeit (ms)", "Leckage (ml/min)", "Verschleiß"]
            )
        }
        
        # Preset Loader
        c_load, c_btn = st.columns([3, 1])
        sel_preset = c_load.selectbox("Schnellvorlage laden", list(PRESETS.keys()))
        
        # Init State Variablen
        if "temp_samples" not in st.session_state:
            st.session_state.temp_samples = "\n".join([s['name'] for s in exp['samples']])
        if "temp_cols" not in st.session_state:
            st.session_state.temp_cols = ", ".join(exp.get('matrix_columns', ['Ergebnis']))

        if c_btn.button("Vorlage anwenden"):
            samps, cols = PRESETS[sel_preset]
            st.session_state.temp_samples = "\n".join(samps)
            st.session_state.temp_cols = ", ".join(cols)
            st.rerun()

        # Editor
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 1. Prüflinge (Zeilen)")
            new_samples_str = st.text_area("Muster/Proben (eine pro Zeile)", value=st.session_state.temp_samples, height=200, key="ta_samples")
            
        with col2:
            st.markdown("#### 2. Prüfkriterien (Spalten)")
            new_cols_str = st.text_area("Spalten (kommagetrennt)", value=st.session_state.temp_cols, height=200, key="ta_cols")

        if st.button("Struktur speichern & Tabelle generieren", type="primary"):
            # Parse Samples
            sample_list = []
            for line in new_samples_str.split('\n'):
                if line.strip():
                    # Versuche ID zu behalten wenn Name gleich bleibt, sonst neu
                    existing = next((s for s in exp['samples'] if s['name'] == line.strip()), None)
                    if existing: sample_list.append(existing)
                    else: sample_list.append({"id": str(uuid.uuid4()), "name": line.strip()}) # FIX: uuid Aufruf
            
            # Parse Columns
            col_list = [c.strip() for c in new_cols_str.split(',') if c.strip()]
            
            # Datenmigration: Versuche alte Werte zu retten
            old_data = {d['sample_id']: d for d in exp.get('matrix_data', [])}
            new_data = []
            
            for samp in sample_list:
                row_obj = {"sample_id": samp['id'], "sample_name": samp['name']}
                old_row = old_data.get(samp['id'], {})
                for col in col_list:
                    row_obj[col] = old_row.get(col, "")
                new_data.append(row_obj)
                
            manager.update_experiment_matrix(eid, sample_list, col_list, new_data)
            st.session_state.temp_samples = new_samples_str 
            st.session_state.temp_cols = new_cols_str
            st.success("Struktur erfolgreich aktualisiert! Wechsel zum Reiter 'Datenerfassung'.")

    # --- TAB 2: DATENERFASSUNG (Matrix) ---
    with tabs[1]:
        if not exp['samples'] or not exp['matrix_columns']:
            st.warning("Bitte erst im Tab 'Versuchs-Setup' Muster und Spalten definieren.")
        else:
            st.markdown("### Messwerte & Ergebnisse")
            st.caption("Tipp: Doppelklick in eine Zelle zum Bearbeiten.")
            
            df_source = pd.DataFrame(exp['matrix_data'])
            if not df_source.empty:
                df_display = df_source.set_index("sample_name")
                display_cols = exp['matrix_columns']
                
                # EDITABLE DATAFRAME
                edited_df = st.data_editor(df_display[display_cols], use_container_width=True, num_rows="fixed", height=400)
                
                if st.button("💾 Daten speichern"):
                    save_list = []
                    for samp in exp['samples']:
                        row_data = {"sample_id": samp['id'], "sample_name": samp['name']}
                        if samp['name'] in edited_df.index:
                            for col in exp['matrix_columns']:
                                row_data[col] = edited_df.loc[samp['name'], col]
                        save_list.append(row_data)
                    
                    manager.update_experiment_matrix(eid, exp['samples'], exp['matrix_columns'], save_list)
                    st.success("Daten gesichert!")

    # --- TAB 3: FOTOS ---
    with tabs[2]:
        st.subheader("Bilddokumentation")
        
        with st.form("upload_exp_img", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f = c1.file_uploader("Bild wählen", type=['png', 'jpg'])
            caption = c2.text_input("Beschreibung (z.B. Rissbildung Muster B)")
            if st.form_submit_button("Hochladen") and f:
                path = save_uploaded_image(f, f"EXP_{eid}")
                manager.add_experiment_image(eid, path, caption)
                st.rerun()
        
        if exp['images']:
            cols = st.columns(3)
            for i, img in enumerate(exp['images']):
                with cols[i % 3]:
                    if os.path.exists(img['path']):
                        st.image(img['path'], use_container_width=True)
                        st.caption(img['caption'])
                    else:
                        st.error("Bild fehlt")
                    if st.button("Löschen", key=f"del_e_img_{i}"):
                        manager.delete_experiment_image(eid, i)
                        st.rerun()

    # --- TAB 4: BERICHT ---
    with tabs[3]:
        st.subheader("Bewertung & Abschluss")
        
        curr_sum = exp.get("result_summary", "")
        new_sum = st.text_area("Zusammenfassung / Fazit / Empfehlung", value=curr_sum, height=200)
        
        c1, c2 = st.columns(2)
        options = ["Geplant", "Laufend", "Abgeschlossen", "Abbruch"]
        try:
            current_index = options.index(exp.get('status', 'Geplant'))
        except ValueError:
            current_index = 0
            
        conc = c1.selectbox("Gesamturteil", ["Offen", "Freigabe", "Bedingte Freigabe", "Keine Freigabe"], index=["Offen", "Freigabe", "Bedingte Freigabe", "Keine Freigabe"].index(exp.get('conclusion', 'Offen')))
        stat = c2.selectbox("Status", options, index=current_index)
        
        if st.button("Bericht speichern"):
            manager.update_experiment_meta(eid, new_sum, conc, stat)
            st.success("Gespeichert!")
            
        st.divider()
        
        from pdf_export import create_lab_report_pdf
        if st.button("📄 PDF Prüfbericht erstellen"):
            path = create_lab_report_pdf(exp)
            if path:
                with open(path, "rb") as f:
                    st.download_button("Download Prüfbericht", f, file_name=f"Pruefbericht_{exp['name']}.pdf")
            else:
                st.error("PDF Erstellung fehlgeschlagen.")