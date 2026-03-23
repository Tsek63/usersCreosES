import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Imports de vos nouveaux fichiers
from data_manager import DataManager
from ui_components import inject_custom_css # Vérifiez bien ce nom
from tabs import dashboard, school_search, config_schools

# Import de votre fichier original intact
import AppTimeTracking

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# On appelle la fonction de design
inject_custom_css()

# Connexion et chargement via le DataManager
conn = st.connection("gsheets", type=GSheetsConnection)
dm = DataManager(conn)
df_ecoles, df_config, df_contacts, data_fwb = dm.load_all_data()

# --- ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau de bord", 
    "🏫 Écoles par Commune", 
    "⚙️ Gestion des Écoles", 
    "⏱️ Time Tracking"
])

with tab1:
    dashboard.render(df_ecoles, df_config, data_fwb)

with tab2:
    # On passe bien l'objet 'conn' pour la gestion des contacts
    school_search.render(conn, df_ecoles, df_config, data_fwb, df_contacts)

with tab3:
    # On passe bien l'objet 'conn' pour l'enregistrement des configs
    config_schools.render(conn, df_ecoles, df_config, data_fwb)

with tab4:
    AppTimeTracking.run(conn)
