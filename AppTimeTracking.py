import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import io
from safe_gsheets import safe_write

@st.cache_data(ttl=60)
def load_timetracking(_conn):
    try:
        df = _conn.read(worksheet="TimeTracking", ttl=60).dropna(how="all")
        return df
    except Exception:
        return pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])

def run(conn):
    st.subheader("⏱️ Time Tracking")
    LISTE_TACHES = sorted([
        "DEPANNAGE TELEPHONIQUE", "DEPANNAGE MAIL", "SUIVI DEPLOIEMENT TELEPHONIQUE",
        "SUIVI DEPLOIEMENT MAIL", "VISIO DE PRESENTATION", "VISIO DIVERS",
        "MAIL DIVERS", "MODIFICATIONS FICHIER PO", "JOURNEE DE FORMATION",
        "SUIVI ADMIN FORMATION", "MATINEE D'ACCOMPAGNEMENT",
        "SUIVI MATINEE D'ACCOMPAGNEMENT", "ENCODAGE TICKET", "SUIVI FICHIER TICKETS",
        "MODIFICATION - CREATION DOC", "MODIFICATION – CREATION VIDEO",
        "NETTOYAGES DES DONNEES CREOS", "BRIEFING DEV", "TEST EN ACCEPTANCE / PROD"
    ])
    COULEURS_MAP = {"Véronique Maigrié": "#FF00FF", "Sylvie Nyssen": "#008080"}

    df = load_timetracking(conn)
    if df.empty:
        st.warning("Aucune donnée enregistrée.")
        # On crée un DF vide avec colonnes pour éviter les erreurs
        df = pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", ["Véronique Maigrié", "Sylvie Nyssen"])
        selected_date = st.date_input("Date", value=date.today())
        tache = st.selectbox("Tâche", LISTE_TACHES)
        with st.form("form_saisie", clear_on_submit=True):
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
            nb_ecoles = 0
            if tache == "NETTOYAGES DES DONNEES CREOS":
                nb_ecoles = st.number_input("Nombre d'écoles", min_value=1, step=1, value=1)
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                new_row = pd.DataFrame([{"date": str(selected_date), "intervenante": user, "tache": tache, "quantite": int(quantite), "nb_ecoles": int(nb_ecoles)}])
                df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                df_updated = pd.concat([df_live, new_row], ignore_index=True)
                safe_write(conn, "TimeTracking", df_updated)
                st.cache_data.clear()
                st.rerun()

    with c2:
        st.subheader(f"📋 Détails du {selected_date.strftime('%d/%m/%Y')}")
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        df_j = df_copy[df_copy["date"] == selected_date]

        if not df_j.empty:
            for i, row in df_j.iterrows():
                col_txt, col_btn = st.columns([0.80, 0.20])
                with col_txt:
                    st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")
                with col_btn:
                    # FIX : Clé unique pour éviter le crash DuplicateElementKey
                    if st.button("🗑️", key=f"del_tt_{i}_{row['intervenante'][:3]}"):
                        st.session_state[f"confirm_{i}"] = True
                    if st.session_state.get(f"confirm_{i}"):
                        if st.button("OUI ✅", key=f"yes_{i}"):
                            df_updated = df.drop(i).reset_index(drop=True)
                            safe_write(conn, "TimeTracking", df_updated)
                            st.cache_data.clear()
                            del st.session_state[f"confirm_{i}"]
                            st.rerun()
        else:
            st.info("Aucune donnée pour ce jour.")

    st.divider()
    st.header("📊 Statistiques & Synthèse")
    if not df.empty:
        # (Le reste de votre code de statistiques reste ici...)
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        # ... filtres et graphiques plotly ...
        st.info("Utilisez les filtres pour analyser les données.")
