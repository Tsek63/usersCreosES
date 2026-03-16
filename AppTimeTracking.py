def run(conn):
    import streamlit as st
    import pandas as pd
    from datetime import date

    st.subheader("⏱️ Time Tracking")

    # -------------------------------
    # Lecture des données depuis Google Sheet
    # -------------------------------
    try:
        df = conn.read(worksheet="Data", ttl=0)
    except Exception as e:
        st.error(f"Erreur chargement Data : {e}")
        return

    if df.empty:
        st.warning("Aucune donnée")
        return

    # -------------------------------
    # Sélection de l'intervenante
    # -------------------------------
    intervenantes = sorted(df["intervenante"].dropna().unique())
    user = st.selectbox("Intervenante", intervenantes)

    # -------------------------------
    # Sélection de la date
    # -------------------------------
    selected_date = st.date_input("Date", value=date.today())

    # -------------------------------
    # Filtrer pour l'intervenante et la date
    # -------------------------------
    df_user = df[df["intervenante"] == user]
    df_user["date"] = pd.to_datetime(df_user["date"], errors="coerce")
    df_filtered = df_user[df_user["date"] == pd.to_datetime(selected_date)]

    # -------------------------------
    # Sélection de la tâche/action
    # -------------------------------
    taches = sorted(df["tache"].dropna().unique())
    tache = st.selectbox("Tâche", taches)

    # -------------------------------
    # Encodage des valeurs
    # -------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        quantite = st.number_input("Quantité", 0)
    with col2:
        nb_ecoles = 0
        if tache == "NETTOYAGE DES DONNEES":
            nb_ecoles = st.number_input("Nombre d'écoles", 0)
    with col3:
        # choix multiple pour d'autres options si nécessaire
        st.markdown("Choix multiples / paramètres supplémentaires (facultatif)")

    # -------------------------------
    # Bouton Ajouter
    # -------------------------------
    if st.button("Ajouter entrée"):
        new_row = {
            "date": selected_date,
            "intervenante": user,
            "tache": tache,
            "quantite": quantite,
            "nb_ecoles": nb_ecoles
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Mise à jour de la Google Sheet
        conn.update(worksheet="Data", data=df)

        st.success("Entrée ajoutée avec succès !")

    # -------------------------------
    # Graphiques et synthèse
    # -------------------------------
    st.markdown("### Graphiques et synthèse")
    if not df_filtered.empty:
        import plotly.express as px

        # Graphique 1 : Quantité par tâche
        fig1 = px.bar(df_filtered, x="tache", y="quantite", title="Quantité par tâche")
        st.plotly_chart(fig1, use_container_width=True)

        # Graphique 2 : Nombre d'écoles pour NETTOYAGE DES DONNEES
        df_nb = df_filtered[df_filtered["tache"] == "NETTOYAGE_DES_DONNEES"]
        if not df_nb.empty:
            fig2 = px.bar(df_nb, x="tache", y="nb_ecoles", title="Nombre d'écoles")
            st.plotly_chart(fig2, use_container_width=True)

        # Synthèse par tâche
        summary = df_filtered.groupby("tache").agg({"quantite":"sum","nb_ecoles":"sum"}).reset_index()
        st.markdown("### Synthèse par tâche")
        st.dataframe(summary)
