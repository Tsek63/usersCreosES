import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb):
    st.markdown("#### ⚙️ Paramétrage")
    
    col_l, col_r = st.columns([2, 1])

    with col_l:
        # CASCADE DE MENUS (Hors du formulaire pour le rafraîchissement)
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()), key="cfg_p")
        c_sel = st.selectbox("2. Commune", ["—"] + data_fwb.get(p_sel, []), key="cfg_c")
        
        if c_sel != "—":
            e_loc = df_ecoles[df_ecoles['Commune'] == c_sel]
            e_sel = st.selectbox("3. École", e_loc['Ecole'].tolist(), key="cfg_e")
            fase_sel = str(e_loc[e_loc['Ecole'] == e_sel]['Fase école'].iloc[0])

            # FORMULAIRE DE SAUVEGARDE
            with st.form("save_cfg_form"):
                extra = st.radio("Utilise l'extrascolaire ?", ["Oui", "Non"], horizontal=True)
                pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                servs = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
                
                if st.form_submit_button("💾 Sauvegarder"):
                    new_row = pd.DataFrame([{
                        "Fase école": fase_sel, "Commune": c_sel, "Province": p_sel,
                        "Extrascolaire": extra, "Paiement": pay if extra=="Oui" else "",
                        "Services": "|".join(servs) if extra=="Oui" else ""
                    }])
                    df_upd = pd.concat([df_config[df_config['Fase école'] != fase_sel], new_row])
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear()
                    st.success("Config enregistrée !")
                    st.rerun()

    with col_r:
        # BLOC TEAL
        st.markdown(f"""
        <div style="background:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; opacity:0.8;">ÉCOLES ACTIVES</div>
            <div style="font-size:48px; font-weight:bold;">{len(df_config[df_config['Extrascolaire']=='Oui'])}</div>
        </div>
        """, unsafe_allow_html=True)
