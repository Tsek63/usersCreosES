import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import io
from safe_gsheets import safe_write

# --- CACHE POUR LA FEUILLE TIMETRACKING ---
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
    # AJOUT DE "CALL TONY" ICI
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

    JOURS_NOM = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    LISTE_USERS = ["Véronique Maigrié", "Sylvie Nyssen"]
    COULEURS_MAP = {"Véronique Maigrié": "#FF00FF", "Sylvie Nyssen": "#008080"}

    df = load_timetracking(conn)

    # --- LAYOUT ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")
        user = st.selectbox("Intervenante", LISTE_USERS)
        selected_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        
        num_jour = selected_date.weekday()
        nom_du_jour = JOURS_NOM[num_jour]
        is_weekend = num_jour >= 5

        if is_weekend:
            st.error(f"⚠️ {nom_du_jour} est un jour de week-end.")
            confirm_wk = st.checkbox("Je confirme vouloir encoder une prestation un week-end")
        else:
            st.info(f"📅 Jour : {nom_du_jour}")
            confirm_wk = True

        tache = st.selectbox("Tâche", LISTE_TACHES)

        with st.form("form_saisie", clear_on_submit=True):
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
            nb_ecoles = 0
            if tache == "NETTOYAGES DES DONNEES CREOS":
                nb_ecoles = st.number_input("Nombre d'écoles", min_value=1, step=1, value=1)

            submit_disabled = is_weekend and not confirm_wk
            
            if st.form_submit_button("💾 Enregistrer", use_container_width=True, disabled=submit_disabled):
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
                    style = "color: #FF43D0; font-weight: bold;" if is_weekend else ""
                    st.markdown(f"<span style='{style}'>{row['intervenante']} • {row['tache']} ({int(row['quantite'])})</span>", unsafe_allow_html=True)

                if col_edit.button("✏️", key=f"edit_{i}"):
                    st.session_state[f"editing_{i}"] = True

                if col_del.button("🗑️", key=f"del_{i}"):
                    st.session_state[f"confirm_{i}"] = True

                # --- FORMULAIRE DE MODIFICATION COMPLET ---
                if st.session_state.get(f"editing_{i}"):
                    with st.form(key=f"form_mod_{i}"):
                        st.write("🔧 Correction")
                        # 1. Modifier l'intervenante
                        idx_user = LISTE_USERS.index(row['intervenante']) if row['intervenante'] in LISTE_USERS else 0
                        new_u = st.selectbox("Intervenante", LISTE_USERS, index=idx_user)
                        
                        # 2. Modifier la date
                        current_date_val = datetime.strptime(str(row['date']), "%Y-%m-%d").date()
                        new_d = st.date_input("Date", value=current_date_val, format="DD/MM/YYYY")
                        
                        # 3. Modifier la tâche
                        new_t = st.selectbox("Tâche", LISTE_TACHES, index=LISTE_TACHES.index(row['tache']) if row['tache'] in LISTE_TACHES else 0)
                        
                        # 4. Modifier quantité et écoles
                        new_q = st.number_input("Quantité", min_value=1, value=int(row['quantite']))
                        new_e = st.number_input("Nombre écoles", value=int(row['nb_ecoles'])) if new_t == "NETTOYAGES DES DONNEES CREOS" else 0
                        
                        sv, cn = st.columns(2)
                        if sv.form_submit_button("✅ Valider"):
                            df.at[i, 'intervenante'] = new_u
                            df.at[i, 'date'] = str(new_d)
                            df.at[i, 'tache'] = new_t
                            df.at[i, 'quantite'] = new_q
                            df.at[i, 'nb_ecoles'] = new_e
                            safe_write(conn, "TimeTracking", df)
                            del st.session_state[f"editing_{i}"]
                            st.cache_data.clear(); st.rerun()
                        if cn.form_submit_button("❌ Annuler"):
                            del st.session_state[f"editing_{i}"]; st.rerun()

                if st.session_state.get(f"confirm_{i}"):
                    st.warning("Supprimer ?")
                    y, n = st.columns(2)
                    if y.button("OUI ✅", key=f"y_{i}"):
                        df_updated = df.drop(i).reset_index(drop=True)
                        safe_write(conn, "TimeTracking", df_updated)
                        st.cache_data.clear(); del st.session_state[f"confirm_{i}"]; st.rerun()
                    if n.button("NON ❌", key=f"n_{i}"):
                        del st.session_state[f"confirm_{i}"]; st.rerun()
        else:
            st.info("Aucune donnée pour ce jour.")

    # --- SECTION STATS ---
    st.divider()
    st.header("📊 Statistiques & Synthèse")
    df_stats = df.copy()
    df_stats["date_dt"] = pd.to_datetime(df_stats["date"], errors="coerce")
    df_stats["date_only"] = df_stats["date_dt"].dt.date

    if not df_stats.empty:
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            per = st.date_input("Période", [min(df_stats['date_only']), max(df_stats['date_only'])], format="DD/MM/YYYY")
        
        if isinstance(per, (list, tuple)) and len(per) == 2:
            d_start, d_end = per[0], per[1]
            df_f = df_stats[(df_stats['date_only'] >= d_start) & (df_stats['date_only'] <= d_end)]
            
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
                    fig1 = px.pie(df_f, names='intervenante', values='quantite', title="Par Intervenante", color='intervenante', color_discrete_map=COULEURS_MAP)
                    st.plotly_chart(fig1, use_container_width=True)
                with g2:
                    fig2 = px.pie(df_f, names='tache', values='quantite', title="Par Tâche")
                    st.plotly_chart(fig2, use_container_width=True)

                st.markdown("---")
                df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
                df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
                df_synth["Total Quantité"] = df_synth["Total Quantité"].fillna(0).astype(int)
                df_synth["Total Écoles"] = df_synth["Total Écoles"].fillna(0).astype(int)
                
                st.table(df_synth.sort_values("Action / Tâche"))
                st.metric("TOTAL GÉNÉRAL", int(df_synth["Total Quantité"].sum()))
