import streamlit as st
import pandas as pd
from safe_gsheets import safe_write

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    st.subheader("⚙️ Configuration des Écoles")
    
    # Formulaire simplifié
    with st.form("config_school"):
        fase = st.text_input("Code FASE de l'école")
        extra = st.radio("Utilise Creos ?", ["Oui", "Non"])
        pay = st.selectbox("Paiement", ["Prépaiement", "Post-paiement"])
        servs = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Garderie", "Activités"])
        
        if st.form_submit_button("Enregistrer"):
            # Trouver la commune et province via df_ecoles
            ref = df_ecoles[df_ecoles['Fase école'] == fase]
            if ref.empty:
                st.error("Code FASE inconnu dans la liste FWB")
            else:
                new_row = pd.DataFrame([{
                    "Fase école": fase,
                    "Commune": ref.iloc[0]['Commune'],
                    "Province": ref.iloc[0]['Province'],
                    "Extrascolaire": extra,
                    "Paiement": pay if extra == "Oui" else "",
                    "Services": "|".join(servs) if extra == "Oui" else ""
                }])
                df_updated = pd.concat([df_config[df_config['Fase école'] != fase], new_row])
                safe_write(conn, "EcolesConfig", df_updated)
                st.success("Configuration enregistrée !")
                st.cache_data.clear()
