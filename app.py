import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date # <--- Nouvel import

# Imports de nos fichiers
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

# Chargement
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

# --- FOOTER DYNAMIQUE ---
current_year = date.today().year
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: white; 
                text-align: center; padding: 10px; font-size: 12px; color: #64748b; 
                border-top: 1px solid #e2e8f0; z-index: 100;">
        © AJH - Creos Extrascolaire {current_year}
    </div>
    <div style="height: 50px;"></div> <!-- Espace pour éviter que le footer cache le contenu -->
""", unsafe_allow_html=True)
