import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date

from data_manager import DataManager
from ui_components import inject_custom_css
from tabs import dashboard, school_search, config_schools
import AppTimeTracking

st.set_page_config(layout="wide", page_title="Creos Extrascolaire")
inject_custom_css()

conn = st.connection("gsheets", type=GSheetsConnection)
dm = DataManager(conn)

# Chargement centralisé
df_ecoles, df_config, df_contacts, data_fwb = dm.load_all_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau de bord", "🏫 Écoles par Commune", "⚙️ Gestion des Écoles", "⏱️ Time Tracking"
])

with tab1:
    dashboard.render(df_ecoles, df_config, data_fwb, df_contacts)

with tab2:
    # On envoie bien les 5 éléments requis
    school_search.render(conn, df_ecoles, df_config, data_fwb, df_contacts)

with tab3:
    config_schools.render(conn, df_ecoles, df_config, data_fwb)

with tab4:
    AppTimeTracking.run(conn)

# Copyright dynamique
st.markdown(f'<div style="text-align:center; padding:20px; color:gray; font-size:11px;">© AJH & Creos Extrascolaire {date.today().year}</div>', unsafe_allow_html=True)
