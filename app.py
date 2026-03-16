import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

import AppTimeTracking

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

st.set_page_config(layout="wide")

st.title("Gestion des écoles")

# -------------------------------------------------
# CONNEXION GOOGLE SHEETS
# -------------------------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)

# -------------------------------------------------
# CHARGEMENT DES DONNEES
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
# TABS
# -------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tableau de bord",
    "🏫 Écoles",
    "👥 Contacts",
    "⚙️ Configuration",
    "⏱️ Time Tracking"
])

# -------------------------------------------------
# TAB 1
# -------------------------------------------------

with tab1:

    st.subheader("Tableau de bord")

    if df_ecoles.empty:
        st.warning("Pas de données")
    else:
        st.write("Nombre d'écoles :", len(df_ecoles))

# -------------------------------------------------
# TAB 2
# -------------------------------------------------

with tab2:

    st.subheader("Écoles")

    if df_ecoles.empty:
        st.warning("Pas de données")
    else:
        st.dataframe(df_ecoles)

# -------------------------------------------------
# TAB 3
# -------------------------------------------------

with tab3:

    st.subheader("Contacts")

    if df_contacts.empty:
        st.warning("Pas de contacts")
    else:
        st.dataframe(df_contacts)

# -------------------------------------------------
# TAB 4
# -------------------------------------------------

with tab4:

    st.subheader("Configuration écoles")

    if df_config.empty:
        st.warning("Pas de configuration")
    else:
        st.dataframe(df_config)

# -------------------------------------------------
# TAB 5
# -------------------------------------------------

with tab5:

    AppTimeTracking.run(conn)
