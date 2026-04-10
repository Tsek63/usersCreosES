import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64
import streamlit.components.v1 as components
from datetime import datetime
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, df_contacts, df_time, data_fwb):
    # --- BOUTON ACTUALISER ---
    titre_col, refresh_col = st.columns([0.8, 0.2])
    with refresh_col:
        if st.button("🔄 Actualiser", use_container_width=True, key="btn_ref_cfg"):
            st.cache_data.clear()
            st.rerun()

    st.header("⚙️ Configuration")
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
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, format_func=lambda x: f"{'✅' if x in active_communes_global else '⚪'} {icon_po(x)} {x}" if x != "— Sélectionnez —" else x, key="cfg_c")
        if c_sel != "— Sélectionnez —":
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                g1, g2 = st.columns(2)
                with g1: m_pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True, key="m_p")
                with g2: m_svc = st.multiselect("Services", svc_list, key="m_s")
                if st.button(f"🚀 Activer tout {c_sel} à 'OUI'", use_container_width=True):
                    f_list = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    new = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Oui", "Paiement": m_pay, "Services": "|".join(m_svc) if m_svc else "-"} for f in f_list]
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(f_list)], pd.DataFrame(new)], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

    with col_r:
        st.markdown(f"""<div style="background:#008080; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
<div style="font-size:14px; font-weight:bold;">Écoles qui Utilisent l'Extrascolaire</div><div style="font-size:42px; font-weight:bold;">{len(df_config[df_config['Extrascolaire'] == 'Oui'])}</div></div>
<div style="background:#FF43D0; padding:15px; border-radius:10px; color:white; text-align:center; margin-bottom:10px;">
<div style="font-size:14px; font-weight:bold;">Écoles avec 'abandon'</div><div style="font-size:42px; font-weight:bold;">{len(df_config[df_config['Extrascolaire'] == 'Non'])}</div></div>""", unsafe_allow_html=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df_config.to_excel(writer, sheet_name='EcolesConfig', index=False)
            df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
            df_time.to_excel(writer, sheet_name='TimeTracking', index=False)
        st.download_button("🛡️ Sécurité : export Excel complet", buf.getvalue(), "BACKUP.xlsx", use_container_width=True)

    # =========================================================================
    # PARTIE BASSE : SITUATION ACTUELLE (70/30)
    # =========================================================================
    st.divider()
    st.subheader("📊 Situation actuelle")
    view_mode = st.radio("Choix de la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec 'abandon'"], horizontal=True, key="v_mode")
    is_refus = "abandon" in view_mode
    
    col_list, col_stats = st.columns([0.7, 0.3])

    with col_list:
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1: fl_p = st.multiselect("Province", sorted(df_config['Province'].unique()), key="f_p_low")
        with f2: fl_m = st.selectbox("Mode de paiement", ["TOUS", "Prépaiement", "Post-paiement"], disabled=is_refus)
        with f3: 
            fl_s = st.multiselect("Services (Correspondance exacte)", svc_list, disabled=is_refus, help="Affiche uniquement les écoles possédant EXACTEMENT cette combinaison de services.")

        df_target = df_config[df_config['Extrascolaire'] == ('Non' if is_refus else 'Oui')].copy()
        
        # 1. Filtre Province
        if fl_p: df_target = df_target[df_target['Province'].isin(fl_p)]
        
        if not is_refus:
            # 2. Filtre Paiement
            if fl_m != "TOUS": df_target = df_target[df_target['Paiement'] == fl_m]
            
            # 3. LOGIQUE DE FILTRAGE PAR CORRESPONDANCE EXACTE
            if fl_s:
                def check_exact_match(val):
                    if not val or val == "-": return False
                    school_services = set([x.strip() for x in str(val).split('|') if x.strip()])
                    selected_services = set(fl_s)
                    return school_services == selected_services
                
                df_target = df_target[df_target['Services'].apply(check_exact_match)]
        
        # --- TRI ---
        df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates()
        df_disp = df_target.merge(df_names, on='Fase école', how='left').fillna("-").sort_values(['Province', 'Commune', 'Ecole'])
        
        if not df_disp.empty:
            h1, h2, h3, h4 = st.columns([1.5, 1.5, 2, 0.5])
            h1.write("**Commune**"); h2.write("**École**"); h3.write("**Détails**")
            for i, (_, r) in enumerate(df_disp.iterrows()):
                r1, r2, r3, r4 = st.columns([1.5, 1.5, 2, 0.5])
                r1.write(r['Commune']); r2.write(f"{r['Ecole']} ({r['Fase école']})")
                if not is_refus:
                    p_c = "#FF43D0" if r['Paiement'] == "Prépaiement" else "#008080"
                    html = f'<b style="color:{p_c};">{r["Paiement"]}</b><br>'
                    for s in str(r['Services']).split('|'):
                        if s.strip() and s.strip() != "-": html += f'<span style="background:{colors_map.get(s.strip(),"#999")}; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:3px; display:inline-block; margin-top:2px;">{s.strip()}</span>'
                    r3.markdown(html, unsafe_allow_html=True)
                else: r3.write("Abandon enregistré")
                if r4.button("🗑️", key=f"dlow_{i}"):
                    safe_write(conn, "EcolesConfig", df_config[df_config['Fase école'] != str(r['Fase école'])]); st.cache_data.clear(); st.rerun()
        else: st.info("Aucun résultat pour cette combinaison exacte de filtres.")

    with col_stats:
        n_com = df_disp['Commune'].nunique(); n_eco = len(df_disp); p_c = df_disp['Paiement'].value_counts()
        st.markdown(f'<div style="background:#008080; padding:20px; border-radius:12px; color:white;"><div style="font-size:12px; font-weight:bold; text-transform:uppercase;">Résultats filtrés</div><hr style="margin:10px 0; opacity:0.3;"><div style="display:flex; justify-content:space-between;"><b style="font-size:22px;">{n_com}</b><span style="font-size:22px;">Communes</span></div><div style="display:flex; justify-content:space-between;"><b style="font-size:22px;">{n_eco}</b><span style="font-size:22px;">Écoles</span></div>{f"<hr style='margin:10px 0; opacity:0.3;'><div style='display:flex; justify-content:space-between; font-size:14px;'><span>Prépaiement:</span><b>{p_c.get('Prépaiement', 0)}</b></div><div style='display:flex; justify-content:space-between; font-size:14px;'><span>Post-paiement:</span><b>{p_c.get('Post-paiement', 0)}</b></div>" if not is_refus else ""}</div>', unsafe_allow_html=True)
        
        img_p, img_s = None, None
        if not is_refus and not df_disp.empty:
            fig_p = px.pie(df_disp, names='Paiement', hole=0.4, height=220, color='Paiement', color_discrete_map={'Prépaiement':'#FF43D0', 'Post-paiement':'#008080'})
            fig_p.update_layout(margin=dict(l=0,r=0,t=30,b=0), showlegend=True, legend=dict(orientation="h", y=-0.2)); st.plotly_chart(fig_p, use_container_width=True)
            try: img_p = fig_p.to_image(format="png", width=400, height=300)
            except: pass

            all_s = []
            for s in df_disp['Services'].str.split('|'):
                if isinstance(s, list): all_s.extend([x.strip() for x in s if x.strip() and x != "-"])
            if all_s:
                df_s = pd.DataFrame(all_s, columns=['S']).value_counts().reset_index(); df_s.columns = ['S', 'N']
                fig_s = px.bar(df_s, x='N', y='S', orientation='h', height=300, text='N', color='S', color_discrete_map=colors_map)
                fig_s.update_traces(textposition='outside'); fig_s.update_layout(margin=dict(l=0,r=0,t=30,b=0), showlegend=True, legend=dict(orientation="h", y=-0.5), xaxis_title=None, yaxis_title=None); st.plotly_chart(fig_s, use_container_width=True)
                try: img_s = fig_s.to_image(format="png", width=400, height=300)
                except: pass

        if not df_disp.empty:
            st.write("---")
            buf_rep = io.BytesIO()
            with pd.ExcelWriter(buf_rep, engine='xlsxwriter') as wr:
                df_disp.to_excel(wr, sheet_name='Details', index=False)
                if img_p: wr.sheets['Details'].insert_image('G2', 'p.png', {'image_data': io.BytesIO(img_p)})
            st.download_button("📥 Export Excel", buf_rep.getvalue(), "rapport.xlsx", use_container_width=True)
            
            # --- RAPPORT IMPRESSION ---
            print_html = f"<html><head><meta charset='UTF-8'><style>body{{font-family:Arial;padding:30px;}}.h{{background:#008080;color:white;padding:20px;border-radius:8px;display:flex;justify-content:space-between;}}.prov-h{{background:#1e293b;color:white;padding:8px;margin-top:20px;}}.comm-h{{background:#f1f5f9;color:#008080;padding:5px;font-weight:bold;border-left:4px solid #008080;}}table{{width:100%;border-collapse:collapse;margin-bottom:10px;font-size:11px;}}th,td{{border:1px solid #ddd;padding:8px;}}th{{background:#eee;}}.badge{{padding:2px 6px;border-radius:4px;color:white;font-weight:bold;font-size:10px;display:inline-block;}}</style></head><body><div class='h'><h2>Rapport : {view_mode}</h2><span>{datetime.now().strftime('%d/%m/%Y')}</span></div><p><b>Synthèse :</b> {n_com} Communes | {n_eco} Écoles</p>"
            curr_p, curr_c = "", ""
            for _, r in df_disp.iterrows():
                if r['Province'] != curr_p:
                    curr_p = r['Province']; print_html += f"<div class='prov-h'>📍 PROVINCE : {curr_p}</div>"
                if r['Commune'] != curr_c:
                    if curr_c != "": print_html += "</tbody></table>"
                    curr_c = r['Commune']; print_html += f"<div class='comm-h'>🏘️ Commune : {curr_c}</div><table><thead><tr><th style='width:35%'>École</th><th style='width:20%'>Paiement</th><th>Services</th></tr></thead><tbody>"
                p_col = "#FF43D0" if r.get('Paiement')=="Prépaiement" else "#008080"
                s_h = "".join([f"<span class='badge' style='background:{colors_map.get(s.strip(),'#999')}'>{s.strip()}</span> " for s in str(r.get('Services')).split('|') if s.strip() and s.strip()!="-"])
                print_html += f"<tr><td>{r['Ecole']}</td><td><span class='badge' style='background:{p_col}'>{r.get('Paiement','-')}</span></td><td>{s_h}</td></tr>"
            print_html += "</tbody></table></body></html>"
            b64 = base64.b64encode(print_html.encode('utf-8')).decode('utf-8')
            js = f"<script>function pr(){{ var w=window.open(); w.document.write(decodeURIComponent(escape(atob('{b64}')))); w.document.close(); setTimeout(function(){{w.print();}},500); }}</script><button onclick='pr()' style='width:100%;padding:12px;background:#008080;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;'>🖨️ IMPRIMER LE RAPPORT</button>"
            components.html(js, height=60)
