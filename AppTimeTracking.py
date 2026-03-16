def run(conn):

    import streamlit as st
    import pandas as pd
    from datetime import date

    st.subheader("⏱️ Time Tracking")

    # --------------------------------------------
    # CHARGEMENT DATA
    # --------------------------------------------

    try:
        df = conn.read(worksheet="Data", ttl=0)
    except Exception as e:
        st.error(f"Erreur chargement Data : {e}")
        return

    if df.empty:
        st.warning("Aucune donnée dans l'onglet Data")
        return

    # --------------------------------------------
    # FILTRES
    # --------------------------------------------

    utilisateurs = sorted(df["Utilisateur"].dropna().unique())

    user = st.selectbox(
        "Utilisateur",
        utilisateurs
    )

    df_user = df[df["Utilisateur"] == user]

    # --------------------------------------------
    # AJOUT D'UNE LIGNE
    # --------------------------------------------

    st.markdown("### Ajouter une entrée")

    col1, col2, col3 = st.columns(3)

    with col1:
        jour = st.date_input("Date", value=date.today())

    with col2:
        heures = st.number_input("Heures", 0.0, 24.0)

    with col3:
        ecole = st.text_input("École")

    if st.button("Ajouter"):

        new_row = pd.DataFrame({
            "Date": [jour],
            "Utilisateur": [user],
            "Ecole": [ecole],
            "Heures": [heures]
        })

        df = pd.concat([df, new_row], ignore_index=True)

        conn.update(
            worksheet="Data",
            data=df
        )

        st.success("Entrée ajoutée")

    # --------------------------------------------
    # TABLEAU
    # --------------------------------------------

    st.markdown("### Historique")

    st.dataframe(df_user)
