import streamlit as st
import pandas as pd
import io
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    # --- LOGIQUE ET CALCULS ---
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
    total_ecoles_global = len(df_ecoles)
    total_po_global = df_ecoles['Commune'].nunique()
    total_active_with_schools = len([c for c in active_communes if c in df_ecoles['Commune'].values])

    # --- BANDEAU STATS ---
    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:16px;">
        <div style="flex:1; background:#4169E1; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Total Écoles</div>
            <div style="font-size:32px; font-weight:bold;">{total_ecoles_global}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Communes</div>
            <div style="font-size:32px; font-weight:bold;">{total_po_global}</div>
        </div>
        <div style="flex:1; background:#1e293b; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Actives</div>
            <div style="font-size:32px; font-weight:bold; color:#4ade80;">{total_active_with_schools}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- FILTRES ---
    if 't3_rc' not in st.session_state: st.session_state.t3_rc = 0
    c1, c2, c3 = st.columns([2, 3, 3])
    
    with c1:
        prov_tab3 = st.selectbox("🗺️ Province", ["Toutes"] + list(data_fwb.keys()), key=f"t3p_{st.session_state.t3_rc}")
    with c2:
        comm_list = data_fwb.get(prov_tab3, sorted(df_ecoles['Commune'].unique())) if prov_tab3 != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune_tab3 = st.selectbox("🏘️ Commune", [""] + comm_list, key=f"t3c_{st.session_state.t3_rc}")
    with c3:
        search_ecole = st.text_input("🔍 Recherche rapide", placeholder="Nom, Fase...", key=f"t3s_{st.session_state.t3_rc}")

    if commune_tab3:
        df_comm = df_ecoles[df_ecoles['Commune'] == commune_tab3].copy()
        is_active = commune_tab3 in active_communes
        
        # En-tête commune
        st.markdown(f"""<div style="background:#1e293b; color:white; padding:15px; border-radius:10px; margin-bottom:20px;">
            <span style="font-size:20px; font-weight:bold;">🏛️ {commune_tab3}</span>
            &nbsp;&nbsp; | &nbsp;&nbsp; {len(df_comm)} école(s)
        </div>""", unsafe_allow_html=True)

        # --- SECTION CONTACTS ---
        st.markdown("#### 👤 Contacts Extrascolaire")
        contacts_comm = df_contacts[df_contacts['Commune'] == commune_tab3].copy()
        
        if not contacts_comm.empty:
            for idx, ct in contacts_comm.iterrows():
                with st.expander(f"👤 {ct['Titre']} {ct['Nom']}"):
                    st.write(f"📞 {ct['Téléphone']} | 📱 {ct['GSM']} | ✉️ {ct['Email']}")
                    if st.button("🗑️ Supprimer", key=f"del_ct_{idx}"):
                        df_upd = df_contacts.drop(idx)
                        safe_write(conn, "Contacts", df_upd)
                        st.cache_data.clear()
                        st.rerun()

        with st.expander("➕ Ajouter un contact"):
            with st.form("add_ct"):
                f1, f2 = st.columns(2)
                t = f1.text_input("Titre (M., Mme)")
                n = f1.text_input("Nom")
                tel = f2.text_input("Tel")
                mail = f2.text_input("Email")
                if st.form_submit_button("Enregistrer"):
                    new_ct = pd.DataFrame([{"Province": prov_tab3, "Commune": commune_tab3, "Titre": t, "Nom": n, "Téléphone": tel, "Email": mail}])
                    safe_write(conn, "Contacts", pd.concat([df_contacts, new_ct]))
                    st.cache_data.clear()
                    st.rerun()

        # --- LISTE ÉCOLES ---
        st.markdown("#### 🏫 Liste des écoles")
        for _, school in df_comm.iterrows():
            st.markdown(f"""
            <div style="background:white; border:1px solid #eee; border-left:5px solid #4169E1; padding:10px; border-radius:8px; margin-bottom:5px;">
                <b>{school['Ecole']}</b> (Fase: {school['Fase école']})<br>
                <small>{school.get('Email', '-')}</small>
            </div>
            """, unsafe_allow_html=True)
