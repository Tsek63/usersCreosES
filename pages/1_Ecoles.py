import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🏫 Écoles")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Ecoles", ttl=0)
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lecture feuille Ecoles : {e}")
