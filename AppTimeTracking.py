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

    # --- CONFIGURATION ---
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
    
    # --- LAYOUT ENCODAGE ---
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
                new_row = pd.DataFrame([{
                    "date": str(selected_date),
                    "intervenante": user,
                    "tache": tache,
                    "quantite": int(quantite),
                    "nb_ecoles": int(nb_ecoles)
                }])
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
                    if st.button("🗑️", key=f"del_tt_{i}"):
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

    # =========================================================================
    # SECTION STATISTIQUES (Formatage des nombres corrigé)
    # =========================================================================
    st.divider()
    st.header("📊 Statistiques & Synthèse")

    if not df.empty:
        df_stats = df.copy()
        df_stats["date"] = pd.to_datetime(df_stats["date"], errors="coerce").dt.date
        
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            d_min = df_stats['date'].min() if not df_stats['date'].isnull().all() else date.today()
            d_max = df_stats['date'].max() if not df_stats['date'].isnull().all() else date.today()
            per = st.date_input("Période", [d_min, d_max])

        with f2:
            ints = sorted(df_stats["intervenante"].unique())
            f_int = st.multiselect("Intervenantes", ints, default=ints)

        with f3:
            f_tac = st.multiselect("Filtrer Tâches", LISTE_TACHES)

        if isinstance(per, (list, tuple)) and len(per) == 2:
            mask = (df_stats['date'] >= per[0]) & (df_stats['date'] <= per[1])
            df_f = df_stats[mask]
        else:
            df_f = df_stats.copy()

        if f_int: df_f = df_f[df_f['intervenante'].isin(f_int)]
        if f_tac: df_f = df_f[df_f['tache'].isin(f_tac)]

        if not df_f.empty:
            g1, g2 = st.columns(2)
            with g1:
                fig1 = px.pie(df_f, names='intervenante', values='quantite', color='intervenante',
                             color_discrete_map=COULEURS_MAP, title="Par Intervenante")
                st.plotly_chart(fig1, use_container_width=True)
            with g2:
                fig2 = px.pie(df_f, names='tache', values='quantite', title="Par Tâche")
                st.plotly_chart(fig2, use_container_width=True)

            # --- SYNTHÈSE TABLEAU AVEC FORMAT ENTIER ---
            st.markdown("---")
            df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
            df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
            
            # CORRECTION ICI : Conversion en entier pour supprimer les .0000
            df_synth["Total Quantité"] = df_synth["Total Quantité"].astype(int)
            df_synth["Total Écoles"] = df_synth["Total Écoles"].astype(int)
            
            col_table, col_metric = st.columns([3, 1])
            with col_table:
                # Utilisation de dataframe pour un rendu propre
                st.dataframe(df_synth, use_container_width=True, hide_index=True)
            
            with col_metric:
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Total Quantité"].sum()), "actions")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_synth.to_excel(writer, index=False, sheet_name='Synthese')
                st.download_button("📥 Export Synthèse Excel", output.getvalue(), "synthese_time.xlsx", use_container_width=True)
        else:
            st.info("Aucune donnée pour les filtres sélectionnés.")
    else:
        st.info("Aucune donnée enregistrée.")
