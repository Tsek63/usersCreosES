import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Imports de nos fichiers (Vérifiez bien que les fichiers sont dans le même dossier)
from data_manager import DataManager
from ui_components import inject_custom_css
from tabs import dashboard, school_search, config_schools
import AppTimeTracking

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")
inject_custom_css()

# Connexion
conn = st.connection("gsheets", type=GSheetsConnection)
dm = DataManager(conn)

# Chargement (Cette ligne doit correspondre au nom dans data_manager.py)
df_ecoles, df_config, df_contacts, data_fwb = dm.load_all_data()

# --- ONGLETS ---
t1, t2, t3, t4 = st.tabs([
    "📊 Tableau de bord", 
    "🏫 Écoles par Commune", 
    "⚙️ Gestion des Écoles", 
    "⏱️ Time Tracking"
])

with t1:
    dashboard.render(df_ecoles, df_config, data_fwb)

with t2:
    school_search.render(conn, df_ecoles, df_config, data_fwb, df_contacts)

with t3:
    config_schools.render(conn, df_ecoles, df_config, data_fwb)

with t4:
    AppTimeTracking.run(conn)
