import streamlit as st
import pandas as pd
import io
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
    
    # BANDEAU STATS ORIGINAL
    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:16px;">
        <div style="flex:1; background:#4169E1; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Total Écoles</div>
            <div style="font-size:38px; font-weight:bold;">{len(df_ecoles)}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Communes</div>
            <div style="font-size:38px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
        </div>
        <div style="flex:1; background:#1e293b; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Actives</div>
            <div style="font-size:38px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FILTRES
    if 't3_rc' not in st.session_state: st.session_state.t3_rc = 0
    c1, c2, c3 = st.columns([2, 3, 3])
    with c1:
        prov_tab3 = st.selectbox("🗺️ Province", ["Toutes"] + list(data_fwb.keys()), key=f"t3p_{st.session_state.t3_rc}")
    with c2:
        comm_opts = data_fwb.get(prov_tab3, sorted(df_ecoles['Commune'].unique())) if prov_tab3 != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune_tab3 = st.selectbox("🏘️ Commune", [""] + comm_opts, key=f"t3c_{st.session_state.t3_rc}")
    with c3:
        search_ecole = st.text_input("🔍 Rechercher", placeholder="Nom d'école, fase...", key=f"t3s_{st.session_state.t3_rc}")

    if commune_tab3:
        df_comm = df_ecoles[df_ecoles['Commune'] == commune_tab3].copy()
        
        # Header Commune Bleu Foncé
        st.markdown(f'<div style="background:#1e293b; color:white; padding:13px 20px; border-radius:10px; margin-bottom:14px;">'
                    f'<span style="font-size:20px; font-weight:bold;">🏛️ {commune_tab3}</span></div>', unsafe_allow_html=True)

        # CONTACTS (Mise en page originale)
        contacts_comm = df_contacts[df_contacts['Commune'] == commune_tab3].copy()
        if not contacts_comm.empty:
            st.markdown("<div style='font-size:13px; font-weight:700; color:#7c3aed; margin-bottom:8px;'>👤 Contacts extrascolaire</div>", unsafe_allow_html=True)
            cols_c = st.columns(3)
            for i, (idx, ct) in enumerate(contacts_comm.iterrows()):
                with cols_c[i % 3]:
                    st.markdown(f'<div style="background:#f5f3ff; border-left:5px solid #7c3aed; padding:10px; border-radius:8px; font-size:11px;">'
                                f'<b>{ct["Titre"]} {ct["Nom"]}</b><br>📞 {ct["Téléphone"]}<br>✉️ {ct["Email"]}</div>', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_ct_{idx}"):
                        safe_write(conn, "Contacts", df_contacts.drop(idx))
                        st.rerun()

        # ÉCOLES EN 2 COLONNES (RETOUR DU CODE ORIGINAL)
        st.divider()
        df_display = df_comm[df_comm['Ecole'].str.contains(search_ecole, case=False, na=False)] if search_ecole else df_comm
        
        for i in range(0, len(df_display), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_display):
                    school = df_display.iloc[i + j]
                    fase_e = str(school['Fase école'])
                    is_act = not df_config[df_config['Fase école'] == fase_e].empty
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold;">✓ Active</span>' if is_act else ''
                    
                    with cols[j]:
                        st.markdown(f"""
                        <div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:16px; margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between;"><b>{school['Ecole']}</b> {badge}</div>
                            <div style="font-size:11px; color:gray;">FASE: {fase_e} | {school['Directeur.rice']}</div>
                            <div style="font-size:11px; color:#4169E1;">✉️ {school['Email']} | 📞 {school['Téléphone']}</div>
                        </div>
                        """, unsafe_allow_html=True)
