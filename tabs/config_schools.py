import streamlit as st
import pandas as pd
import plotly.express as px
import io, base64
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb):
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("📝 Paramétrage")
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()), key="c_p")
        c_sel = st.selectbox("2. Commune", ["—"] + data_fwb.get(p_sel, []), key="c_c")
        if c_sel != "—":
            e_loc = df_ecoles[df_ecoles['Commune'] == c_sel]
            e_sel = st.selectbox("3. École", e_loc['Ecole'].tolist(), key="c_e")
            fase_sel = str(e_loc[e_loc['Ecole'] == e_sel]['Fase école'].iloc[0])
            with st.form("f_cfg"):
                ex = st.radio("Utilise l'extrascolaire ?", ["Oui", "Non"], horizontal=True)
                pa = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                sv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
                if st.form_submit_button("💾 Sauvegarder"):
                    new = pd.DataFrame([{"Fase école": fase_sel, "Commune": c_sel, "Province": p_sel, "Extrascolaire": ex, "Paiement": pa if ex=="Oui" else "", "Services": "|".join(sv) if ex=="Oui" else ""}])
                    df_upd = pd.concat([df_config[df_config['Fase école'] != fase_sel], new])
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

    with col_r:
        st.markdown(f"""
        <div style="background:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; opacity:0.8;">ÉCOLES ACTIVES</div><div style="font-size:48px; font-weight:bold;">{len(df_active)}</div>
            <div style="display:flex; justify-content:space-around; margin-top:10px; border-top:1px solid rgba(255,255,255,0.2); padding-top:10px; font-size:12px;">
                <div><b>{len(df_active[df_active['Paiement']=='Prépaiement'])}</b><br>Pré</div>
                <div><b>{len(df_active[df_active['Paiement']=='Post-paiement'])}</b><br>Post</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- EXPORTS ---
    st.divider()
    if not df_active.empty:
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            buf = io.BytesIO()
            df_active.to_excel(buf, index=False)
            st.download_button("📥 Export Excel", buf.getvalue(), "ecoles_actives.xlsx", "application/vnd.ms-excel")

        # --- GRAPH ET LISTE ---
        g1, g2 = st.columns(2)
        with g1:
            fig = px.pie(df_active, names='Paiement', title="Modes de Paiement", hole=0.4, color_discrete_sequence=['#ec4899', '#38bdf8'])
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.markdown("##### 🗑️ Supprimer une école")
            del_f = st.selectbox("Choisir école", df_active['Fase école'].tolist())
            if st.button("❌ Supprimer définitivement"):
                safe_write(conn, "EcolesConfig", df_config[df_config['Fase école'] != del_f])
                st.cache_data.clear(); st.rerun()
