import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    # Stats en haut
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
    
    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:16px;">
        <div style="flex:1; background:#4169E1; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Total Écoles</div>
            <div style="font-size:32px; font-weight:bold;">{len(df_ecoles)}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Communes</div>
            <div style="font-size:32px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
        </div>
        <div style="flex:1; background:#1e293b; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; opacity:0.8;">Actives</div>
            <div style="font-size:32px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filtres
    c1, c2, c3 = st.columns([2, 3, 3])
    with c1:
        prov = st.selectbox("🗺️ Province", ["Toutes"] + list(data_fwb.keys()), key="t3_p")
    with c2:
        # Cascade de communes
        comm_opts = data_fwb.get(prov, sorted(df_ecoles['Commune'].unique())) if prov != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune_sel = st.selectbox("🏘️ Commune", [""] + comm_opts, key="t3_c")
    with c3:
        search = st.text_input("🔍 Recherche rapide", placeholder="Nom d'école...")

    if commune_sel:
        # On filtre les écoles DE LA COMMUNE
        df_display = df_ecoles[df_ecoles['Commune'] == commune_sel].copy()
        
        if search:
            df_display = df_display[df_display['Ecole'].str.contains(search, case=False, na=False)]

        st.markdown(f'<div style="background:#1e293b; color:white; padding:12px; border-radius:10px; margin-bottom:10px;">🏛️ {commune_sel}</div>', unsafe_allow_html=True)

        # Affichage en 2 colonnes
        if not df_display.empty:
            for i in range(0, len(df_display), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df_display):
                        school = df_display.iloc[i + j]
                        fase = str(school['Fase école'])
                        is_active = not df_config[df_config['Fase école'] == fase].empty
                        badge = '✅ Active' if is_active else ''
                        with cols[j]:
                            st.markdown(f"""
                            <div style="background:white; border:1px solid #eee; border-left:5px solid #4169E1; padding:15px; border-radius:10px; margin-bottom:10px;">
                                <b>{school['Ecole']}</b> <span style="color:green; font-size:10px;">{badge}</span><br>
                                <small>Fase: {fase} | {school.get('Email', '-')}</small>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("Aucune école trouvée.")
