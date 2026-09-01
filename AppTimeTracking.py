import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
from safe_gsheets import safe_write

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
        "NETTOYAGES DES DONNEES CREOS", "BRIEFING DEV", "TEST EN ACCEPTANCE / PROD",
        "CALL TONY"
    ])
    USERS = ["Véronique Maigrié", "Sylvie Nyssen"]
    
    # Chargement avec cache pour éviter les erreurs API de Google
    try:
        df = conn.read(worksheet="TimeTracking", ttl=60).dropna(how="all")
    except:
        df = pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])

    if st.button("🔄 Rafraîchir l'affichage"):
        st.cache_data.clear()
        st.rerun()

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", USERS)
        
        # --- FIX CALENDRIER : On définit une plage min et max pour débloquer la navigation ---
        sel_date = st.date_input(
            "Date", 
            value=date.today(), 
            min_value=date(2023, 1, 1), 
            max_value=date(2030, 12, 31),
            format="DD/MM/YYYY"
        )
        
        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_timetracking_v6", clear_on_submit=True):
            q = st.number_input("Quantité", min_value=1, value=1)
            e = st.number_input("Nb Écoles", min_value=0, value=0) if tache == "NETTOYAGES DES DONNEES CREOS" else 0
            
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                new_row = pd.DataFrame([{"date": str(sel_date), "intervenante": user, "tache": tache, "quantite": q, "nb_ecoles": e}])
                df_final = pd.concat([df, new_row], ignore_index=True)
                safe_write(conn, "TimeTracking", df_final)
                st.cache_data.clear()
                st.rerun()

    with c2:
        st.subheader(f"📋 Détails du {sel_date.strftime('%d/%m/%Y')}")
        if not df.empty:
            df_view = df.copy()
            df_view["date"] = pd.to_datetime(df_view["date"], errors="coerce").dt.date
            df_j = df_view[df_view["date"] == sel_date]

            if not df_j.empty:
                for i, row in df_j.iterrows():
                    col_t, col_e, col_d = st.columns([0.7, 0.15, 0.15])
                    with col_t: st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")
                    
                    if col_e.button("✏️", key=f"ed_{i}"): 
                        st.session_state[f"edit_tt_{i}"] = True
                    if col_d.button("🗑️", key=f"de_{i}"): 
                        st.session_state[f"del_tt_{i}"] = True

                    # FORMULAIRE DE MODIFICATION
                    if st.session_state.get(f"edit_tt_{i}"):
                        with st.form(key=f"f_mod_{i}"):
                            u_idx = USERS.index(row['intervenante']) if row['intervenante'] in USERS else 0
                            new_u = st.selectbox("Nom", USERS, index=u_idx)
                            new_t = st.selectbox("Tâche", LISTE_TACHES, index=LISTE_TACHES.index(row['tache']) if row['tache'] in LISTE_TACHES else 0)
                            new_q = st.number_input("Quantité", min_value=1, value=int(row['quantite']))
                            if st.form_submit_button("✅ Valider"):
                                df.at[i, 'intervenante'] = new_u
                                df.at[i, 'tache'] = new_t
                                df.at[i, 'quantite'] = new_q
                                safe_write(conn, "TimeTracking", df)
                                del st.session_state[f"edit_tt_{i}"]
                                st.cache_data.clear()
                                st.rerun()

                    # SUPPRESSION
                    if st.session_state.get(f"del_tt_{i}"):
                        if st.button("Confirmer Suppression", key=f"c_{i}"):
                            df_new = df.drop(i).reset_index(drop=True)
                            safe_write(conn, "TimeTracking", df_new)
                            del st.session_state[f"del_tt_{i}"]
                            st.cache_data.clear()
                            st.rerun()
            else:
                st.info("Aucune donnée pour ce jour.")
        else:
            st.warning("Base de données vide.")

    st.divider()
    st.header("📊 Statistiques")
    if not df.empty:
        df_stats = df.copy()
        df_stats["date_only"] = pd.to_datetime(df_stats["date"], errors="coerce").dt.date
        per = st.date_input("Période", [min(df_stats['date_only']), max(df_stats['date_only'])], format="DD/MM/YYYY")
        if isinstance(per, list) and len(per) == 2:
            df_f = df_stats[(df_stats['date_only'] >= per[0]) & (df_stats['date_only'] <= per[1])]
            if not df_f.empty:
                st.plotly_chart(px.pie(df_f, names='tache', values='quantite', title="Répartition par Tâche"), use_container_width=True)
                df_synth = df_f.groupby('tache').agg({'quantite': 'sum'}).reset_index()
                df_synth.columns = ["Tâche", "Total"]; df_synth["Total"] = df_synth["Total"].astype(int)
                st.table(df_synth)
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Total"].sum()))
