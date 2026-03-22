import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Imports de vos outils personnalisés (nouveaux fichiers)
from data_manager import DataManager
from ui_components import inject_style
from tabs import dashboard, school_search, config_schools

# 2. Import de VOTRE fichier original (celui auquel on ne touche pas)
import AppTimeTracking

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Injection du CSS (Header bleu, etc.)
inject_style()

# --- CONNEXION ET CHARGEMENT ---
conn = st.connection("gsheets", type=GSheetsConnection)
dm = DataManager(conn)

# On charge toutes les données proprement via le DataManager
df_ecoles, df_config, df_contacts, data_fwb = dm.load_all()

# --- CRÉATION DES ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau de bord", 
    "🏫 Écoles par Commune", 
    "⚙️ Gestion des Écoles", 
    "⏱️ Time Tracking"
])

# --- CONTENU DE CHAQUE ONGLET ---

with tab1:
    # On appelle la fonction render() du fichier tabs/dashboard.py
    dashboard.render(df_ecoles, df_config)

with tab2:
    # On appelle la fonction render() du fichier tabs/school_search.py
    school_search.render(df_ecoles, df_config, data_fwb, df_contacts)

with tab3:
    # On appelle la fonction render() du fichier tabs/config_schools.py
    config_schools.render(conn, df_ecoles, df_config, data_fwb)

with tab4:
    # On appelle DIRECTEMENT votre fichier original AppTimeTracking.py
    # On lui passe la connexion 'conn' comme il l'attendait
    AppTimeTracking.run(conn)

# --- FOOTER ---
st.markdown("""
    <div style="text-align: center; color: rgba(0,0,0,0.4); font-size: 11px; margin-top: 50px;">
        © AJH 2026 — Creos Extrascolaire (Version Modulaire)
    </div>
""", unsafe_allow_html=True)
