import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

import AppTimeTracking

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Gestion des écoles",
    layout="wide"
)

st.title("Gestion des écoles")

# -------------------------------------------------
# CONNEXION GOOGLE SHEETS
# -------------------------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)

import streamlit as st
import AppTimeTracking

st.set_page_config(layout="wide")

tab1, tab2 = st.tabs(["Test", "Time Tracking"])

with tab1:
    st.write("L'app fonctionne")

with tab2:
    AppTimeTracking.run()



# -------------------------------------------------
# CHARGEMENT DES DONNEES
# -------------------------------------------------

try:
    df_ecoles = conn.read(worksheet="Ecoles", ttl=0)
except:
    df_ecoles = pd.DataFrame()

# -------------------------------------------------
# TABS
# -------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau de bord et Carte",
    "🏫 Écoles par Commune",
    "⚙️ Gestion des Écoles",
    "⏱️ Time Tracking"
])

# -------------------------------------------------
# TAB 1
# -------------------------------------------------

with tab1:

    st.subheader("Tableau de bord")

    if df_ecoles.empty:
        st.warning("Aucune donnée")
    else:
        st.write("Nombre d'écoles :", len(df_ecoles))
        st.dataframe(df_ecoles)

# -------------------------------------------------
# TAB 2
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

# -------------------------------------------------
# TAB 3
# -------------------------------------------------

with tab3:

    st.subheader("Gestion des écoles")

    if df_ecoles.empty:
        st.warning("Pas de données")
    else:
        st.data_editor(df_ecoles)

# -------------------------------------------------
# TAB 4 : TIME TRACKING
# -------------------------------------------------

with tab4:
    AppTimeTracking.run(conn)
