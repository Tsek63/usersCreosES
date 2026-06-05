import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
from safe_gsheets import safe_write

@st.cache_data(ttl=60)
def load_timetracking(_conn):
    try:
        df = _conn.read(worksheet="TimeTracking", ttl=60).dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])
        return df
    except:
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
        "NETTOYAGES DES DONNEES CREOS", "BRIEFING DEV", "TEST EN ACCEPTANCE / PROD",
        "CALL TONY"
    ])

    USERS = ["Véronique Maigrié", "Sylvie Nyssen"]
    df = load_timetracking(conn)

    # Petit indicateur de santé
    if df.empty:
        st.warning("⚠️ La base de données semble vide. Si ce n'est pas normal, cliquez sur Actualiser.")

    if st.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()

    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", USERS)
        sel_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_v5", clear_on_submit=True):
            q = st.number_input("Quantité", min_value=1, value=1)
            e = st.number_input("Nombre d'écoles", min_value=0, value=0) if tache == "NETTOYAGES DES DONNEES CREOS" else 0

            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                # On relit le live pour ne rien perdre
                df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                new_row = pd.DataFrame([{"date": str(sel_date), "intervenante": user, "tache": tache, "quantite": q, "nb_ecoles": e}])
                
                df_final = pd.concat([df_live, new_row], ignore_index=True)
                safe_write(conn, "TimeTracking", df_final)
                st.cache_data.clear()
                st.rerun()

    with c2:
        st.subheader(f"📋 Détails du {sel_date.strftime('%d/%m/%Y')}")
        df_view = df.copy()
        df_view["date"] = pd.to_datetime(df_view["date"], errors="coerce").dt.date
        df_j = df_view[df_view["date"] == sel_date]

        if not df_j.empty:
            for i, row in df_j.iterrows():
                col_t, col_e, col_d = st.columns([0.7, 0.15, 0.15])
                with col_t:
                    st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")
                
                if col_e.button("✏️", key=f"edit_{i}"):
                    st.session_state[f"editing_{i}"] = True
                
                if col_d.button("🗑️", key=f"del_{i}"):
                    st.session_state[f"confirm_{i}"] = True

                if st.session_state.get(f"editing_{i}"):
                    with st.form(key=f"f_mod_{i}"):
                        u_idx = USERS.index(row['intervenante']) if row['intervenante'] in USERS else 0
                        new_u = st.selectbox("Intervenante", USERS, index=u_idx)
                        try: d_val = datetime.strptime(str(row['date']), "%Y-%m-%d").date()
                        except: d_val = date.today()
                        new_d = st.date_input("Date", value=d_val, format="DD/MM/YYYY")
                        new_t = st.selectbox("Tâche", LISTE_TACHES, index=LISTE_TACHES.index(row['tache']) if row['tache'] in LISTE_TACHES else 0)
                        new_q = st.number_input("Quantité", min_value=1, value=int(row['quantite']))
                        new_nb = st.number_input("Écoles", value=int(row['nb_ecoles'])) if new_t == "NETTOYAGES DES DONNEES CREOS" else 0
                        
                        if st.form_submit_button("✅ Valider"):
                            df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                            df_live.at[i, 'intervenante'] = new_u
                            df_live.at[i, 'date'] = str(new_d)
                            df_live.at[i, 'tache'] = new_t
                            df_live.at[i, 'quantite'] = new_q
                            df_live.at[i, 'nb_ecoles'] = new_nb
                            safe_write(conn, "TimeTracking", df_live)
                            del st.session_state[f"editing_{i}"]
                            st.cache_data.clear(); st.rerun()

                if st.session_state.get(f"confirm_{i}"):
                    if st.button("Confirmer Suppression ?", key=f"conf_{i}"):
                        df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                        df_upd = df_live.drop(i).reset_index(drop=True)
                        safe_write(conn, "TimeTracking", df_upd)
                        del st.session_state[f"confirm_{i}"]
                        st.cache_data.clear(); st.rerun()
        else:
            st.info("Aucune donnée.")

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
                df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
                df_synth.columns = ["Tâche", "Quantité", "Écoles"]
                df_synth["Quantité"] = df_synth["Quantité"].astype(int)
                df_synth["Écoles"] = df_synth["Écoles"].astype(int)
                st.table(df_synth)
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Quantité"].sum()))
