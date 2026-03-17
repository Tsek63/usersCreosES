def run(conn):
    import streamlit as st
    import pandas as pd
    from datetime import date, datetime
    import plotly.express as px
    import io

    st.subheader("⏱️ Time Tracking")

    # --- CONFIGURATION ET PARAMÈTRES ---
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

    # --- CHARGEMENT DES DONNÉES ---
    try:
        df = conn.read(worksheet="TimeTracking", ttl=0)
    except Exception as e:
        st.error(f"❌ Erreur chargement feuille 'TimeTracking' : {e}")
        st.info("⚠️ Créez une feuille nommée 'TimeTracking' avec les colonnes : date, intervenante, tache, quantite, nb_ecoles")
        return

    if df.empty:
        st.warning("Aucune donnée enregistrée. Commencez à encoder des entrées !")
        return

    # --- LAYOUT EN 2 COLONNES ---
    c1, c2 = st.columns([1, 1.2])

    # --- COLONNE 1 : ENCODAGE ---
    with c1:
        st.subheader("📝 Encodage")
        
        # Sélection de l'intervenante
        intervenantes = sorted(df["intervenante"].dropna().unique().tolist())
        if not intervenantes:
            st.warning("Aucune intervenante trouvée dans les données.")
            return
        user = st.selectbox("Intervenante", intervenantes)
        
        # Sélection de la date
        selected_date = st.date_input("Date", value=date.today())
        
        # Sélection de la tâche
        tache = st.selectbox("Tâche", LISTE_TACHES)

        # Formulaire d'encodage
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
                    st.success("✅ Entrée ajoutée avec succès !")
                    st.rerun()
                except Exception as e_update:
                    st.error(f"Erreur lors de l'enregistrement : {e_update}")

    # --- COLONNE 2 : DÉTAILS DU JOUR ---
    with c2:
        st.subheader(f"📋 Détails du {selected_date.strftime('%d/%m/%Y')}")
        
        # Conversion des dates
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        df_j = df_copy[df_copy["date"] == selected_date].copy()
        
        if not df_j.empty:
            for i, row in df_j.iterrows():
                st.write(f"**{row['intervenante']}** • {row['tache']} ({int(row['quantite'])})")
        else:
            st.info("Aucune donnée pour ce jour.")

    # --- SECTION STATISTIQUES & SYNTHÈSE ---
    st.divider()
    st.header("📊 Statistiques & Synthèse")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date

    if not df_copy.empty:
        # Filtres
        f1, f2, f3 = st.columns([1, 1, 1.5])
        
        with f1:
            per = st.date_input("Sélectionnez la période", 
                               [min(df_copy['date']), max(df_copy['date'])])
        
        # Gérer le cas où per est un tuple ou une date unique
        if isinstance(per, (list, tuple)) and len(per) == 2:
            date_start, date_end = per[0], per[1]
        else:
            date_start = date_end = per
        
        with f2:
            intervenantes_list = sorted(df_copy["intervenante"].dropna().unique())
            f_int = st.multiselect("Filtrer Intervenantes", intervenantes_list, 
                                   default=intervenantes_list)
        
        with f3:
            f_tac = st.multiselect("Filtrer Tâches", LISTE_TACHES)

        # Appliquer les filtres
        df_f = df_copy.copy()
        df_f = df_f[(df_f['date'] >= date_start) & (df_f['date'] <= date_end)]
        
        if f_int: 
            df_f = df_f[df_f['intervenante'].isin(f_int)]
        if f_tac: 
            df_f = df_f[df_f['tache'].isin(f_tac)]

        if not df_f.empty:
            # Graphiques
            g1, g2 = st.columns(2)
            
            with g1:
                try:
                    fig1 = px.pie(df_f, names='intervenante', values='quantite', 
                                color='intervenante', color_discrete_map=COULEURS_MAP,
                                title="Répartition par Intervenante")
                    st.plotly_chart(fig1, use_container_width=True)
                except Exception:
                    st.info("Pas assez de données pour le graphique 'Répartition par Intervenante'")
            
            with g2:
                try:
                    fig2 = px.pie(df_f, names='tache', values='quantite',
                                title="Répartition par Tâche",
                                color_discrete_sequence=px.colors.qualitative.Safe)
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception:
                    st.info("Pas assez de données pour le graphique 'Répartition par Tâche'")

            st.markdown("---")
            
            # Synthèse par tâche
            df_synth = df_f.groupby('tache').agg({'quantite': 'sum', 'nb_ecoles': 'sum'}).reset_index()
            df_synth.columns = ["Action / Tâche", "Total Quantité", "Total Écoles"]
            df_synth = df_synth.sort_values("Total Quantité", ascending=False)
            
            col_synth, col_metric = st.columns([3, 1])
            with col_synth:
                st.subheader("📋 Synthèse par tâche")
                st.dataframe(df_synth, use_container_width=True, hide_index=True)
            
            with col_metric:
                st.metric(
                    label="TOTAL GÉNÉRAL",
                    value=int(df_synth["Total Quantité"].sum()),
                    delta="heures/actions"
                )
            
            st.divider()
            
            # --- EXPORT EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Time Tracking')
                
                # Formats
                titre_format = workbook.add_format({
                    'font_size': 14,
                    'bold': True,
                    'bg_color': '#4169E1',
                    'font_color': 'white',
                    'align': 'left',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                info_format = workbook.add_format({
                    'font_size': 10,
                    'italic': True,
                    'bg_color': '#F0F0F0',
                    'align': 'left',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                header_format = workbook.add_format({
                    'font_size': 11,
                    'bold': True,
                    'bg_color': '#008080',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                cell_format = workbook.add_format({
                    'align': 'left',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                cell_number_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'num_format': '0'
                })
                
                total_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D3D3D3',
                    'align': 'right',
                    'valign': 'vcenter',
                    'border': 1,
                    'num_format': '0'
                })
                
                # En-têtes colonnes
                worksheet.set_column('A:A', 35)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 15)
                
                row = 0
                
                # Titre
                worksheet.merge_cells(f'A{row+1}:C{row+1}')
                worksheet.write(row, 0, '🏫 Creos Extrascolaire - Time Tracking', titre_format)
                row += 1
                
                # Période et date d'export
                date_str = pd.Timestamp.now().strftime("%d/%m/%Y à %H:%M")
                period_text = f"Période : {date_start.strftime('%d/%m/%Y')} → {date_end.strftime('%d/%m/%Y')} | Exporté le {date_str}"
                worksheet.merge_cells(f'A{row+1}:C{row+1}')
                worksheet.write(row, 0, period_text, info_format)
                row += 1
                
                # Espace
                row += 1
                
                # En-tête du tableau
                worksheet.write(row, 0, 'Action / Tâche', header_format)
                worksheet.write(row, 1, 'Total Quantité', header_format)
                worksheet.write(row, 2, 'Total Écoles', header_format)
                row += 1
                
                # Données
                for _, r in df_synth.iterrows():
                    worksheet.write(row, 0, r['Action / Tâche'], cell_format)
                    worksheet.write(row, 1, int(r['Total Quantité']), cell_number_format)
                    worksheet.write(row, 2, int(r['Total Écoles']), cell_number_format)
                    row += 1
                
                # Ligne de total
                worksheet.write(row, 0, 'TOTAL GÉNÉRAL', total_format)
                worksheet.write(row, 1, int(df_synth['Total Quantité'].sum()), total_format)
                worksheet.write(row, 2, int(df_synth['Total Écoles'].sum()), total_format)
            
            output.seek(0)
            
            # Bouton d'export
            col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])
            with col_btn2:
                st.download_button(
                    label="📥 Exporter vers Excel",
                    data=output.getvalue(),
                    file_name=f"time_tracking_{date_start.strftime('%Y%m%d')}_to_{date_end.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
        else:
            st.warning("❌ Aucune donnée pour les filtres sélectionnés.")
    else:
        st.info("La
