import io
from datetime import datetime

# Ajouter à la fin du bloc "if not df_f.empty:" (après ligne 172)

            st.divider()
            
            # --- EXPORT EXCEL ---
            # Générer le fichier Excel
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
                
                # En-têtes
                worksheet.set_column('A:A', 35)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 15)
                
                row = 0
                
                # Titre
                worksheet.merge_cells(f'A{row+1}:C{row+1}')
                worksheet.write(row, 0, '🏫 Creos Extrascolaire - Time Tracking', titre_format)
                row += 1
                
                # Période
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
                total_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D3D3D3',
                    'align': 'right',
                    'valign': 'vcenter',
                    'border': 1,
                    'num_format': '0'
                })
                
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
