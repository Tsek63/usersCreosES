import streamlit as st
import pandas as pd
import plotly.express as px
import io
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
    # PARTIE HAUTE : FORMULAIRE ET TOTAUX GLOBAUX
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
    st.subheader("Situation actuelle") # Taille équivalente à Configuration

    view_mode = st.radio("Filtre global :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="view_mode")
    
    # Séparation 70/30
    col_list, col_stats = st.columns([0.7, 0.3])

    with col_list:
        # --- FILTRES ---
        f1, f2, f3 = st.columns(3)
        with f1:
            fl_p = st.multiselect("Filtrer par Province", sorted(df_config['Province'].unique()), key="f_p")
        
        # Filtres Paiement et Services (Affichés uniquement si "Utilisatrices" est choisi)
        is_refus_view = "Refus" in view_mode
        with f2:
            fl_m = st.selectbox("Mode de paiement", ["TOUS", "Prépaiement", "Post-paiement"], disabled=is_refus_view)
        with f3:
            fl_s = st.selectbox("Services", ["TOUS"] + svc_list, disabled=is_refus_view)

        # --- LOGIQUE DE FILTRAGE ---
        df_target = df_config[df_config['Extrascolaire'] == ('Non' if is_refus_view else 'Oui')].copy()
        if fl_p:
            df_target = df_target[df_target['Province'].isin(fl_p)]
        if not is_refus_view:
            if fl_m != "TOUS":
                df_target = df_target[df_target['Paiement'] == fl_m]
            if fl_s != "TOUS":
                df_target = df_target[df_target['Services'].str.contains(fl_s, na=False)]

        # --- AFFICHAGE DE LA LISTE ---
        if not df_target.empty:
            df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates()
            df_display = df_target.merge(df_names, on='Fase école', how='left').fillna("-")
            
            h1, h2, h3, h4 = st.columns([1.5, 1.5, 2, 0.5])
            h1.write("**Commune**"); h2.write("**École**"); h3.write("**Détails**"); h4.write("")
            
            for i, (_, row) in enumerate(df_display.iterrows()):
                r1, r2, r3, r4 = st.columns([1.5, 1.5, 2, 0.5])
                r1.write(row['Commune'])
                r2.write(f"{row['Ecole']} ({row['Fase école']})")
                
                # Détails (Paiement + Services en badges)
                if not is_refus_view:
                    p_c = "#ec4899" if row['Paiement'] == "Prépaiement" else "#38bdf8"
                    details_html = f'<b style="color:{p_c};">{row["Paiement"]}</b><br>'
                    svs = str(row['Services']).split('|')
                    colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                    for s in svs:
                        if s.strip() and s.strip() != "-":
                            details_html += f'<span style="background:{colors.get(s.strip(),"#999")}; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:3px; display:inline-block; margin-top:2px;">{s.strip()}</span>'
                    r3.markdown(details_html, unsafe_allow_html=True)
                else:
                    r3.write("Refus enregistré")
                
                if r4.button("🗑️", key=f"del_low_{i}"):
                    df_new = df_config[df_config['Fase école'] != str(row['Fase école'])]
                    safe_write(conn, "EcolesConfig", df_new); st.cache_data.clear(); st.rerun()
        else:
            st.info("Aucune école ne correspond aux filtres.")

    with col_stats:
        # --- BLOC DE CHIFFRES DYNAMIQUES (30%) ---
        st.markdown(f"""
            <div style="background-color:#f1f5f9; padding:20px; border-radius:10px; border:1px solid #cbd5e1; color:#1e293b;">
                <div style="font-size:12px; font-weight:bold; color:#64748b; text-transform:uppercase;">Résultats filtrés</div>
                <hr style="margin:10px 0;">
                <div style="font-size:24px; font-weight:bold;">{df_target['Commune'].nunique()} <small style="font-size:14px; font-weight:normal;">Communes</small></div>
                <div style="font-size:24px; font-weight:bold;">{len(df_target)} <small style="font-size:14px; font-weight:normal;">Écoles</small></div>
            </div>
        """, unsafe_allow_html=True)

        if not is_refus_view and not df_target.empty:
            # Stats Paiement
            p_counts = df_target['Paiement'].value_counts()
            st.markdown(f"""
                <div style="margin-top:10px; padding:10px; background:#fff; border:1px solid #eee; border-radius:8px;">
                    <small>💳 <b>Prépaiement :</b> {p_counts.get('Prépaiement', 0)}</small><br>
                    <small>🏦 <b>Post-paiement :</b> {p_counts.get('Post-paiement', 0)}</small>
                </div>
            """, unsafe_allow_html=True)

            # Graphique Paiement
            fig_p = px.pie(df_target, names='Paiement', hole=0.4, height=200, color='Paiement',
                           color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
            fig_p.update_layout(margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
            st.plotly_chart(fig_p, use_container_width=True)

            # Stats Services
            all_s = []
            for s in df_target['Services'].str.split('|'):
                if isinstance(s, list): all_s.extend([x.strip() for x in s if x.strip() and x != "-"])
            
            if all_s:
                df_s_plot = pd.DataFrame(all_s, columns=['Service']).value_counts().reset_index()
                df_s_plot.columns = ['Service', 'Nombre']
                
                fig_s = px.bar(df_s_plot, x='Nombre', y='Service', orientation='h', height=300,
                               color='Service', color_discrete_map={"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"})
                fig_s.update_layout(margin=dict(l=10, r=10, t=30, b=10), showlegend=False, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True)
