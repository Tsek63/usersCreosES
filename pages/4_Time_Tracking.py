import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.title("⏱️ Time Tracking")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Data", ttl=0)
except Exception as e:
    st.error(f"Erreur lecture Data : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune donnée")
    st.stop()

intervenantes = sorted(df["intervenante"].dropna().unique())

user = st.selectbox("Intervenante", intervenantes)

df_user = df[df["intervenante"] == user]

st.dataframe(df_user)

st.markdown("### Ajouter une entrée")

col1, col2 = st.columns(2)

with col1:
    jour = st.date_input("Date", value=date.today())
    tache = st.text_input("Tâche")

with col2:
    quantite = st.number_input("Quantité", 0)
    nb_ecoles = st.number_input("Nombre d'écoles", 0)

if st.button("Ajouter entrée"):

    new_row = pd.DataFrame({
        "date": [jour],
        "intervenante": [user],
        "tache": [tache],
        "quantite": [quantite],
        "nb_ecoles": [nb_ecoles]
    })

    df = pd.concat([df, new_row], ignore_index=True)

    conn.update(
        worksheet="Data",
        data=df
    )

    st.success("Entrée ajoutée")
