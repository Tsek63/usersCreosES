import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import io

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
    LISTE_TACHES = sorted([
        "DEPANNAGE TELEPHONIQUE", "DEPANNAGE MAIL", "SUIVI DEPLOIEMENT TELEPHONIQUE",
        "SUIVI DEPLOIEMENT MAIL", "VISIO DE PRESENTATION", "VISIO DIVERS",
        "MAIL DIVERS", "MODIFICATIONS FICHIER PO", "JOURNEE DE FORMATION",
        "SUIVI ADMIN FORMATION", "MATINEE D'ACCOMPAGNEMENT",
        "SUIVI MATINEE D'ACCOMPAGNEMENT", "ENCODAGE TICKET", "SUIVI FICHIER TICKETS",
        "MODIFICATION - CREATION DOC", "MODIFICATION – CREATION VIDEO",
        "NETTOYAGES DES DONNEES CREOS", "BRIEFING DEV", "TEST EN ACCEPTANCE / PROD"
    ])

    COULEURS_MAP = {
        "Véronique Maigrié": "#FF00FF",
        "Sylvie Nyssen": "#008080"
    }

    # --- CHARGEMENT (CACHÉ) ---
    df = load_timetracking(conn)

    if df.empty:
        st.warning("Aucune donnée enregistrée. Commencez à encoder des entrées !")
        return

    # --- LAYOUT ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")

        intervenantes = sorted(df["intervenante"].dropna().unique().tolist())
        if not intervenantes:
            st.warning("Aucune intervenante trouvée dans les données.")
            return

        user = st.selectbox("Intervenante", intervenantes)
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

                df_updated = pd.concat([df, new_row], ignore_index=True)

                try:
                    conn.update(worksheet="TimeTracking", data=df_updated)
                    st.cache_data.clear()
                    st.success("✅ Entrée ajoutée avec succès !")
                    st.rerun()
                except Exception as e_update:
                    st.error(f"Erreur lors de l'enregistrement : {e_update}")

    # --- COLONNE 2 : DÉTAILS DU JOUR ---
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
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state[f"confirm_{i}"] = True

                    if st.session_state.get(f"confirm_{i}"):
                        st.warning("Supprimer ?")
                        if st.button("OUI ✅", key=f"yes_{i}"):
                            df_updated = df.drop(i)
                            try:
                                conn.update(worksheet="TimeTracking", data=df_updated)
                                st.cache_data.clear()
                                del st.session_state[f"confirm_{i}"]
                                st.rerun()
                            except Exception as e_del:
                                st.error(f"Erreur : {e_del}")

                        if st.button("NON ❌", key=f"no_{i}"):
                            del st.session_state[f"confirm_{i}"]
                            st.rerun()
        else:
            st.info("Aucune donnée pour ce jour.")

    # --- SECTION STATISTIQUES & SYNTHÈSE ---
    st.divider()
    st.header("📊 Statistiques & Synthèse")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date

    if not df_copy.empty:
        f1, f2, f3 = st.columns([1, 1, 1.5])

        with f1:
            per = st.date_input("Sélectionnez la période", [min(df_copy['date']), max(df_copy['date'])])

        if isinstance(per, (list, tuple)) and len(per) == 2:
            date_start, date_end = per[0], per[1]
        else:
            date_start = date_end = per

        with f2:
            intervenantes_list = sorted(df_copy["intervenante"].dropna().unique())
            f_int = st.multiselect("Filtrer Intervenantes", intervenantes_list, default=intervenantes_list)

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
                fig1 = px.pie(
                    df_f,
                    names='intervenante',
                    values='quantite',
                    color='intervenante',
                    color_discrete_map=COULEURS_MAP,
                    title="Répartition par Intervenante"
                )
                st.plotly_chart(fig1, use_container_width=True)

            with g2:
                fig2 = px.pie(
                    df_f,
                    names='tache',
                    values='quantite',
                    title="Répartition par Tâche",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")

            df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
            df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
            df_synth = df_synth.sort_values("Action / Tâche", ascending=True)

            col_synth, col_metric = st.columns([3, 1.2])

            with col_synth:
                st.subheader("📋 Synthèse par tâche")
                df_synth["Total Quantité"] = df_synth["Total Quantité"].fillna(0).astype(int)
                df_synth["Total Écoles"] = df_synth["Total Écoles"].fillna(0).astype(int)
                st.table(df_synth)

            with col_metric:

                def to_excel(df_to_export, df_source, start_date, end_date):
                    output = io.BytesIO()
                    try:
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_to_export.to_excel(writer, index=False, sheet_name='Synthese', startrow=4)

                            workbook = writer.book
                            worksheet = writer.sheets['Synthese']

                            header_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#008080'})

                            worksheet.write('A1', "Creos Extrascolaire - Time tracking", header_fmt)
                            worksheet.write('A2', f"Période : du {start_date} au {end_date}")
                            worksheet.write('A3', f"Date de l'export : {date.today().strftime('%d/%m/%Y')}")

                            for i, col in enumerate(df_to_export.columns):
                                column_len = max(df_to_export[col].astype(str).str.len().max(), len(col)) + 2
                                worksheet.set_column(i, i, column_len)

                            fig_export = px.pie(
                                df_source,
                                names='tache',
                                values='quantite',
                                title="Répartition par Tâche",
                                color_discrete_sequence=px.colors.qualitative.Safe
                            )

                            img_data = fig_export.to_image(format="png", width=600, height=450)
                            img_result = io.BytesIO(img_data)

                            worksheet.insert_image('E5', 'plot.png', {'image_data': img_result})

                        return output.getvalue()
                    except Exception:
                        return None

                excel_data = to_excel(df_synth, df_f, date_start, date_end)

                st.markdown(
                    """<style> div.stDownloadButton > button {
                        background-color: #008080 !important;
                        color: white !important;
                        height: 3em !important;
                    } </style>""",
                    unsafe_allow_html=True
                )

                if excel_data:
                    st.download_button(
                        label="📥 Export vers Excel",
                        data=excel_data,
                        file_name=f"Synthese_Complete_{date.today()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

                st.metric(
                    label="TOTAL GÉNÉRAL",
                    value=int(df_synth["Total Quantité"].sum()),
                    delta="heures/actions"
                )
