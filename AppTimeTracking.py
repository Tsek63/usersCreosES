import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import io
from safe_gsheets import safe_write

# --- CHARGEMENT AVEC SÉCURITÉ ---
@st.cache_data(ttl=10) # TTL réduit à 10s pour le débuggage
def load_timetracking(_conn):
    try:
        # On force la lecture sans cache pour être sûr
        df = _conn.read(worksheet="TimeTracking", ttl=0).dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])
        return df
    except Exception as e:
        st.error(f"Erreur de lecture Google Sheets : {e}")
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

    # Bouton de secours pour vider le cache manuellement
    if st.button("🔄 Rafraîchir les données (Forcer la lecture)"):
        st.cache_data.clear()
        st.rerun()

    df = load_timetracking(conn)

    # --- LAYOUT ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", LISTE_USERS)
        selected_date = st.date_input("Date Prestation", value=date.today(), format="DD/MM/YYYY")
        
        # Vérification Week-end
        is_weekend = selected_date.weekday() >= 5
        if is_weekend:
            st.error("⚠️ Date de week-end sélectionnée.")
            confirm_wk = st.checkbox("Confirmer l'encodage le week-end")
        else:
            confirm_wk = True

        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_saisie_v4", clear_on_submit=True):
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
            nb_ecoles = 0
            if tache == "NETTOYAGES DES DONNEES CREOS":
                nb_ecoles = st.number_input("Nombre d'écoles", min_value=0, value=1)

            btn_disabled = is_weekend and not confirm_wk
            
            if st.form_submit_button("💾 Enregistrer", use_container_width=True, disabled=btn_disabled):
                new_row = pd.DataFrame([{
                    "date": str(selected_date),
                    "intervenante": user,
                    "tache": tache,
                    "quantite": int(quantite),
                    "nb_ecoles": int(nb_ecoles)
                }])
                df_updated = pd.concat([df, new_row], ignore_index=True)
                safe_write(conn, "TimeTracking", df_updated)
                st.cache_data.clear()
                st.success("✅ Enregistré !")
                st.rerun()

    # --- COLONNE 2 : DÉTAILS DU JOUR ---
    with c2:
        st.subheader(f"📋 Détails du {selected_date.strftime('%d/%m/%Y')}")
        if not df.empty:
            df_view = df.copy()
            df_view["date_dt"] = pd.to_datetime(df_view["date"], errors="coerce").dt.date
            df_j = df_view[df_view["date_dt"] == selected_date]

            if not df_j.empty:
                for i, row in df_j.iterrows():
                    col_t, col_e, col_d = st.columns([0.7, 0.15, 0.15])
                    with col_t:
                        st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")
                    
                    # MODIFIER
                    if col_e.button("✏️", key=f"ed_{i}"):
                        st.session_state[f"edit_tt_{i}"] = True
                    
                    # SUPPRIMER
                    if col_d.button("🗑️", key=f"de_{i}"):
                        st.session_state[f"conf_tt_{i}"] = True

                    # FORMULAIRE DE MODIFICATION
                    if st.session_state.get(f"edit_tt_{i}"):
                        with st.form(key=f"f_mod_{i}"):
                            st.write("🔧 Correction")
                            # Pré-sélection
                            idx_u = LISTE_USERS.index(row['intervenante']) if row['intervenante'] in LISTE_USERS else 0
                            new_u = st.selectbox("Intervenante", LISTE_USERS, index=idx_u)
                            
                            try: curr_d = datetime.strptime(str(row['date']), "%Y-%m-%d").date()
                            except: curr_d = date.today()
                            
                            new_d = st.date_input("Date", value=curr_d, format="DD/MM/YYYY")
                            new_t = st.selectbox("Tâche", LISTE_TACHES, index=LISTE_TACHES.index(row['tache']) if row['tache'] in LISTE_TACHES else 0)
                            new_q = st.number_input("Quantité", min_value=1, value=int(row['quantite']))
                            new_ec = st.number_input("Écoles", value=int(row['nb_ecoles'])) if new_t == "NETTOYAGES DES DONNEES CREOS" else 0
                            
                            c1, c2 = st.columns(2)
                            if c1.form_submit_button("✅ Valider"):
                                df.at[i, 'intervenante'] = new_u
                                df.at[i, 'date'] = str(new_d)
                                df.at[i, 'tache'] = new_t
                                df.at[i, 'quantite'] = new_q
                                df.at[i, 'nb_ecoles'] = new_ec
                                safe_write(conn, "TimeTracking", df)
                                del st.session_state[f"edit_tt_{i}"]
                                st.cache_data.clear(); st.rerun()
                            if c2.form_submit_button("❌ Annuler"):
                                del st.session_state[f"edit_tt_{i}"]; st.rerun()

                    # SUPPRESSION
                    if st.session_state.get(f"conf_tt_{i}"):
                        st.error("Confirmer suppression ?")
                        y, n = st.columns(2)
                        if y.button("OUI", key=f"y_tt_{i}"):
                            df_new = df.drop(i).reset_index(drop=True)
                            safe_write(conn, "TimeTracking", df_new)
                            del st.session_state[f"conf_tt_{i}"]
                            st.cache_data.clear(); st.rerun()
                        if n.button("NON", key=f"n_tt_{i}"):
                            del st.session_state[f"conf_tt_{i}"]; st.rerun()
            else:
                st.info("Aucune prestation ce jour.")
        else:
            st.warning("La base de données est vide ou inaccessible.")

    # --- SECTION STATS ---
    st.divider()
    st.header("📊 Statistiques")
    if not df.empty:
        df_stats = df.copy()
        df_stats["date_only"] = pd.to_datetime(df_stats["date"], errors="coerce").dt.date
        
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            per = st.date_input("Période", [min(df_stats['date_only']), max(df_stats['date_only'])], format="DD/MM/YYYY")
        
        if isinstance(per, (list, tuple)) and len(per) == 2:
            df_f = df_stats[(df_stats['date_only'] >= per[0]) & (df_stats['date_only'] <= per[1])]
            with f2:
                ints = sorted(df_f["intervenante"].dropna().unique())
                f_int = st.multiselect("Intervenantes", ints, default=ints)
            with f3:
                f_tac = st.multiselect("Filtrer Tâches", LISTE_TACHES)

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
                df_synth["Quantité"] = df_synth["Quantité"].astype(int)
                df_synth["Écoles"] = df_synth["Écoles"].astype(int)
                
                st.table(df_synth.sort_values("Action"))
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Quantité"].sum()))
