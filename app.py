import streamlit as st
import pandas as pd
import plotly.express as px
# ... tous tes autres imports existants
import AppTimeTracking  # <-- nouvel onglet Time Tracking

# Import nécessaire pour Google Sheets
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------
# Configuration de la page
# -------------------------------------------------
st.set_page_config(layout="wide")
st.title("Gestion des écoles")

# -------------------------------------------------
# Connexion Google Sheets
# -------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

# -------------------------------------------------
# Chargement des données existantes
# -------------------------------------------------
try:
    df_ecoles = conn.read(worksheet="Ecoles", ttl=0)
except:
    df_ecoles = pd.DataFrame()

try:
    df_contacts = conn.read(worksheet="Contacts", ttl=0)
except:
    df_contacts = pd.DataFrame()

try:
    df_config = conn.read(worksheet="EcolesConfig", ttl=0)
except:
    df_config = pd.DataFrame()

# -------------------------------------------------
# Définition des onglets
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tableau de bord et Carte",
    "🏫 Écoles par Commune",
    "👥 Contacts",
    "⚙️ Gestion des Écoles",
    "⏱️ Time Tracking"
])

# -------------------------------------------------
# TAB 1 : Tableau de bord
# -------------------------------------------------
with tab1:
    st.subheader("Tableau de bord")
    if df_ecoles.empty:
        st.warning("Pas de données")
    else:
        st.write("Nombre d'écoles :", len(df_ecoles))
        st.dataframe(df_ecoles)
    # --- tes graphes existants restent ici ---

# -------------------------------------------------
# TAB 2 : Écoles par commune
# -------------------------------------------------
with tab2:
    st.subheader("Écoles par commune")
    if df_ecoles.empty:
        st.warning("Pas de données")
    else:
        communes = sorted(df_ecoles["Commune"].dropna().unique())
        commune = st.selectbox("Choisir une commune", communes)
        df_filtre = df_ecoles[df_ecoles["Commune"] == commune]
        st.dataframe(df_filtre)
    # --- tes filtres et cartes restent ici ---

# -------------------------------------------------
# TAB 3 : Contacts
# -------------------------------------------------
with tab3:
    st.subheader("Contacts")
    if df_contacts.empty:
        st.warning("Pas de contacts")
    else:
        st.dataframe(df_contacts)

# -------------------------------------------------
# TAB 4 : Gestion des écoles
# -------------------------------------------------
with tab4:
    st.subheader("Configuration écoles")
    if df_config.empty:
        st.warning("Pas de configuration")
    else:
        st.dataframe(df_config)

# -------------------------------------------------
# TAB 5 : Time Tracking
# -------------------------------------------------
with tab5:
    try:
        AppTimeTracking.run(conn)  # <-- ton code Time Tracking complet
    except Exception as e:
        st.error(f"Erreur Time Tracking : {e}")
