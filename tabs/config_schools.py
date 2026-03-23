import streamlit as st
import pandas as pd
import plotly.express as px
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles")
    
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📝 Configurer une École")
        s1, s2, s3 = st.columns(3)
        with s1:
            p_sel = st.selectbox("1. Province", list(data_fwb.keys()), key="cfg_p")
        with s2:
            c_opts = data_fwb.get(p_sel, [])
            c_sel = st.selectbox("2. Commune", ["— Sélectionnez —"] + c_opts, key="cfg_c")
        with s3:
            if c_sel != "— Sélectionnez —":
                e_loc = df_ecoles[df_ecoles['Commune'] == c_sel]
                e_sel = st.selectbox("3. École", e_loc['Ecole'].tolist(), key="cfg_e")
                fase_sel = str(e_loc[e_loc['Ecole'] == e_sel]['Fase école'].iloc[0])
            else:
                st.selectbox("3. École", ["—"], disabled=True)
                fase_sel = None

        if fase_sel:
            with st.form("form_cfg"):
                extra = st.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], horizontal=True)
                pay = st.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                servs = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
                
                if st.form_submit_button("💾 ENREGISTRER"):
                    new_row = pd.DataFrame([{
                        "Fase école": fase_sel, "Commune": c_sel, "Province": p_sel,
                        "Extrascolaire": extra, "Paiement": pay if extra=="Oui" else "",
                        "Services": "|".join(servs) if extra=="Oui" else ""
                    }])
                    df_upd = pd.concat([df_config[df_config['Fase école'] != fase_sel], new_row])
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear()
                    st.rerun()

    with col_right:
        # BLOC TEAL ORIGINAL
        n_act = len(df_active)
        n_pre = len(df_active[df_active['Paiement'] == 'Prépaiement'])
        n_post = len(df_active[df_active['Paiement'] == 'Post-paiement'])
        
        st.markdown(f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.8;">Écoles actives</div>
            <div style="font-size:52px; font-weight:bold; line-height:1;">{n_act}</div>
            <div style="display:flex; justify-content:space-around; margin-top:15px; border-top:1px solid rgba(255,255,255,0.2); padding-top:10px;">
                <div><b>{n_pre}</b><br><small>Pré</small></div>
                <div><b>{n_post}</b><br><small>Post</small></div>
                <div><b>{df_active['Commune'].nunique()}</b><br><small>Com</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # GRAPHIQUES ET LISTE (Bas de page)
    if not df_active.empty:
        st.divider()
        st.subheader("📊 Répartition et Liste")
        # Ici vous pouvez remettre vos graphiques Plotly et la liste avec bouton poubelle
