import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64
from datetime import datetime
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, df_contacts, df_time, data_fwb):
    # --- BOUTON ACTUALISER ---
    titre_col, refresh_col = st.columns([0.8, 0.2])
    with refresh_col:
        if st.button("🔄 Actualiser", use_container_width=True, key="btn_ref_config"):
            st.cache_data.clear()
            st.rerun()

    st.header("⚙️ Configuration")

    # --- PRÉPARATION DES DONNÉES ---
    df_config['Fase école'] = df_config['Fase école'].astype(str).str.strip()
    df_config = df_config.drop_duplicates(subset=['Fase école'], keep='last').reset_index(drop=True)
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # =========================================================================
    # PARTIE HAUTE : FORMULAIRE
    # =========================================================================
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        s1, s2, s3 = st.columns([1, 1, 1.5])
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            active_communes_global = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, 
                                 format_func=lambda x: f"{'✅' if x in active_communes_global else '⚪'} {icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                 key="cfg_c")
        
        if c_sel != "— Sélectionnez —":
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.markdown("**1. Premier encodage groupé**")
                g1, g2 = st.columns(2)
                with g1:
                    m_pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True, key="m_p")
                with g2:
                    m_svc = st.multiselect("Services", svc_list, key="m_s")
                if st.button(f"🚀 Activer tout {c_sel} à 'OUI'", use_container_width=True):
                    fases = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    new_rows = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Oui", "Paiement": m_pay, "Services": "|".join(m_svc) if m_svc else "-"} for f in fases]
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(fases)], pd.DataFrame(new_rows)], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

            df_sch = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
            sch_opts = [f"{r['Ecole']} {'✅' if not df_config[(df_config['Fase école']==str(r['Fase école'])) & (df_config['Extrascolaire']=='Oui')].empty else ('❌' if not df_config[(df_config['Fase école']==str(r['Fase école'])) & (df_config['Extrascolaire']=='Non')].empty else '⭕')} — Fase {r['Fase école']}" for _, r in df_sch.iterrows()]
            e_label = st.selectbox("3. École individuelle", sch_opts, key="cfg_e")
            e_fase = e_label.split(" — Fase ")[-1]
            if e_fase:
                curr = df_config[df_config['Fase école'] == e_fase]
                idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
                with st.form("form_cfg_final"):
                    f1, f2 = st.columns(2)
                    v_ex = f1.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                    v_pa = f2.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=0 if (curr.empty or curr.iloc[0]['Paiement'] != "Post-paiement") else 1, horizontal=True)
                    v_sv = st.multiselect("Services", svc_list, default=str(curr.iloc[0]['Services']).split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else [])
                    if st.form_submit_button("💾 ENREGISTRER L'ÉCOLE", use_container_width=True):
                        new = pd.DataFrame([{"Fase école": e_fase, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != e_fase], new], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

    with col_r:
        df_active_total = df_config[df_config['Extrascolaire'] == 'Oui']
        df_refus_total = df_config[df_config['Extrascolaire'] == 'Non']
        st.markdown(f"""
            <div style="background-color:#008080; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
                <div style="font-size:14px; font-weight:bold;">Écoles qui Utilisent l'Extrascolaire</div>
                <div style="font-size:42px; font-weight:bold;">{len(df_active_total)}</div>
            </div>
            <div style="background-color:#FF43D0; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
                <div style="font-size:14px; font-weight:bold;">Écoles qui n'utilisent pas l'Extrascolaire</div>
                <div style="font-size:42px; font-weight:bold;">{len(df_refus_total)}</div>
            </div>
        """, unsafe_allow_html=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_config.to_excel(writer, sheet_name='Configurations', index=False)
            df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
            df_time.to_excel(writer, sheet_name='TimeTracking', index=False)
        st.download_button(label="🛡️ Sécurité : export Excel complet", data=buffer.getvalue(), file_name=f"SAVE_TOTAL_{datetime.now().strftime('%d_%m_%Y')}.xlsx", use_container_width=True)

    # =========================================================================
    # PARTIE BASSE : SITUATION ACTUELLE (70/30)
    # =========================================================================
    st.divider()
    st.subheader("📊 Situation actuelle")

    view_mode = st.radio("Filtre global :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="view_mode")
    is_refus_view = "Refus" in view_mode
    
    # --- FILTRES (70/30) ---
    col_list, col_stats = st.columns([0.7, 0.3])

    with col_list:
        f1, f2, f3 = st.columns(3)
        with f1: fl_p = st.multiselect("Filtrer par Province", sorted(df_config['Province'].unique()), key="f_p")
        with f2: fl_m = st.selectbox("Mode de paiement", ["TOUS", "Prépaiement", "Post-paiement"], disabled=is_refus_view)
        with f3: fl_s = st.selectbox("Services", ["TOUS"] + svc_list, disabled=is_refus_view)

        # Logique de filtrage et TRI
        df_target = df_config[df_config['Extrascolaire'] == ('Non' if is_refus_view else 'Oui')].copy()
        if fl_p: df_target = df_target[df_target['Province'].isin(fl_p)]
        if not is_refus_view:
            if fl_m != "TOUS": df_target = df_target[df_target['Paiement'] == fl_m]
            if fl_s != "TOUS": df_target = df_target[df_target['Services'].str.contains(fl_s, na=False)]
        
        # Tri par Province puis Commune
        df_target = df_target.sort_values(by=['Province', 'Commune'])

        if not df_target.empty:
            df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates()
            df_display = df_target.merge(df_names, on='Fase école', how='left').fillna("-")
            
            h1, h2, h3, h4 = st.columns([1.5, 1.5, 2, 0.5])
            h1.write("**Commune**"); h2.write("**École**"); h3.write("**Détails**"); h4.write("")
            
            for i, (_, row) in enumerate(df_display.iterrows()):
                r1, r2, r3, r4 = st.columns([1.5, 1.5, 2, 0.5])
                r1.write(row['Commune'])
                r2.write(f"{row['Ecole']} ({row['Fase école']})")
                if not is_refus_view:
                    p_c = "#FF43D0" if row['Paiement'] == "Prépaiement" else "#008080"
                    details_html = f'<b style="color:{p_c};">{row["Paiement"]}</b><br>'
                    svs = str(row['Services']).split('|')
                    colors_map = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                    for s in svs:
                        if s.strip() and s.strip() != "-":
                            details_html += f'<span style="background:{colors_map.get(s.strip(),"#999")}; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:3px; display:inline-block; margin-top:2px;">{s.strip()}</span>'
                    r3.markdown(details_html, unsafe_allow_html=True)
                else: r3.write("Refus enregistré")
                
                if r4.button("🗑️", key=f"del_low_{i}"):
                    safe_write(conn, "EcolesConfig", df_config[df_config['Fase école'] != str(row['Fase école'])]); st.cache_data.clear(); st.rerun()
        else:
            st.info("Aucune école ne correspond aux filtres.")

    with col_stats:
        # --- BLOC CHIFFRES (BLEU CANARD) ---
        st.markdown(f"""
            <div style="background-color:#008080; padding:20px; border-radius:12px; color:white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size:12px; font-weight:bold; opacity:0.8; text-transform:uppercase;">Résultats filtrés</div>
                <hr style="margin:10px 0; opacity:0.3;">
                <div style="font-size:26px; font-weight:bold;">{df_target['Commune'].nunique()} <small style="font-size:14px; font-weight:normal;">Communes</small></div>
                <div style="font-size:26px; font-weight:bold;">{len(df_target)} <small style="font-size:14px; font-weight:normal;">Écoles</small></div>
            </div>
        """, unsafe_allow_html=True)

        if not is_refus_view and not df_target.empty:
            # Stats Paiement (BLEU CANARD)
            p_counts = df_target['Paiement'].value_counts()
            st.markdown(f"""
                <div style="margin-top:10px; padding:15px; background:#008080; border-radius:12px; color:white;">
                    <div style="display:flex; justify-content:space-between;"><span>Prépaiement:</span><b>{p_counts.get('Prépaiement', 0)}</b></div>
                    <div style="display:flex; justify-content:space-between;"><span>Post-paiement:</span><b>{p_counts.get('Post-paiement', 0)}</b></div>
                </div>
            """, unsafe_allow_html=True)

            # Graphique Paiement (Fuchsia / Bleu Canard)
            fig_p = px.pie(df_target, names='Paiement', hole=0.4, height=220, color='Paiement',
                           color_discrete_map={'Prépaiement':'#FF43D0', 'Post-paiement':'#008080'})
            fig_p.update_layout(margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_p, use_container_width=True)

            # Graphique Services avec Nombres
            all_s = []
            for s in df_target['Services'].str.split('|'):
                if isinstance(s, list): all_s.extend([x.strip() for x in s if x.strip() and x != "-"])
            if all_s:
                df_s_plot = pd.DataFrame(all_s, columns=['Service']).value_counts().reset_index()
                df_s_plot.columns = ['Service', 'Nombre']
                fig_s = px.bar(df_s_plot, x='Nombre', y='Service', orientation='h', height=300, text='Nombre',
                               color='Service', color_discrete_map=colors_map)
                fig_s.update_traces(textposition='outside', textfont_size=12)
                fig_s.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=False, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True)

        # --- BOUTONS EXPORT ET IMPRESSION ---
        st.write("---")
        if not df_target.empty:
            # 1. Export Excel Right Side
            buf_stats = io.BytesIO()
            with pd.ExcelWriter(buf_stats, engine='xlsxwriter') as wr:
                df_target.to_excel(wr, sheet_name='Détails', index=False)
                # On ajoute une feuille de synthèse
                summary = pd.DataFrame({
                    "Indicateur": ["Nombre Communes", "Nombre Écoles", "Prépaiements", "Post-paiements"],
                    "Valeur": [df_target['Commune'].nunique(), len(df_target), p_counts.get('Prépaiement',0) if not is_refus_view else 0, p_counts.get('Post-paiement',0) if not is_refus_view else 0]
                })
                summary.to_excel(wr, sheet_name='Synthese', index=False)
            
            st.download_button("📥 Export Excel (Filtres)", buf_stats.getvalue(), "synthese_situation.xlsx", use_container_width=True)

            # 2. Bouton Impression (Génération HTML)
            print_html = f"""
            <html><head><style>
                body {{ font-family: sans-serif; padding: 20px; }}
                h1 {{ color: #008080; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }}
                th {{ background-color: #008080; color: white; }}
                .prov {{ background-color: #f2f2f2; font-weight: bold; }}
            </style></head><body>
                <h1>Rapport Creos : {view_mode}</h1>
                <p>Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p>Filtres Province(s): {', '.join(fl_p) if fl_p else 'Toutes'}</p>
                <table>
                    <thead><tr><th>Province</th><th>Commune</th><th>École</th><th>Paiement</th><th>Services</th></tr></thead>
                    <tbody>
            """
            for _, r in df_display.iterrows():
                print_html += f"<tr><td>{r['Province']}</td><td>{r['Commune']}</td><td>{r['Ecole']}</td><td>{r.get('Paiement','-')}</td><td>{r.get('Services','-')}</td></tr>"
            print_html += "</tbody></table></body></html>"
            
            b64 = base64.b64encode(print_html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration:none;"><div style="text-align:center; padding:10px; background:#1e293b; color:white; border-radius:5px; font-weight:bold;">🖨️ IMPRIMER LE RAPPORT</div></a>'
            st.markdown(href, unsafe_allow_html=True)
