import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
    
    # Filtres
    c1, c2, c3 = st.columns([2, 3, 3])
    with c1:
        prov = st.selectbox("🗺️ Province", ["Toutes"] + list(data_fwb.keys()), key="s_p")
    with c2:
        comm_opts = data_fwb.get(prov, sorted(df_ecoles['Commune'].unique())) if prov != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune_sel = st.selectbox("🏘️ Commune", [""] + comm_opts, key="s_c")
    with c3:
        search = st.text_input("🔍 Rechercher", placeholder="Nom, Fase...")

    if commune_sel:
        # --- CONTACTS (RETOUR DU DESIGN VIOLET) ---
        st.markdown(f"#### 👤 Contacts Extrascolaire - {commune_sel}")
        contacts_comm = df_contacts[df_contacts['Commune'] == commune_sel]
        
        if not contacts_comm.empty:
            cols_c = st.columns(3)
            for i, (idx, ct) in enumerate(contacts_comm.iterrows()):
                with cols_c[i % 3]:
                    st.markdown(f"""
                    <div style="background:#f5f3ff; border:1px solid #ddd6fe; border-left:5px solid #7c3aed; border-radius:10px; padding:12px; margin-bottom:10px; color:#334155;">
                        <b style="color:#7c3aed;">{ct['Titre']} {ct['Nom']}</b><br>
                        📞 <a href="tel:{ct['Téléphone']}" style="color:#7c3aed;">{ct['Téléphone']}</a><br>
                        ✉️ <a href="mailto:{ct['Email']}" style="color:#7c3aed;">{ct['Email']}</a>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_ct_{idx}"):
                        safe_write(conn, "Contacts", df_contacts.drop(idx))
                        st.rerun()

        # --- AJOUT CONTACT ---
        with st.expander("➕ Ajouter un contact"):
            with st.form("add_contact"):
                f1, f2 = st.columns(2)
                t = f1.text_input("Titre")
                n = f1.text_input("Nom")
                tel = f2.text_input("Téléphone")
                mail = f2.text_input("Email")
                if st.form_submit_button("💾 Enregistrer"):
                    new_ct = pd.DataFrame([{"Province": prov, "Commune": commune_sel, "Titre": t, "Nom": n, "Téléphone": tel, "Email": mail}])
                    safe_write(conn, "Contacts", pd.concat([df_contacts, new_ct], ignore_index=True))
                    st.cache_data.clear()
                    st.rerun()

        # --- ÉCOLES (RETOUR DU DESIGN 2 COLONNES) ---
        st.divider()
        df_disp = df_ecoles[df_ecoles['Commune'] == commune_sel]
        if search:
            df_disp = df_disp[df_disp['Ecole'].str.contains(search, case=False, na=False)]

        for i in range(0, len(df_disp), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_disp):
                    school = df_disp.iloc[i + j]
                    fase = str(school['Fase école'])
                    conf = df_config[df_config['Fase école'] == fase]
                    is_act = not conf.empty and conf.iloc[0]['Extrascolaire'] == 'Oui'
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold; float:right;">✓ Active</span>' if is_act else ''
                    
                    with cols[j]:
                        st.markdown(f"""
                        <div class="school-card">
                            {badge}
                            <b>{school['Ecole']}</b><br>
                            <span style="font-size:11px; color:#64748b;">FASE: {fase} | Dir: {school['Directeur.rice']}</span><br>
                            <span style="font-size:11px;">✉️ {school['Email']} | 📞 {school['Téléphone']}</span><br>
                            <span style="font-size:10px; color:#94a3b8;">📍 {school['Rue']} {school['N°']}, {school['Code postal']} {school['Localité']}</span>
                        </div>
                        """, unsafe_allow_html=True)
