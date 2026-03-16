def run(conn):
    import streamlit as st
    from streamlit_gsheets import GSheetsConnection
    import pandas as pd
    from datetime import date
    import plotly.express as px

    st.subheader("⏱️ Time Tracking")

    # --- CONNEXION SPÉCIFIQUE AU SHEET TIMETRACKING ---
    # (On peut utiliser la connexion passée en paramètre si c'est le bon sheet)
    # Sinon, créer une nouvelle connexion avec un ID de sheet différent
    
    # Essayer d'abord avec la connexion fournie
    try:
        df = conn.read(worksheet="Data", ttl=0)
        if df.empty:
            st.info("Aucune donnée dans la feuille TimeTracking/Data")
            return
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.warning("⚠️ Assurez-vous que la connexion pointe vers le bon Google Sheet (ID: 195v8jf2n1jjVQuWlw1s_ka32bu0K13mGrTUnksEp3GU)")
        return

    # --- PARAMÈTRES ---
    LISTE_TACHES = [
        "DEPANNAGE TELEPHONIQUE", "DEPANNAGE MAIL", "SUIVI DEPLOIEMENT TELEPHONIQUE",
        "SUIVI DEPLOIEMENT MAIL", "VISIO DE PRESENTATION", "VISIO DIVERS",
        "MAIL DIVERS", "MODIFICATIONS FICHIER PO", "JOURNEE DE FORMATION",
        "SUIVI ADMIN FORMATION", "MATINEE D'ACCOMPAGNEMENT", 
        "SUIVI MATINEE D'ACCOMPAGNEMENT", "ENCODAGE TICKET", "SUIVI FICHIER TICKETS",
        "MODIFICATION - CREATION DOC", "MODIFICATION – CREATION VIDEO",
        "NETTOYAGES DES DONNEES CREOS", "Briefing DEV"
    ]

    COULEURS_MAP = {
        "Véronique Maigrié": "#FF00FF",
        "Sylvie Nyssen": "#008080"
    }

    # --- LAYOUT EN 2 COLONNES ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")
        
        intervenantes = sorted(df["intervenante"].dropna().unique())
        user = st.selectbox("Intervenante", intervenantes)
        selected_date = st.date_input("Date", value=date.today())
        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_saisie", clear_on_submit=True):
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
            nb_ecoles = 0
            if tache == "NETTOYAGES DES DONNEES CREOS":
                nb_ecoles = st.number_input("Nombre d'écoles", min_value=1, step=1, value=1)
            
            if st.form_submit_button("💾 Enregistrer"):
                new_row = {
                    "date": str(selected_date),
                    "intervenante": user,
                    "tache": tache,
                    "quantite": int(quantite),
                    "nb_ecoles": int(nb_ecoles)
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="Data", data=df)
                st.success("✅ Entrée ajoutée avec succès !")
                st.rerun()

    # --- COLONNE 2 : DÉTAILS DU JOUR ---
    with c2:
        st.subheader(f"📋 Détails du {selected_date.strftime('%d/%m/%Y')}")
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        df_j = df_copy[df_copy["date"] == selected_date].copy()
        
        if not df_j.empty:
            for i, row in df_j.iterrows():
                ca, cb = st.columns([5, 1])
                ca.write(f"**{row['intervenante']}** | {row['tache']} ({int(row['quantite'])})")
        else:
            st.info("Aucune donnée pour ce jour.")

    # --- SECTION STATISTIQUES ---
    st.divider()
    st.header("📊 Statistiques & Synthèse")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date

    if not df_copy.empty:
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            per = st.date_input("Sélectionnez la période", 
                               [min(df_copy['date']), max(df_copy['date'])])
        
        date_start = per[0] if isinstance(per, (list, tuple)) else per
        date_end = per[1] if isinstance(per, (list, tuple)) and len(per) == 2 else date_start
        
        with f2:
            intervenantes_list = sorted(df_copy["intervenante"].dropna().unique())
            f_int = st.multiselect("Filtrer Intervenantes", intervenantes_list, 
                                   default=intervenantes_list)
        with f3:
            f_tac = st.multiselect("Filtrer Tâches", LISTE_TACHES)

        df_f = df_copy.copy()
        df_f = df_f[(df_f['date'] >= date_start) & (df_f['date'] <= date_end)]
        
        if f_int: 
            df_f = df_f[df_f['intervenante'].isin(f_int)]
        if f_tac: 
            df_f = df_f[df_f['tache'].isin(f_tac)]

        if not df_f.empty:
            g1, g2 = st.columns(2)
            with g1:
                fig1 = px.pie(df_f, names='intervenante', values='quantite', 
                            color='intervenante', color_discrete_map=COULEURS_MAP,
                            title="Répartition par Intervenante")
                st.plotly_chart(fig1, use_container_width=True)
            with g2:
                fig2 = px.pie(df_f, names='tache', values='quantite',
                            title="Répartition par Tâche",
                            color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")
            
            df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
            df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
            
            st.subheader("📋 Synthèse par tâche")
            st.table(df_synth)
            st.metric(label="TOTAL GÉNÉRAL", value=int(df_synth["Total Quantité"].sum()))
            
        else:
            st.warning("Aucune donnée pour les filtres sélectionnés.")
    else:
        st.info("La base est vide.")
