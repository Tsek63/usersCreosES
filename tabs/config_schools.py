import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64
import streamlit.components.v1 as components
from safe_gsheets import safe_write
from ui_components import icon_po, is_province

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. CALCUL DES STATS POUR LE BLOC TEAL ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    n_active = len(df_active)
    n_comm = df_active['Commune'].nunique() if not df_active.empty else 0
    n_prep = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    n_post = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    svc_cnt = {s: int(df_active['Services'].str.contains(s, na=False).sum()) for s in svc_list}

    # --- 2. MISE EN PAGE HAUT (Formulaire | Bloc Teal) ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📝 Configurer une École")
        s1, s2, s3 = st.columns([1, 1, 1.5])
        
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="t4_prov")
        
        with s2:
            communes_p = sorted(data_fwb.get(p_sel, []))
            com_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + communes_p, 
                                   format_func=lambda x: f"{icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                   key="t4_comm")

        with s3:
            if com_sel != "— Sélectionnez —":
                df_comm_schools = df_ecoles[df_ecoles['Commune'] == com_sel].copy()
                school_opts = []
                for _, r in df_comm_schools.iterrows():
                    fase = str(r['Fase école'])
                    match = df_config[df_config['Fase école'] == fase]
                    icon = " ✅" if (not match.empty and match.iloc[0]['Extrascolaire'] == 'Oui') else " ⭕"
                    school_opts.append(f"{r['Ecole']}{icon} — Fase {fase}")
                
                ecole_label_sel = st.selectbox("3. École", school_opts, key="t4_ecole")
                ecole_fase_sel = ecole_label_sel.split(" — Fase ")[-1]
                ecole_name_sel = ecole_label_sel.split(" — Fase ")[0][:-2] # Enlève l'icône et l'espace
            else:
                st.selectbox("3. École", ["—"], disabled=True)
                ecole_fase_sel = None

        if ecole_fase_sel:
            # Pré-remplissage
            curr = df_config[df_config['Fase école'] == ecole_fase_sel]
            idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
            curr_pay = curr.iloc[0]['Paiement'] if not curr.empty else "Prépaiement"
            idx_pay = 0 if curr_pay == "Prépaiement" else 1
            curr_serv = curr.iloc[0]['Services'].split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else []

            with st.form("form_ecole_cfg"):
                st.markdown(f"**Édition : {ecole_name_sel}**")
                f1, f2 = st.columns(2)
                with f1:
                    v_extra = st.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                with f2:
                    v_pay = st.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=idx_pay, horizontal=True)
                
                v_serv = st.multiselect("Services utilisés", svc_list, default=[s for s in curr_serv if s in svc_list])
                
                if st.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                    new_row = pd.DataFrame([{
                        "Fase école": ecole_fase_sel, "Commune": com_sel, "Province": p_sel,
                        "Extrascolaire": v_extra, "Paiement": v_pay if v_extra == "Oui" else "-",
                        "Services": "|".join(v_serv) if (v_extra == "Oui" and v_serv) else "-"
                    }])
                    df_upd = pd.concat([df_config[df_config['Fase école'] != ecole_fase_sel], new_row], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

    with col_right:
        # --- BLOC TEAL ORIGINAL ---
        teal_html = f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.8;">Total des écoles actives</div>
            <div style="font-size:52px; font-weight:bold; line-height:1;">{n_active}</div>
            <div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); padding:12px 0; margin:12px 0;">
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#ec4899;">{n_prep}</span><small>Prépaiement</small></div>
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#38bdf8;">{n_post}</span><small>Post-paiement</small></div>
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#a78bfa;">{n_comm}</span><small>Communes</small></div>
            </div>
            <div style="text-align:left; font-size:10px; display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
                <div style="background:rgba(255,255,255,0.1); padding:5px; border-radius:4px;">Cant. Jour : {svc_cnt['Cantine Jour']}</div>
                <div style="background:rgba(255,255,255,0.1); padding:5px; border-radius:4px;">Cant. Sem. : {svc_cnt['Cantine Semaine']}</div>
                <div style="background:rgba(255,255,255,0.1); padding:5px; border-radius:4px;">Cant. Mois : {svc_cnt['Cantine Mois']}</div>
                <div style="background:rgba(255,255,255,0.1); padding:5px; border-radius:4px;">Garderie : {svc_cnt['Garderie']}</div>
            </div>
        </div>"""
        st.markdown(teal_html, unsafe_allow_html=True)

    # --- 3. FILTRES ET LISTE DÉTAILLÉE ---
    st.divider()
    st.subheader("🔍 Liste des écoles actives")
    
    f1, f2, f3 = st.columns(3)
    with f1: fl_p = st.multiselect("Filtrer par Province", sorted(df_active['Province'].unique()))
    with f2: fl_m = st.multiselect("Filtrer par Paiement", ["Prépaiement", "Post-paiement"])
    with f3: fl_s = st.multiselect("Filtrer par Service", svc_list)

    df_filt = df_active.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]
    if fl_m: df_filt = df_filt[df_filt['Paiement'].isin(fl_m)]
    for s in fl_s: df_filt = df_filt[df_filt['Services'].str.contains(s, na=False)]

    if not df_filt.empty:
        # Ajout du nom de l'école pour la liste
        df_filt = df_filt.merge(df_ecoles[['Fase école', 'Ecole']], on='Fase école', how='left')
        
        # BOUTON EXCEL
        buf = io.BytesIO()
        df_filt.to_excel(buf, index=False)
        st.download_button("📥 Exporter vers Excel", buf.getvalue(), "ecoles_actives.xlsx", use_container_width=True)

        col_list, col_viz = st.columns([1.8, 1])
        
        with col_list:
            # En-têtes
            h1, h2, h3, h4, h5 = st.columns([1.5, 1.5, 2, 2.5, 0.5])
            h1.write("**Commune**")
            h2.write("**Paiement**")
            h3.write("**École**")
            h4.write("**Services**")
            
            for _, row in df_filt.iterrows():
                r1, r2, r3, r4, r5 = st.columns([1.5, 1.5, 2, 2.5, 0.5])
                r1.write(row['Commune'])
                p_col = "#ec4899" if row['Paiement'] == "Prépaiement" else "#38bdf8"
                r2.markdown(f'<b style="color:{p_col}">{row["Paiement"]}</b>', unsafe_allow_html=True)
                r3.write(f"{row['Ecole']} ({row['Fase école']})")
                
                # Badges services
                svcs = row['Services'].split('|')
                svc_badges = ""
                colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in svcs:
                    if s.strip():
                        svc_badges += f'<span style="background:{colors.get(s,"#999")}; color:white; padding:2px 5px; border-radius:4px; font-size:9px; margin-right:3px;">{s}</span>'
                r4.markdown(svc_badges, unsafe_allow_html=True)
                
                if r5.button("🗑️", key=f"del_{row['Fase école']}"):
                    df_final = df_config[df_config['Fase école'] != row['Fase école']]
                    safe_write(conn, "EcolesConfig", df_final)
                    st.cache_data.clear(); st.rerun()

        with col_viz:
            fig_p = px.pie(df_filt, names='Paiement', hole=0.4, title="Modes de Paiement", color_discrete_sequence=['#ec4899', '#38bdf8'])
            fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig_p, use_container_width=True)
            
            # Bar chart services
            all_s = []
            for s in df_filt['Services'].str.split('|'): all_s.extend(s)
            df_s_plot = pd.DataFrame(all_s, columns=['S']).value_counts().reset_index()
            fig_s = px.bar(df_s_plot, x='count', y='S', orientation='h', title="Services populaires")
            fig_s.update_layout(height=250, margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Aucune école ne correspond à ces filtres.")
