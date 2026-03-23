import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    st.markdown("#### 🔍 Recherche d'écoles et contacts")
    
    # Filtres
    c1, c2 = st.columns(2)
    with c1:
        prov = st.selectbox("🗺️ Choisir Province", ["Toutes"] + list(data_fwb.keys()), key="search_p")
    with c2:
        comm_opts = data_fwb.get(prov, sorted(df_ecoles['Commune'].unique())) if prov != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune_sel = st.selectbox("🏘️ Choisir Commune", [""] + comm_opts, key="search_c")

    if commune_sel:
        # 1. FILTRAGE DES DONNÉES
        df_display = df_ecoles[df_ecoles['Commune'] == commune_sel].copy()
        
        # 2. AFFICHAGE DES CONTACTS
        st.markdown(f"**👤 Contacts pour {commune_sel}**")
        contacts = df_contacts[df_contacts['Commune'] == commune_sel]
        if not contacts.empty:
            cols_c = st.columns(3)
            for i, (_, ct) in enumerate(contacts.iterrows()):
                with cols_c[i % 3]:
                    st.info(f"**{ct['Nom']}**\n\n📞 {ct['Téléphone']}\n\n✉️ {ct['Email']}")
        else:
            st.warning("Aucun contact enregistré.")

        # 3. AFFICHAGE DES ÉCOLES EN 2 COLONNES
        st.markdown(f"**🏫 Écoles ({len(df_display)})**")
        if not df_display.empty:
            for i in range(0, len(df_display), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df_display):
                        school = df_display.iloc[i + j]
                        fase = str(school['Fase école'])
                        is_active = not df_config[df_config['Fase école'] == fase].empty
                        badge = "✅" if is_active else "⚪"
                        with cols[j]:
                            st.markdown(f"""
                            <div style="background:white; border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid #4169E1;">
                                {badge} <b>{school['Ecole']}</b><br>
                                <small>Fase: {fase}</small><br>
                                <small>Dir: {school.get('Directeur.rice','-')}</small>
                            </div>
                            """, unsafe_allow_html=True)
