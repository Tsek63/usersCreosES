import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    df_ecoles = df_ecoles.fillna("-").astype(str).replace("nan", "-")
    df_contacts = df_contacts.fillna("-").astype(str).replace("nan", "-")
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())

    st.markdown(f"""<div style="display:flex; gap:12px; margin-bottom:20px;">
<div style="flex:1; background:#4169E1; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">TOTAL ÉCOLES</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Fase école'].nunique()}</div>
</div>
<div style="flex:1; background:#008080; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">COMMUNES / PO</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
</div>
<div style="flex:1.5; background:#1e293b; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">UTILISATEURS CREOS EXTRASCOLAIRE</div>
<div style="font-size:48px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
</div>
</div>""", unsafe_allow_html=True)

    if 't3_rc' not in st.session_state: st.session_state.t3_rc = 0
    c1, c2, c3, cr = st.columns([2, 3, 3, 1.2])
    with c1:
        prov = st.selectbox("Province", ["Toutes"] + sorted(list(data_fwb.keys())), key=f"t3p_{st.session_state.t3_rc}")
    with c2:
        c_list = sorted(data_fwb.get(prov, df_ecoles['Commune'].unique().tolist())) if prov != "Toutes" else sorted(df_ecoles['Commune'].unique().tolist())
        commune = st.selectbox("Commune", [""] + c_list, format_func=lambda x: f"{'✅' if x in active_communes else '⚪'} {icon_po(x)} {x}" if x else "Sélectionnez...", key=f"t3c_{st.session_state.t3_rc}")
    with c3: search = st.text_input("Recherche", placeholder="Nom, Fase...", key=f"t3s_{st.session_state.t3_rc}")
    with cr:
        st.write("")
        if st.button("🗑️ Effacer", key="reset_t3"):
            st.session_state.t3_rc += 1
            st.rerun()

    if commune:
        st.markdown(f"### 👤 Contacts - {commune}")
        contacts = df_contacts[df_contacts['Commune'] == commune]
        if not contacts.empty:
            cols = st.columns(3)
            for i, (idx, ct) in enumerate(contacts.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""<div style="background:#f5f3ff; border-left:5px solid #7c3aed; padding:15px; border-radius:10px; margin-bottom:10px; color:#334155; min-height:150px;">
<b style="color:#7c3aed; font-size:20px;">{ct['Titre']} {ct['Nom']}</b><br><div style="margin-top:10px; font-size:14px;">
📞 <a href="tel:{ct['Téléphone']}">{ct['Téléphone']}</a><br>📱 <a href="tel:{ct['GSM']}">{ct['GSM']}</a><br>✉️ <a href="mailto:{ct['Email']}">{ct['Email']}</a>
</div></div>""", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    if b1.button("✏️", key=f"ed_{idx}"): st.session_state[f"edit_{idx}"] = True
                    if b2.button("🗑️", key=f"de_{idx}"): safe_write(conn, "Contacts", df_contacts.drop(idx)); st.cache_data.clear(); st.rerun()
                    if st.session_state.get(f"edit_{idx}"):
                        with st.form(f"f_{idx}"):
                            new_data = { "Titre": st.text_input("Titre", value=ct['Titre']), "Nom": st.text_input("Nom", value=ct['Nom']), "Téléphone": st.text_input("Tel", value=ct['Téléphone']), "GSM": st.text_input("GSM", value=ct['GSM']), "Email": st.text_input("Email", value=ct['Email']) }
                            if st.form_submit_button("Valider"):
                                for k, v in new_data.items(): df_contacts.at[idx, k] = v
                                safe_write(conn, "Contacts", df_contacts); del st.session_state[f"edit_{idx}"]; st.cache_data.clear(); st.rerun()

        st.divider()
        df_disp = df_ecoles[df_ecoles['Commune'] == commune]
        if search: df_disp = df_disp[df_disp['Ecole'].str.contains(search, case=False)]
        for i in range(0, len(df_disp), 2):
            row_cols = st.columns(2)
            for j in range(2):
                if i + j < len(df_disp):
                    sch = df_disp.iloc[i + j]
                    is_act = not df_config[(df_config['Fase école'] == sch['Fase école']) & (df_config['Extrascolaire'] == 'Oui')].empty
                    badge = '<span style="background:#4ade80; color:#1e293b; padding:6px 12px; border-radius:6px; font-size:11px; font-weight:bold; float:right;">✓ ACTIVE</span>' if is_act else ''
                    with row_cols[j]:
                        card = f"""<div style="background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:20px; margin-bottom:12px; color:#1e293b; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height:180px;">
{badge}<b style="font-size:22px; color:#4169E1; line-height:1.2;">{sch['Ecole']}</b><br><div style="margin-top:10px; font-size:14px; color:#64748b;"><b>FASE:</b> {sch['Fase école']} | <b>Dir:</b> {sch.get('Directeur.rice','-')}</div>
<div style="margin-top:10px; font-size:15px;">✉️ <a href="mailto:{sch['Email']}">{sch['Email']}</a><br>📞 <a href="tel:{sch['Téléphone']}">{sch['Téléphone']}</a></div>
<div style="margin-top:10px; font-size:12px; color:gray;">📍 {sch.get('Rue','')} {sch.get('N°','')}, {sch.get('Code postal','')} {sch.get('Localité','')}</div></div>"""
                        st.markdown(card.strip(), unsafe_allow_html=True)
