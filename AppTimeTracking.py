def run(conn):
    import streamlit as st
    import pandas as pd
    from datetime import date

    st.subheader("⏱️ Time Tracking")

    try:
        df = conn.read(worksheet="Data", ttl=0)
    except Exception as e:
        st.error(f"Erreur chargement Data : {e}")
        return

    if df.empty:
        st.warning("Aucune donnée")
        return

    intervenantes = sorted(df["intervenante"].dropna().unique())
    user = st.selectbox("Intervenante", intervenantes)
    st.dataframe(df[df["intervenante"] == user])
