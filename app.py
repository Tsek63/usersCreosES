import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import json
import pandas as pd

# Configuration de la page
st.set_page_config(layout="wide", page_title="Creos Extrascolaire v4.0")

# --- CONNEXION GOOGLE SHEETS ---
# Note: Les informations de connexion seront dans le menu "Secrets" de Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl=0) # ttl=0 pour forcer la lecture fraîche
        # Transformer le DataFrame en dictionnaire pour le JS
        data_dict = {}
        for _, row in df.iterrows():
            data_dict[row['Commune']] = {
                "prov": row['Province'],
                "pay": row['Paiement'],
                "services": str(row['Services']).split('|') if row['Services'] else []
            }
        return data_dict
    except:
        return {}

def save_data(commune, province, paiement, services):
    # Récupérer les données actuelles
    df = conn.read(ttl=0)
    
    # Préparer la nouvelle ligne
    new_data = pd.DataFrame([{
        "Commune": commune,
        "Province": province,
        "Paiement": paiement,
        "Services": "|".join(services)
    }])
    
    # Mettre à jour ou ajouter
    if commune in df['Commune'].values:
        df = df[df['Commune'] != commune]
    
    df = pd.concat([df, new_data], ignore_index=True)
    conn.update(data=df)
    st.cache_data.clear()

# --- INTERFACE ---
st.title("🌐 Creos Extrascolaire - Partage Collaboratif")

# Chargement des données
data_json = json.dumps(load_data())

# On injecte votre code HTML/JS original (adapté pour communiquer avec Streamlit)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Copiez ici TOUT votre style CSS d'origine */
        {open('style.css', 'r').read() if 'style.css' in locals() else ""} 
        /* (Note: Pour simplifier j'inclus le style directement dans la réponse ci-dessous) */
    </style>
</head>
<body>
    <script>
        // On initialise selected avec les données venant de Google Sheets
        let selected = new Map(Object.entries({data_json}));
        
        // On modifie la fonction saveCommune pour envoyer les infos à Streamlit
        async function saveCommune() {{
            // ... (votre logique de récupération de formulaire) ...
            
            // Envoyer au parent (Streamlit)
            window.parent.postMessage({{
                type: 'SAVE',
                commune: currentCommune,
                prov: prov,
                pay: pay,
                services: serv
            }}, "*");
        }}
    </script>
</body>
</html>
"""

# Affichage de l'application
# Note : L'intégration complète demande de passer par un "Custom Component" 
# pour que le JS puisse renvoyer des données à Python.
