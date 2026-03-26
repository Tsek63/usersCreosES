import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import io
import base64
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
    # SECTION STATISTIQUES
    # =========================================================================
    st.divider()
    st.header("📊 Statistiques & Synthèse")

    if not df.empty:
        df_stats = df.copy()
        df_stats["date"] = pd.to_datetime(df_stats["date"], errors="coerce").dt.date
        
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            d_min = df_stats['date'].min()
            d_max = df_stats['date'].max()
            per = st.date_input("Période", [d_min, d_max])

        with f2:
            ints = sorted(df_stats["intervenante"].unique())
            f_int = st.multiselect("Intervenantes", ints, default=ints)

        with f3:
            f_tac = st.multiselect("Filtrer Tâches", LISTE_TACHES)

        # Application des filtres
        mask = (df_stats['date'] >= per[0]) & (df_stats['date'] <= per[1]) if len(per)==2 else True
        df_f = df_stats[mask]
        if f_int: df_f = df_f[df_f['intervenante'].isin(f_int)]
        if f_tac: df_f = df_f[df_f['tache'].isin(f_tac)]

        if not df_f.empty:
            g1, g2 = st.columns(2)
            with g1:
                fig1 = px.pie(df_f, names='intervenante', values='quantite', color='intervenante', 
                             color_discrete_map=COULEURS_MAP, title="Répartition par Intervenante")
                fig1.update_layout(paper_bgcolor="white", plot_bgcolor="white")
                st.plotly_chart(fig1, use_container_width=True)
            with g2:
                # --- AMÉLIORATION DU GRAPHIQUE PAR TÂCHE ---
                fig2 = px.pie(df_f, names='tache', values='quantite', title="Répartition par Tâche",
                             color_discrete_sequence=px.colors.qualitative.Safe)
                
                # Correction des couleurs et de la légende
                fig2.update_traces(textposition='inside', textinfo='percent')
                fig2.update_layout(
                    paper_bgcolor="white", 
                    plot_bgcolor="white",
                    margin=dict(l=20, r=150, t=50, b=20), # Plus de marge à droite (r=150) pour la légende
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")
            df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
            df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
            df_synth["Total Quantité"] = df_synth["Total Quantité"].astype(int)
            df_synth["Total Écoles"] = df_synth["Total Écoles"].astype(int)
            
            col_table, col_metric = st.columns([3, 1])
            with col_table:
                st.table(df_synth)
            
            with col_metric:
                total_actions = int(df_synth["Total Quantité"].sum())
                st.metric("TOTAL GÉNÉRAL", total_actions, "actions")
                
                # --- EXPORT EXCEL AVEC GRAPHES LISIBLES ---
                def to_excel_time():
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_synth.to_excel(writer, index=False, sheet_name='Synthèse', startrow=1)
                        ws = writer.sheets['Synthèse']
                        ws.write('A1', f"Rapport Time Tracking - Du {per[0]} au {per[1]}")
                        
                        # Capture image avec fond blanc forcé et haute résolution
                        img_bytes = fig2.to_image(format="png", width=900, height=600, scale=2)
                        ws.insert_image('E2', 'chart.png', {'image_data': io.BytesIO(img_bytes), 'x_scale': 0.5, 'y_scale': 0.5})
                    return output.getvalue()
                
                st.download_button("📥 Export Excel complet", to_excel_time(), "synthese_time_tracking.xlsx", use_container_width=True)

                # --- IMPRESSION PDF PRO ---
                if st.button("🖨️ IMPRIMER LE RAPPORT", use_container_width=True):
                    # Graphique haute qualité pour le PDF
                    img_base64 = base64.b64encode(fig2.to_image(format="png", width=1000, height=600, scale=2)).decode('utf-8')
                    
                    rows_html = "".join([f"<tr><td>{r['Action / Tâche']}</td><td style='text-align:center;'>{r['Total Quantité']}</td><td style='text-align:center;'>{r['Total Écoles']}</td></tr>" for _, r in df_synth.iterrows()])
                    
                    print_template = f"""
                    <!DOCTYPE html><html><head><meta charset="UTF-8"><style>
                        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #333; background: white; }}
                        h1 {{ color: #008080; border-bottom: 3px solid #008080; padding-bottom: 10px; }}
                        .info {{ margin-bottom: 20px; font-size: 14px; color: #555; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 13px; }}
                        th {{ background: #008080; color: white; padding: 12px; border: 1px solid #ddd; text-align: left; -webkit-print-color-adjust: exact; }}
                        td {{ padding: 10px; border: 1px solid #ddd; }}
                        .total {{ font-size: 20px; font-weight: bold; color: #008080; margin-top: 15px; border-top: 2px solid #eee; padding-top: 10px; }}
                        .chart-section {{ text-align: center; margin-top: 40px; page-break-inside: avoid; }}
                        img {{ width: 100%; max-width: 850px; border: 1px solid #eee; padding: 10px; }}
                    </style></head><body>
                        <h1>Rapport d'activité - Creos Extrascolaire</h1>
                        <div class="info">
                            <strong>Période :</strong> Du {per[0].strftime('%d/%m/%Y')} au {per[1].strftime('%d/%m/%Y')}<br>
                            <strong>Généré le :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}
                        </div>
                        <table><thead><tr><th>Action / Tâche</th><th style='text-align:center;'>Quantité</th><th style='text-align:center;'>Écoles</th></tr></thead>
                        <tbody>{rows_html}</tbody></table>
                        <div class="total">TOTAL GÉNÉRAL : {total_actions} actions</div>
                        <div class="chart-section">
                            <h3 style="color:#008080;">Visualisation de la répartition</h3>
                            <img src="data:image/png;base64,{img_base64}">
                        </div>
                        <script>window.onload = function() {{ window.print(); }}</script>
                    </body></html>"""
                    
                    b64_html = base64.b64encode(print_template.encode('utf-8')).decode('utf-8')
                    js_code = f"""
                        var win = window.open("", "_blank");
                        var html = decodeURIComponent(escape(atob("{b64_html}")));
                        win.document.write(html);
                        win.document.close();
                    """
                    st.components.v1.html(f"<script>{js_code}</script>", height=0)

        else:
            st.info("Aucune donnée pour ces filtres.")
    else:
        st.info("Encodez des données pour voir les statistiques.")
