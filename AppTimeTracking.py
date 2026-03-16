def run(conn):
    import streamlit as st
    import pandas as pd
    from datetime import date, timedelta

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

    # Convertir la colonne 'date' en datetime
df_user["date"] = pd.to_datetime(df_user["date"], errors="coerce")

# Filtrage sur période
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", value=date.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("Date de fin", value=date.today())

# Conversion en datetime
df_user["date"] = pd.to_datetime(df_user["date"], errors="coerce")

mask = (df_user["date"] >= pd.to_datetime(start_date)) & (df_user["date"] <= pd.to_datetime(end_date))
df_filtered = df_user.loc[mask]

st.markdown("### Historique")
st.dataframe(df_filtered)

    # --------------------------------------------
    # Ajouter une nouvelle entrée
    # --------------------------------------------
    st.markdown("### Ajouter une entrée")
    col1, col2, col3 = st.columns(3)

    with col1:
        jour = st.date_input("Date", value=date.today())
        tache = st.text_input("Tâche")

    with col2:
        quantite = st.number_input("Quantité", 0)
        nb_ecoles = st.number_input("Nombre d'écoles", 0)

    with col3:
        # choix multiple pour les écoles
        ecoles = df["Ecole"].dropna().unique().tolist()
        selected_ecoles = st.multiselect("Écoles", options=ecoles)

    if st.button("Ajouter entrée"):
        new_rows = []
        for ecole in selected_ecoles:
            new_rows.append({
                "date": jour,
                "intervenante": user,
                "tache": tache,
                "quantite": quantite,
                "nb_ecoles": nb_ecoles,
                "Ecole": ecole
            })
        df_new = pd.DataFrame(new_rows)

        df = pd.concat([df, df_new], ignore_index=True)

        # mise à jour de la Google Sheet
        conn.update(
            worksheet="Data",
            data=df
        )

        st.success("Entrées ajoutées avec succès !")

    # --------------------------------------------
    # Affichage final
    # --------------------------------------------
    st.markdown("### Historique complet filtré")
    st.dataframe(df_filtered)
