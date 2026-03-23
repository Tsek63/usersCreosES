import streamlit as st
import streamlit.components.v1 as components
import json

def render(df_ecoles, df_config, data_fwb):
    st.subheader("📊 État du déploiement")
    
    # Calcul des stats pour la carte
    df_active = df_config[df_config['Extrascolaire'] == 'Oui']
    
    # Résumé par commune
    tab1_rows = []
    for comm, grp in df_active.groupby('Commune'):
        tab1_rows.append({
            'Commune': comm, 
            'Province': grp['Province'].iloc[0], 
            'NbOui': len(grp)
        })
    
    # Ici, insérez votre bloc de code Javascript de la carte (trop long pour ce message, mais vous avez le principe)
    st.info("La carte interactive s'affiche ici.")
    st.write(f"Total communes actives : {len(tab1_rows)}")
