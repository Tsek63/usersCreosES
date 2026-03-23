import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    # --- 0. NETTOYAGE DES DONNÉES ---
    df_ecoles = df_ecoles.fillna("-").astype(str).replace("nan", "-")
    df_contacts = df_contacts.fillna("-").astype(str).replace("nan", "-")
    
    # On identifie les communes utilisatrices (au moins une école à "Oui")
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())

    # --- 1. BANDEAU STATS (Correction Total à 1089 via nunique) ---
    st.markdown(f"""<div style="display:flex; gap:12px; margin-bottom:20px;">
<div style="flex:1; background:#4169E1; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Total Écoles</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Fase école'].nunique()}</div>
</div>
<div style="flex:1; background:#008080; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Communes / PO</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
</div>
<div style="flex:1.5; background:#1e293b; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; text-transform:uppercase; opacity:0.8;">Utilisateurs Creos Extrascolaire</div>
<div style="font-size:48px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
</div>
</div>""", unsafe_allow_html=True)

    # --- 2. FILTRES ---
    if 't3_rc' not in st.session_state: st.session_state.t3_rc = 0
    c1, c2, c3, cr = st.columns([2, 3, 3, 1.2])
    
    with c1:
        prov_list = sorted(list(data_fwb.keys()))
        prov_tab3 = st.selectbox("🗺️ Province", ["Toutes"] + prov_list, key=f"t3p_{st.session_state.t3_rc}")
    
    with c2:
        if prov_tab3 != "Toutes":
            comm_list = sorted(data_fwb.get(prov_tab3, []))
        else:
            comm_list = sorted(df_ecoles['Commune'].unique().tolist())
        
        commune_tab3 = st.selectbox(
            "🏘️ Commune", 
            [""] + comm_list, 
            format_func=lambda x: f"{'✅' if x in active_communes else '⚪'} {icon_po(x)} {x}" if x else "Sélectionnez...",
            key=f"t3c_{st.session_state.t3_rc}"
        )
    
    with c3:
        search_ecole = st.text_input("🔍 Rechercher une école", placeholder="Nom, Fase...", key=f"t3s_{st.session_state.t3_rc}")

    with cr:
        st.write("") 
        if st.button("🗑️ Effacer", use_container_width=True, key="reset_btn_tab2"):
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
                    tel_l = f'<a href="tel:{ct["Téléphone"]}" style="color:#7c3aed;">{ct["Téléphone"]}</a>' if ct["Téléphone"] != "-" else "-"
                    gsm_l = f'<a href="tel:{ct["GSM"]}" style="color:#7c3aed;">{ct["GSM"]}</a>' if ct["GSM"] != "-" else "-"
                    mai_l = f'<a href="mailto:{ct["Email"]}" style="color:#7c3aed;">{ct["Email"]}</a>' if ct["Email"] != "-" else "-"

                    contact_card = f"""<div style="background:#f5f3ff; border-left:5px solid #7c3aed; padding:15px; margin-bottom:10px; color:#334155; min-height:150px;">
<b style="color:#7c3aed; font-size:20px;">{ct['Titre']} {ct['Nom']}</b><br>
<div style="margin-top:10px; font-size:14px; line-height:1.6;">
📞 {tel_l}<br>📱 {gsm_l}<br>✉️ {mai_l}
</div></div>"""
                    st.markdown(contact_card.strip(), unsafe_allow_html=True)
                    
                    b_edit, b_del = st.columns(2)
                    if b_edit.button("✏️ Modifier", key=f"ed_{idx}"):
                        st.session_state[f"editing_{idx}"] = True
                    if b_del.button("🗑️ Supprimer", key=f"de_{idx}"):
                        safe_write(conn, "Contacts", df_contacts.drop(idx))
                        st.cache_data.clear(); st.rerun()
                    
                    if st.session_state.get(f"editing_{idx}"):
                        with st.form(f"form_edit_{idx}"):
                            et = st.text_input("Titre", value=ct['Titre'])
                            en = st.text_input("Nom", value=ct['Nom'])
                            ef = st.text_input("Tel fixe", value=ct['Téléphone'])
                            eg = st.text_input("GSM", value=ct['GSM'])
                            em = st.text_input("Email", value=ct['Email'])
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("✅ Valider"):
                                df_contacts.loc[idx, ['Titre','Nom','Téléphone','GSM','Email']] = [et,en,ef,eg,em]
                                safe_write(conn, "Contacts", df_contacts)
                                del st.session_state[f"editing_{idx}"]
                                st.cache_data.clear(); st.rerun()
                            if c2.form_submit_button("❌ Annuler"):
                                del st.session_state[f"editing_{idx}"]
                                st.rerun()

        with st.expander("➕ Ajouter un nouveau contact"):
            with st.form("new_ct_form_tab2"):
                f1, f2 = st.columns(2)
                nt = f1.text_input("Titre")
                nn = f1.text_input("Nom Prénom")
                nf = f2.text_input("Téléphone fixe")
                ng = f2.text_input("GSM")
                ne = st.text_input("Email")
                if st.form_submit_button("💾 Enregistrer"):
                    new_row = pd.DataFrame([{"Province": prov_tab3, "Commune": commune_tab3, "Titre": nt, "Nom": nn, "Téléphone": nf, "GSM": ng, "Email": ne}])
                    safe_write(conn, "Contacts", pd.concat([df_contacts, new_row], ignore_index=True))
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
                    is_act = not df_config[(df_config['Fase école'] == fase) & (df_config['Extrascolaire'] == 'Oui')].empty
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:bold; float:right;">✓ ACTIVE</span>' if is_act else ''
                    
                    with cols[j]:
                        e_m = f'<a href="mailto:{sch["Email"]}" style="color:#4169E1; text-decoration:none;">{sch["Email"]}</a>' if sch["Email"] != "-" else "-"
                        e_t = f'<a href="tel:{sch["Téléphone"]}" style="color:#1e293b; text-decoration:none;">{sch["Téléphone"]}</a>' if sch["Téléphone"] != "-" else "-"

                        card_html = f"""<div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:20px; margin-bottom:12px; color:#1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height:180px;">
{badge}<b style="font-size:22px; color:#4169E1; line-height:1.2;">{sch['Ecole']}</b><br>
<div style="margin-top:10px; font-size:14px; color:#64748b;"><b>FASE:</b> {fase} | <b>Dir:</b> {sch.get('Directeur.rice','-')}</div>
<div style="margin-top:10px; font-size:15px;">✉️ {e_m}<br>📞 {e_t}</div>
<div style="margin-top:10px; font-size:12px; color:gray;">📍 {sch.get('Rue','')} {sch.get('N°','')}, {sch.get('Code postal','')} {sch.get('Localité','')}</div></div>"""
                        st.markdown(card_html.strip(), unsafe_allow_html=True)
