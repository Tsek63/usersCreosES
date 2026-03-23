import streamlit as st
import pandas as pd
import plotly.express as px
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb):
    st.subheader("⚙️ Gestion des Écoles Actives")
    
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    
    col_form, col_teal = st.columns([2, 1])

    # --- FORMULAIRE (GAUCHE) ---
    with col_form:
        with st.form("config_ecole"):
            st.markdown("##### 📝 Configurer une école")
            p_sel = st.selectbox("1. Province", list(data_fwb.keys()))
            c_sel = st.selectbox("2. Commune", data_fwb.get(p_sel, []))
            
            # Liste écoles de cette commune
            ecoles_loc = df_ecoles[df_ecoles['Commune'] == c_sel]
            e_sel_label = st.selectbox("3. École", ecoles_loc['Ecole'].tolist() if not ecoles_loc.empty else ["-"])
            
            extra = st.radio("Utilise l'extrascolaire ?", ["Oui", "Non"], horizontal=True)
            pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
            servs = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Garderie", "Activités"])
            
            if st.form_submit_button("💾 Enregistrer la configuration"):
                fase = ecoles_loc[ecoles_loc['Ecole'] == e_sel_label]['Fase école'].iloc[0]
                new_row = pd.DataFrame([{
                    "Fase école": fase, "Commune": c_sel, "Province": p_sel,
                    "Extrascolaire": extra, "Paiement": pay if extra == "Oui" else "",
                    "Services": "|".join(servs) if extra == "Oui" else ""
                }])
                df_upd = pd.concat([df_config[df_config['Fase école'] != fase], new_row])
                safe_write(conn, "EcolesConfig", df_upd)
                st.cache_data.clear()
                st.success("Configuration sauvegardée !")
                st.rerun()

    # --- BLOC TEAL (DROITE) ---
    with col_teal:
        n_act = len(df_active)
        st.markdown(f"""
        <div style="background:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:12px; opacity:0.8;">ÉCOLES ACTIVES</div>
            <div style="font-size:48px; font-weight:bold;">{n_act}</div>
            <hr style="opacity:0.3;">
            <div style="font-size:12px;">{len(df_active[df_active['Paiement']=='Prépaiement'])} Prépaiements</div>
            <div style="font-size:12px;">{len(df_active[df_active['Paiement']=='Post-paiement'])} Post-paiements</div>
        </div>
        """, unsafe_allow_html=True)

    # --- GRAPHIQUES ---
    st.divider()
    if not df_active.empty:
        g1, g2 = st.columns(2)
        with g1:
            fig = px.pie(df_active, names='Paiement', title="Répartition Paiement", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            # Compter les services (un peu plus complexe car pipe-separated)
            all_servs = []
            for s in df_active['Services'].dropna():
                all_servs.extend([x.strip() for x in s.split('|') if x.strip()])
            if all_servs:
                df_s = pd.DataFrame(all_servs, columns=['S']).value_counts().reset_index()
                fig2 = px.bar(df_s, x='count', y='S', orientation='h', title="Services les plus utilisés")
                st.plotly_chart(fig2, use_container_width=True)
