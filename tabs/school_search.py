import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())

    # BANDEAU TRIPLE STATS
    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:16px;">
        <div style="flex:1; background:#4169E1; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Total Écoles</div><div style="font-size:38px; font-weight:bold;">{len(df_ecoles)}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Communes</div><div style="font-size:38px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
        </div>
        <div style="flex:1; background:#1e293b; color:white; padding:14px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8;">Actives</div><div style="font-size:38px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 3, 3])
    with c1: prov = st.selectbox("Province", ["Toutes"] + list(data_fwb.keys()), key="t2p")
    with c2: 
        opts = data_fwb.get(prov, sorted(df_ecoles['Commune'].unique())) if prov != "Toutes" else sorted(df_ecoles['Commune'].unique())
        commune = st.selectbox("Commune", [""] + opts, key="t2c")
    with c3: search = st.text_input("🔍 Rechercher une école", key="t2s")

    if commune:
        # CONTACTS SECTION
        st.markdown(f"#### 👤 Contacts Extrascolaire - {commune}")
        contacts_comm = df_contacts[df_contacts['Commune'] == commune].copy()
        if not contacts_comm.empty:
            cols_c = st.columns(3)
            for i, (idx, ct) in enumerate(contacts_comm.iterrows()):
                with cols_c[i % 3]:
                    st.markdown(f"""
                    <div style="background:#f5f3ff; border-left:5px solid #7c3aed; padding:12px; border-radius:10px; margin-bottom:10px; color:#334155;">
                        <b style="color:#7c3aed;">{ct['Titre']} {ct['Nom']}</b><br>
                        📞 <a href="tel:{ct['Téléphone']}">{ct['Téléphone']}</a><br>✉️ {ct['Email']}
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Supprimer", key=f"del_ct_{idx}"):
                        safe_write(conn, "Contacts", df_contacts.drop(idx))
                        st.rerun()

        with st.expander("➕ Ajouter un contact"):
            with st.form("add_ct"):
                f1, f2 = st.columns(2)
                t = f1.text_input("Titre")
                n = f1.text_input("Nom")
                tel = f2.text_input("Téléphone")
                mail = f2.text_input("Email")
                if st.form_submit_button("💾 Enregistrer"):
                    new_ct = pd.DataFrame([{"Province": prov, "Commune": commune, "Titre": t, "Nom": n, "Téléphone": tel, "Email": mail}])
                    safe_write(conn, "Contacts", pd.concat([df_contacts, new_ct], ignore_index=True))
                    st.rerun()

        # SCHOOLS LIST IN 2 COLUMNS
        st.divider()
        df_disp = df_ecoles[df_ecoles['Commune'] == commune]
        if search: df_disp = df_disp[df_disp['Ecole'].str.contains(search, case=False, na=False)]
        
        for i in range(0, len(df_disp), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_disp):
                    sch = df_disp.iloc[i + j]
                    is_act = not df_config[df_config['Fase école'] == str(sch['Fase école'])].empty
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold; float:right;">✓ Active</span>' if is_act else ''
                    with cols[j]:
                        st.markdown(f"""
                        <div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:16px; margin-bottom:12px; color:#334155;">
                            {badge}<b>{sch['Ecole']}</b><br>
                            <small>Fase: {sch['Fase école']} | Dir: {sch['Directeur.rice']}</small><br>
                            <small>✉️ {sch['Email']} | 📞 {sch['Téléphone']}</small><br>
                            <small style="color:gray;">📍 {sch['Rue']} {sch['N°']}, {sch['Code postal']} {sch['Localité']}</small>
                        </div>
                        """, unsafe_allow_html=True)
