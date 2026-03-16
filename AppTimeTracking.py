def run(conn):
    import streamlit as st
    import pandas as pd
    from datetime import date

    st.subheader("⏱️ Time Tracking")

    # --------------------------------------------
    # Lecture des données depuis Google Sheet
    # --------------------------------------------
    try:
        df = conn.read(worksheet="Data", ttl=0)
    except Exception as e:
        st.error(f"Erreur chargement Data : {e}")
        return

    if df.empty:
        st.warning("Aucune donnée")
        return

    # --------------------------------------------
    # Sélection de l'intervenante
    # --------------------------------------------
    intervenantes = sorted(df["intervenante"].dropna().unique())
    user = st.selectbox("Intervenante", intervenantes)

    # --------------------------------------------
    # Sélection de la date
    # --------------------------------------------
    selected_date = st.date_input("Date", value=date.today())

    # --------------------------------------------
    # Sélection de la tâche / action
    # --------------------------------------------
    taches = sorted(df["tache"].dropna().unique())
    tache = st.selectbox("Tâche", taches)

    # --------------------------------------------
    # Encodage des nombres
    # --------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        quantite = st.number_input("Quantité", 0)

    with col2:
        nb_ecoles = 0
        if tache == "NETTOYAGE DES DONNEES":
            nb_ecoles = st.number_input("Nombre d'écoles", 0)

    # --------------------------------------------
    # Bouton d'ajout
    # --------------------------------------------
    if st.button("Ajouter entrée"):

        # Préparer la nouvelle ligne
        new_row = pd.DataFrame({
            "date": [selected_date],
            "intervenante": [user],
            "tache": [tache],
            "quantite": [quantite],
            "nb_ecoles": [nb_ecoles]
        })

        # Ajouter à la table existante
        df = pd.concat([df, new_row], ignore_index=True)

        # Mise à jour Google Sheet
        conn.update(
            worksheet="Data",
            data=df
        )

        st.success("Entrée ajoutée avec succès !")

    # --------------------------------------------
    # Filtrer pour affichage des graphiques et synthèse
    # --------------------------------------------
    df_filtered = df[df["intervenante"] == user]
    df_filtered = df_filtered[df_filtered["date"] == pd.to_datetime(selected_date)]

    st.markdown("### Historique de l'intervenante pour la date sélectionnée")
    st.dataframe(df_filtered)

    # --------------------------------------------
    # Graphiques et synthèse par tâche
    # --------------------------------------------
    if not df_filtered.empty:
        st.markdown("### Graphiques par tâche")
        # Graphique 1 : quantite par tâche
        fig1 = px.bar(df_filtered, x="tache", y="quantite", title="Quantité par tâche")
        st.plotly_chart(fig1, use_container_width=True)

        # Graphique 2 : nombre d'écoles par tâche (pour NETTOYAGE DES DONNEES)
        df_nb_ecoles = df_filtered[df_filtered["tache"] == "NETTOYAGE DES DONNEES"]
        if not df_nb_ecoles.empty:
            fig2 = px.bar(df_nb_ecoles, x="tache", y="nb_ecoles", title="Nombre d'écoles par tâche")
            st.plotly_chart(fig2, use_container_width=True)

        # Synthèse par tâche
        st.markdown("### Synthèse par tâche")
        summary = df_filtered.groupby("tache").agg({"quantite":"sum","nb_ecoles":"sum"}).reset_index()
        st.dataframe(summary)
