import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    # --- 0. NETTOYAGE RADICAL DES DONNÉES ---
    # On transforme tout en texte et on remplace les vides par des tirets
    df_ecoles = df_ecoles.astype(str).replace(['nan', 'None', '<NA>'], '-')
    df_contacts = df_contacts.astype(str).replace(['nan', 'None', '<NA>'], '-')

    # --- 1. BANDEAU STATS (Police 48px) ---
    active_communes = df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique()
    
    stats_html = f"""
    <div style="display:flex; gap:12px; margin-bottom:20px;">
        <div style="flex:1; background:#4169E1; color:white; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Total Écoles</div>
            <div style="font-size:48px; font-weight:bold;">{len(df_ecoles)}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Communes / PO</div>
            <div style="font-size:48px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
        </div>
        <div style="flex:1.5; background:#1e293b; color:white; padding:20px; border-radius:10px; text-align:center;">
            <div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Utilisateurs Creos Extrascolaire</div>
            <div style="font-size:48px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

    # --- 2. FILTRES (Tri alphabétique) ---
    if 't3_rc' not in st.session_state: st.session_state.t3_rc = 0
    c1, c2, c3, c_reset = st.columns([2, 3, 3, 1.2])
    
    with c1:
        prov_list = sorted(list(data_fwb.keys()))
        prov_tab3 = st.selectbox("🗺️ Province", ["Toutes"] + prov_list, key=f"p3_{st.session_state.t3_rc}")
    
    with c2:
        if prov_tab3 != "Toutes":
            comm_list = sorted(data_fwb.get(prov_tab3, []))
        else:
            comm_list = sorted(df_ecoles['Commune'].unique().tolist())
        commune_tab3 = st.selectbox("🏘️ Commune", [""] + comm_list, key=f"c3_{st.session_state.t3_rc}",
                                    format_func=lambda x: f"{icon_po(x)} {x}" if x else "Sélectionnez...")
    
    with c3:
        search_ecole = st.text_input("🔍 Rechercher une école", placeholder="Nom, Fase...", key=f"s3_{st.session_state.t3_rc}")

    with c_reset:
        st.write("") 
        if st.button("🗑️ Effacer", use_container_width=True):
            st.session_state.t3_rc += 1
            st.rerun()

    if commune_tab3:
        # --- 3. SECTION CONTACTS ---
        st.markdown(f"### 👤 Contacts Extrascolaire - {commune_tab3}")
        contacts_comm = df_contacts[df_contacts['Commune'] == commune_tab3].copy()
        
        if not contacts_comm.empty:
            cols_c = st.columns(3)
            for i, (idx, ct) in enumerate(contacts_comm.iterrows()):
                with cols_c[i % 3]:
                    # Liens cliquables
                    t_link = f'<a href="tel:{ct["Téléphone"]}" style="color:#7c3aed; text-decoration:none;">{ct["Téléphone"]}</a>' if ct["Téléphone"] != "-" else "-"
                    g_link = f'<a href="tel:{ct["GSM"]}" style="color:#7c3aed; text-decoration:none;">{ct["GSM"]}</a>' if ct["GSM"] != "-" else "-"
                    m_link = f'<a href="mailto:{ct["Email"]}" style="color:#7c3aed; text-decoration:none;">{ct["Email"]}</a>' if ct["Email"] != "-" else "-"

                    contact_html = f"""
                    <div style="background:#f5f3ff; border:1px solid #ddd6fe; border-left:5px solid #7c3aed; border-radius:10px; padding:15px; margin-bottom:10px; color:#334155;">
                        <b style="color:#7c3aed; font-size:20px;">{ct['Titre']} {ct['Nom']}</b><br>
                        <div style="margin-top:10px; font-size:14px; line-height:1.6;">
                            📞 {t_link}<br>
                            📱 {g_link}<br>
                            ✉️ {m_link}
                        </div>
                    </div>
                    """
                    st.markdown(contact_html, unsafe_allow_html=True)
                    
                    # Boutons Modifier/Supprimer
                    b_edit, b_del = st.columns(2)
                    if b_edit.button("✏️ Modifier", key=f"edit_ct_{idx}"):
                        st.session_state[f"editing_{idx}"] = True
                    if b_del.button("🗑️ Supprimer", key=f"del_ct_{idx}"):
                        df_contacts_upd = df_contacts.drop(idx)
                        safe_write(conn, "Contacts", df_contacts_upd)
                        st.cache_data.clear(); st.rerun()
                    
                    # Formulaire de modification complet
                    if st.session_state.get(f"editing_{idx}"):
                        with st.form(f"form_edit_{idx}"):
                            st.write(f"Modification de {ct['Nom']}")
                            et = st.text_input("Titre", value=ct['Titre'])
                            en = st.text_input("Nom", value=ct['Nom'])
                            etf = st.text_input("Tel fixe", value=ct['Téléphone'])
                            eg = st.text_input("GSM", value=ct['GSM'])
                            em = st.text_input("Email", value=ct['Email'])
                            if st.form_submit_button("✅ Valider"):
                                df_contacts.loc[idx, ['Titre', 'Nom', 'Téléphone', 'GSM', 'Email']] = [et, en, etf, eg, em]
                                safe_write(conn, "Contacts", df_contacts)
                                del st.session_state[f"editing_{idx}"]
                                st.cache_data.clear(); st.rerun()

        # --- AJOUT CONTACT ---
        with st.expander("➕ Ajouter un nouveau contact"):
            with st.form("new_contact_form"):
                f1, f2 = st.columns(2)
                nt = f1.text_input("Titre")
                nn = f1.text_input("Nom Prénom")
                ntel = f2.text_input("Téléphone fixe")
                ng = f2.text_input("GSM")
                nmail = st.text_input("Email")
                if st.form_submit_button("💾 Enregistrer"):
                    new_ct = pd.DataFrame([{"Province": prov_tab3, "Commune": commune_tab3, "Titre": nt, "Nom": nn, "Téléphone": ntel, "GSM": ng, "Email": nmail}])
                    safe_write(conn, "Contacts", pd.concat([df_contacts, new_ct], ignore_index=True))
                    st.cache_data.clear(); st.rerun()

        # --- 4. LISTE ÉCOLES (Mise en page 2 colonnes) ---
        st.divider()
        df_disp = df_ecoles[df_ecoles['Commune'] == commune_tab3]
        if search_ecole:
            df_disp = df_disp[df_disp['Ecole'].str.contains(search_ecole, case=False, na=False)]

        # On boucle pour créer les lignes de 2 colonnes
        for i in range(0, len(df_disp), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_disp):
                    sch = df_disp.iloc[i + j]
                    fase = str(sch['Fase école'])
                    conf = df_config[df_config['Fase école'] == fase]
                    is_act = not conf.empty and conf.iloc[0]['Extrascolaire'] == 'Oui'
                    
                    # Badge Active
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:5px 10px; border-radius:6px; font-size:11px; font-weight:bold; float:right;">✓ ACTIVE</span>' if is_act else ''
                    
                    # Liens cliquables école
                    em_link = f'<a href="mailto:{sch["Email"]}" style="color:#4169E1; text-decoration:none;">{sch["Email"]}</a>' if sch["Email"] != "-" else "-"
                    tl_link = f'<a href="tel:{sch["Téléphone"]}" style="color:#1e293b; text-decoration:none;">{sch["Téléphone"]}</a>' if sch["Téléphone"] != "-" else "-"

                    # Construction de la CARTE ECOLE
                    card_html = f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:20px; margin-bottom:12px; color:#1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height:180px;">
                        {badge}
                        <b style="font-size:22px; color:#4169E1; line-height:1.2;">{sch['Ecole']}</b><br>
                        <div style="margin-top:12px; font-size:14px; color:#64748b;">
                            <b>FASE:</b> {fase} | <b>Dir:</b> {sch.get('Directeur.rice','-')}
                        </div>
                        <div style="margin-top:12px; font-size:16px;">
                            ✉️ {em_link}<br>
                            📞 {tl_link}
                        </div>
                        <div style="margin-top:12px; font-size:13px; color:#94a3b8;">
                            📍 {sch.get('Rue','')} {sch.get('N°','')}, {sch.get('Code postal','')} {sch.get('Localité','')}
                        </div>
                    </div>
                    """
                    # AFFICHAGE DE LA CARTE
                    with cols[j]:
                        st.markdown(card_html, unsafe_allow_html=True)
