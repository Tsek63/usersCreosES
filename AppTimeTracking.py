import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import io
from safe_gsheets import safe_write

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60)
def load_timetracking(_conn):
    try:
        # On lit la feuille
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
        "NETTOYAGES DES DONNEES CREOS", "BRIEFING DEV", "TEST EN ACCEPTANCE / PROD",
        "CALL TONY"
    ])

    LISTE_USERS = ["Véronique Maigrié", "Sylvie Nyssen"]
    COULEURS_MAP = {"Véronique Maigrié": "#FF00FF", "Sylvie Nyssen": "#008080"}

    # Bouton pour forcer la mise à jour si besoin
    if st.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()

    df = load_timetracking(conn)

    # --- LAYOUT ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", LISTE_USERS)
        selected_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        
        # Alerte week-end
        is_weekend = selected_date.weekday() >= 5
        if is_weekend:
            st.error("⚠️ Date de week-end sélectionnée.")
            confirm_wk = st.checkbox("Confirmer l'encodage le week-end")
        else:
            confirm_wk = True

        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_saisie_secure", clear_on_submit=True):
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
            nb_ecoles = 0
            if tache == "NETTOYAGES DES DONNEES CREOS":
                nb_ecoles = st.number_input("Nombre d'écoles", min_value=0, value=1)

            submit_ready = not is_weekend or (is_weekend and confirm_wk)
            
            if st.form_submit_button("💾 Enregistrer", use_container_width=True, disabled=not submit_ready):
                # --- SÉCURITÉ ANTI-EFFACEMENT ---
                # On récupère la version la plus fraîche possible avant d'ajouter
                try:
                    df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                except:
                    df_live = df.copy()
                
                new_row = pd.DataFrame([{
                    "date": str(selected_date),
                    "intervenante": user,
                    "tache": tache,
                    "quantite": int(quantite),
                    "nb_ecoles": int(nb_ecoles)
                }])
                
                df_updated = pd.concat([df_live, new_row], ignore_index=True)
                safe_write(conn, "TimeTracking", df_updated)
                st.cache_data.clear()
                st.success("✅ Enregistré !")
                st.rerun()

    # --- COLONNE 2 : DÉTAILS DU JOUR ---
    with c2:
        st.subheader(f"📋 Détails du {selected_date.strftime('%d/%m/%Y')}")
        df_copy = df.copy()
        df_copy["date_dt"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        df_j = df_copy[df_copy["date_dt"] == selected_date]

        if not df_j.empty:
            for i, row in df_j.iterrows():
                col_txt, col_edit, col_del = st.columns([0.7, 0.15, 0.15])
                with col_txt:
                    st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")

                if col_edit.button("✏️", key=f"ed_{i}"):
                    st.session_state[f"editing_{i}"] = True
                if col_del.button("🗑️", key=f"de_{i}"):
                    st.session_state[f"confirm_{i}"] = True

                # FORMULAIRE DE MODIFICATION (Correction Nom, Date, Tâche)
                if st.session_state.get(f"editing_{i}"):
                    with st.form(key=f"f_mod_{i}"):
                        st.write("🔧 Correction")
                        # 1. Nom
                        idx_u = LISTE_USERS.index(row['intervenante']) if row['intervenante'] in LISTE_USERS else 0
                        new_u = st.selectbox("Nom", LISTE_USERS, index=idx_u)
                        # 2. Date
                        try: curr_d = datetime.strptime(str(row['date']), "%Y-%m-%d").date()
                        except: curr_d = date.today()
                        new_d = st.date_input("Date", value=curr_d, format="DD/MM/YYYY")
                        # 3. Tâche
                        new_t = st.selectbox("Tâche", LISTE_TACHES, index=LISTE_TACHES.index(row['tache']) if row['tache'] in LISTE_TACHES else 0)
                        # 4. Quantité
                        new_q = st.number_input("Quantité", min_value=1, value=int(row['quantite']))
                        new_e = st.number_input("Écoles", value=int(row['nb_ecoles'])) if new_t == "NETTOYAGES DES DONNEES CREOS" else 0
                        
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("✅ Valider"):
                            # On recharge pour être sûr de ne pas écraser d'autres changements
                            df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                            df_live.at[i, 'intervenante'] = new_u
                            df_live.at[i, 'date'] = str(new_d)
                            df_live.at[i, 'tache'] = new_t
                            df_live.at[i, 'quantite'] = int(new_q)
                            df_live.at[i, 'nb_ecoles'] = int(new_e)
                            safe_write(conn, "TimeTracking", df_live)
                            del st.session_state[f"editing_{i}"]
                            st.cache_data.clear(); st.rerun()
                        if c2.form_submit_button("❌ Annuler"):
                            del st.session_state[f"editing_{i}"]; st.rerun()

                if st.session_state.get(f"confirm_{i}"):
                    st.error("Supprimer ?")
                    y, n = st.columns(2)
                    if y.button("OUI", key=f"y_{i}"):
                        # Rechargement live pour suppression précise
                        df_live = conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
                        df_updated = df_live.drop(i).reset_index(drop=True)
                        safe_write(conn, "TimeTracking", df_updated)
                        st.cache_data.clear(); del st.session_state[f"confirm_{i}"]; st.rerun()
                    if n.button("NON", key=f"n_{i}"):
                        del st.session_state[f"confirm_{i}"]; st.rerun()
        else:
            st.info("Rien pour ce jour.")

    # --- SECTION STATS ---
    st.divider()
    st.header("📊 Statistiques")
    if not df.empty:
        df_stats = df.copy()
        df_stats["date_dt"] = pd.to_datetime(df_stats["date"], errors="coerce")
        df_stats["date_only"] = df_stats["date_dt"].dt.date
        
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            per = st.date_input("Période", [min(df_stats['date_only']), max(df_stats['date_only'])], format="DD/MM/YYYY")
        
        if isinstance(per, (list, tuple)) and len(per) == 2:
            df_f = df_stats[(df_stats['date_only'] >= per[0]) & (df_stats['date_only'] <= per[1])]
            with f2:
                ints = sorted(df_f["intervenante"].dropna().unique())
                f_int = st.multiselect("Intervenantes", ints, default=ints)
            with f3:
                f_tac = st.multiselect("Tâches", LISTE_TACHES)

            if f_int: df_f = df_f[df_f['intervenante'].isin(f_int)]
            if f_tac: df_f = df_f[df_f['tache'].isin(f_tac)]

            if not df_f.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.pie(df_f, names='intervenante', values='quantite', title="Répartition / Intervenante", color='intervenante', color_discrete_map=COULEURS_MAP), use_container_width=True)
                with g2:
                    st.plotly_chart(px.pie(df_f, names='tache', values='quantite', title="Répartition / Tâche"), use_container_width=True)

                df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
                df_synth.columns = ["Action", "Quantité", "Écoles"]
                # Forçage ENTIERS
                df_synth["Quantité"] = df_synth["Quantité"].fillna(0).astype(int)
                df_synth["Écoles"] = df_synth["Écoles"].fillna(0).astype(int)
                
                st.table(df_synth.sort_values("Action"))
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Quantité"].sum()))
