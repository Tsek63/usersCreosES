import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    # --- 0. NETTOYAGE DES DONNÉES ---
    df_ecoles = df_ecoles.fillna("-").astype(str).replace("nan", "-")
    df_contacts = df_contacts.fillna("-").astype(str).replace("nan", "-")

    # --- 1. BANDEAU STATS ---
    active_communes = df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique()
    
    stats_html = f"""<div style="display:flex; gap:12px; margin-bottom:20px;">
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
</div>"""
    st.markdown(stats_html.strip(), unsafe_allow_html=True)

    # --- 2. FILTRES ---
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
        if st.button("🗑️ Effacer", use_container_width=True, key="reset_btn"):
            st.session_state.t3_rc += 1
            st.rerun()

    if commune_tab3:
        # --- 3. SECTION CONTACTS ---
        st.markdown(f"### 👤 Contacts - {commune_tab3}")
        contacts_comm = df_contacts[df_contacts['Commune'] == commune_tab3].copy()
        
        if not contacts_comm.empty:
            cols_c = st.columns(3)
            for i, (idx, ct) in enumerate(contacts_comm.iterrows()):
                with cols_c[i % 3]:
                    contact_card = f"""<div style="background:#f5f3ff; border-left:5px solid #7c3aed; padding:15px; margin-bottom:10px; color:#334155;">
<b style="color:#7c3aed; font-size:20px;">{ct['Titre']} {ct['Nom']}</b><br>
<div style="margin-top:10px; font-size:14px;">
📞 <a href="tel:{ct['Téléphone']}">{ct['Téléphone']}</a><br>
📱 <a href="tel:{ct['GSM']}">{ct['GSM']}</a><br>
✉️ <a href="mailto:{ct['Email']}">{ct['Email']}</a>
</div></div>"""
                    st.markdown(contact_card.strip(), unsafe_allow_html=True)
                    
                    b_edit, b_del = st.columns(2)
                    if b_edit.button("✏️ Modifier", key=f"ed_{idx}"):
                        st.session_state[f"editing_{idx}"] = True
                    if b_del.button("🗑️ Supprimer", key=f"de_{idx}"):
                        df_upd = df_contacts.drop(idx)
                        safe_write(conn, "Contacts", df_upd)
                        st.cache_data.clear(); st.rerun()
                    
                    if st.session_state.get(f"editing_{idx}"):
                        with st.form(f"form_edit_{idx}"):
                            st.write(f"Modification de {ct['Nom']}")
                            e_titre = st.text_input("Titre", value=ct['Titre'])
                            e_nom = st.text_input("Nom Prénom", value=ct['Nom'])
                            e_tel = st.text_input("Téléphone fixe", value=ct['Téléphone'])
                            e_gsm = st.text_input("GSM", value=ct['GSM'])
                            e_mail = st.text_input("Email", value=ct['Email'])
                            
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("✅ Valider"):
                                df_contacts.loc[idx, ['Titre', 'Nom', 'Téléphone', 'GSM', 'Email']] = [e_titre, e_nom, e_tel, e_gsm, e_mail]
                                safe_write(conn, "Contacts", df_contacts)
                                del st.session_state[f"editing_{idx}"]
                                st.cache_data.clear(); st.rerun()
                            if c2.form_submit_button("❌ Annuler"):
                                del st.session_state[f"editing_{idx}"]
                                st.rerun()

        with st.expander("➕ Ajouter un nouveau contact"):
            with st.form("new_ct_form"):
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

        # --- 4. LISTE ÉCOLES ---
        st.divider()
        df_disp = df_ecoles[df_ecoles['Commune'] == commune_tab3]
        if search_ecole:
            df_disp = df_disp[df_disp['Ecole'].str.contains(search_ecole, case=False, na=False)]

        for i in range(0, len(df_disp), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_disp):
                    sch = df_disp.iloc[i + j]
                    fase = str(sch['Fase école'])
                    conf = df_config[df_config['Fase école'] == fase]
                    is_act = not conf.empty and conf.iloc[0]['Extrascolaire'] == 'Oui'
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:bold; float:right;">✓ ACTIVE</span>' if is_act else ''
                    
                    with cols[j]:
                        card_html = f"""<div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:20px; margin-bottom:12px; color:#1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height:180px;">
{badge}
<b style="font-size:22px; color:#4169E1; line-height:1.2;">{sch['Ecole']}</b><br>
<div style="margin-top:10px; font-size:14px; color:#64748b;">
<b>FASE:</b> {fase} | <b>Dir:</b> {sch.get('Directeur.rice','-')}
</div>
<div style="margin-top:10px; font-size:15px;">
✉️ <a href="mailto:{sch['Email']}">{sch['Email']}</a><br>
📞 <a href="tel:{sch['Téléphone']}">{sch['Téléphone']}</a>
</div>
<div style="margin-top:10px; font-size:12px; color:gray;">
📍 {sch.get('Rue','')} {sch.get('N°','')}, {sch.get('Code postal','')} {sch.get('Localité','')}
</div></div>"""
                        st.markdown(card_html.strip(), unsafe_allow_html=True)
