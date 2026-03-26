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
    colors_map = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}

    # =========================================================================
    # PARTIE HAUTE : FORMULAIRE
    # =========================================================================
    col_l, col_r = st.columns([1.8, 1.2])
    with col_l:
        s1, s2, s3 = st.columns([1, 1, 1.5])
        with s1: p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            active_communes_global = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, 
                                 format_func=lambda x: f"{'✅' if x in active_communes_global else '⚪'} {icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                 key="cfg_c")
        if c_sel != "— Sélectionnez —":
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.markdown("**1. Premier encodage groupé**")
                g_e1, g_e2 = st.columns(2)
                with g_e1: m_pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True, key="m_p")
                with g_e2: m_svc = st.multiselect("Services", svc_list, key="m_s")
                if st.button(f"🚀 Activer tout {c_sel} à 'OUI'", use_container_width=True):
                    f_list = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    new_rows = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Oui", "Paiement": m_pay, "Services": "|".join(m_svc) if m_svc else "-"} for f in f_list]
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(f_list)], pd.DataFrame(new_rows)], ignore_index=True)
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
        st.markdown(f"""
            <div style="background-color:#008080; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
                <div style="font-size:14px; font-weight:bold;">Écoles qui Utilisent l'Extrascolaire</div>
                <div style="font-size:42px; font-weight:bold;">{len(df_config[df_config['Extrascolaire'] == 'Oui'])}</div>
            </div>
            <div style="background-color:#FF43D0; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
                <div style="font-size:14px; font-weight:bold;">Écoles qui n'utilisent pas l'Extrascolaire</div>
                <div style="font-size:42px; font-weight:bold;">{len(df_config[df_config['Extrascolaire'] == 'Non'])}</div>
            </div>
        """, unsafe_allow_html=True)
        buf_all = io.BytesIO()
        with pd.ExcelWriter(buf_all, engine='xlsxwriter') as writer:
            df_config.to_excel(writer, sheet_name='EcolesConfig', index=False)
            df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
            df_time.to_excel(writer, sheet_name='TimeTracking', index=False)
        st.download_button("🛡️ Sécurité des données : export Excel complet", buf_all.getvalue(), f"BACKUP_TOTAL.xlsx", use_container_width=True)

    # =========================================================================
    # PARTIE BASSE : SITUATION ACTUELLE (70/30)
    # =========================================================================
    st.divider()
    st.subheader("📊 Situation actuelle")

    view_mode = st.radio("Choix de la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="v_mode")
    is_refus = "Refus" in view_mode
    
    col_list, col_stats = st.columns([0.7, 0.3])

    with col_list:
        f1, f2, f3 = st.columns(3)
        with f1: fl_p = st.multiselect("Province", sorted(df_config['Province'].unique()), key="f_p_low")
        with f2: fl_m = st.selectbox("Paiement", ["TOUS", "Prépaiement", "Post-paiement"], disabled=is_refus)
        with f3: fl_s = st.selectbox("Services", ["TOUS"] + svc_list, disabled=is_refus)

        df_target = df_config[df_config['Extrascolaire'] == ('Non' if is_refus else 'Oui')].copy()
        if fl_p: df_target = df_target[df_target['Province'].isin(fl_p)]
        if not is_refus:
            if fl_m != "TOUS": df_target = df_target[df_target['Paiement'] == fl_m]
            if fl_s != "TOUS": df_target = df_target[df_target['Services'].str.contains(fl_s, na=False)]
        
        df_target = df_target.sort_values(['Province', 'Commune'])

        if not df_target.empty:
            df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates()
            df_disp = df_target.merge(df_names, on='Fase école', how='left').fillna("-")
            h1, h2, h3, h4 = st.columns([1.5, 1.5, 2, 0.5])
            h1.write("**Commune**"); h2.write("**École**"); h3.write("**Détails**")
            for i, (_, r) in enumerate(df_disp.iterrows()):
                r1, r2, r3, r4 = st.columns([1.5, 1.5, 2, 0.5])
                r1.write(r['Commune']); r2.write(f"{r['Ecole']} ({r['Fase école']})")
                if not is_refus:
                    p_c = "#FF43D0" if r['Paiement'] == "Prépaiement" else "#008080"
                    html = f'<b style="color:{p_c};">{r["Paiement"]}</b><br>'
                    for s in str(r['Services']).split('|'):
                        if s.strip() and s.strip() != "-":
                            html += f'<span style="background:{colors_map.get(s.strip(),"#999")}; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:3px; display:inline-block; margin-top:2px;">{s.strip()}</span>'
                    r3.markdown(html, unsafe_allow_html=True)
                else: r3.write("Refus enregistré")
                if r4.button("🗑️", key=f"dlow_{i}"):
                    safe_write(conn, "EcolesConfig", df_config[df_config['Fase école'] != str(r['Fase école'])]); st.cache_data.clear(); st.rerun()
        else: st.info("Aucun résultat.")

    with col_stats:
        # BLOC CHIFFRES BLEU CANARD
        n_com = df_target['Commune'].nunique()
        n_eco = len(df_target)
        st.markdown(f"""<div style="background-color:#008080; padding:20px; border-radius:12px; color:white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="font-size:12px; font-weight:bold; opacity:0.8; text-transform:uppercase;">Résultats filtrés</div><hr style="margin:10px 0; opacity:0.3;">
<div style="font-size:26px; font-weight:bold;">{n_com} <small style="font-size:22px; font-weight:normal;">Communes</small></div>
<div style="font-size:26px; font-weight:bold;">{n_eco} <small style="font-size:22px; font-weight:normal;">Écoles</small></div></div>""", unsafe_allow_html=True)

        img_p_base64, img_s_base64 = None, None
        p_counts = df_target['Paiement'].value_counts()

        if not is_refus and not df_target.empty:
            # 1. PIE CHART
            fig_p = px.pie(df_target, names='Paiement', hole=0.4, height=220, color='Paiement', color_discrete_map={'Prépaiement':'#FF43D0', 'Post-paiement':'#008080'})
            fig_p.update_layout(margin=dict(l=0,r=0,t=30,b=0), legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_p, use_container_width=True)
            try: 
                img_p_bytes = fig_p.to_image(format="png", width=400, height=300)
                img_p_base64 = base64.b64encode(img_p_bytes).decode()
            except: img_p_bytes = None

            # 2. BAR CHART
            all_s = []
            for s in df_target['Services'].str.split('|'):
                if isinstance(s, list): all_s.extend([x.strip() for x in s if x.strip() and x != "-"])
            if all_s:
                df_s = pd.DataFrame(all_s, columns=['S']).value_counts().reset_index()
                df_s.columns = ['S', 'N']
                fig_s = px.bar(df_s, x='N', y='S', orientation='h', height=300, text='N', color='S', color_discrete_map=colors_map)
                fig_s.update_traces(textposition='outside'); fig_s.update_layout(margin=dict(l=0,r=0,t=30,b=0), showlegend=False, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True)
                try: 
                    img_s_bytes = fig_s.to_image(format="png", width=400, height=300)
                    img_s_base64 = base64.b64encode(img_s_bytes).decode()
                except: img_s_bytes = None

        # --- BOUTONS RAPPORT ---
        st.write("---")
        if not df_target.empty:
            # EXCEL
            buf_rep = io.BytesIO()
            with pd.ExcelWriter(buf_rep, engine='xlsxwriter') as wr:
                df_disp.to_excel(wr, sheet_name='Details', index=False)
                if not is_refus:
                    ws = wr.sheets['Details']
                    try:
                        if img_p_bytes: ws.insert_image('G2', 'pie.png', {'image_data': io.BytesIO(img_p_bytes)})
                        if img_s_bytes: ws.insert_image('G18', 'bar.png', {'image_data': io.BytesIO(img_s_bytes)})
                    except: pass
            st.download_button("📥 Export Excel complet (avec graphiques)", buf_rep.getvalue(), "rapport_creos.xlsx", use_container_width=True)

            # IMPRESSION (Correction du bouton)
            print_html = f"""
            <html><head><style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .h {{ background: #008080; color: white; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; }}
                .f {{ background: #f8fafc; border-left: 5px solid #008080; padding: 10px; margin: 15px 0; display: flex; gap: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 11px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #008080; color: white; }}
            </style></head><body>
                <div class="h"><div><b>Rapport Creos : {view_mode}</b></div><div>{datetime.now().strftime('%d/%m/%Y')}</div></div>
                <div class="f"><div><b>{n_com}</b> Communes</div><div><b>{n_eco}</b> Écoles</div></div>
                <table><thead><tr><th>Province</th><th>Commune</th><th>École</th><th>Paiement</th><th>Services</th></tr></thead><tbody>
            """
            for _, r in df_disp.iterrows():
                print_html += f"<tr><td>{r['Province']}</td><td>{r['Commune']}</td><td>{r['Ecole']}</td><td>{r.get('Paiement','-')}</td><td>{r.get('Services','-')}</td></tr>"
            print_html += "</tbody></table></body></html>"
            
            b64_p = base64.b64encode(print_html.encode('utf-8')).decode('utf-8')
            # JS pour ouvrir une nouvelle fenêtre et imprimer
            js_print = f"""<script>
            function printReport() {{
                var win = window.open();
                win.document.write(decodeURIComponent(escape(atob('{b64_p}'))));
                win.document.close();
                win.print();
            }}
            </script>
            <button onclick="printReport()" style="width:100%; padding:12px; background:#008080; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">🖨️ IMPRIMER LE RAPPORT (BLEU CANARD)</button>
            """
            components.html(js_print, height=60)
