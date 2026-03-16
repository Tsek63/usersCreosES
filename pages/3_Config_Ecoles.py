import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("⚙️ Configuration des écoles")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="EcolesConfig", ttl=0)
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lecture feuille Config : {e}")
