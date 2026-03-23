import streamlit as st
import pandas as pd
import plotly.express as px
import io
from safe_gsheets import safe_write
from ui_components import icon_po, is_province

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. CALCUL DES STATS (BLOC TEAL) ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    n_active = len(df_active)
    n_comm = df_active['Commune'].nunique() if not df_active.empty else 0
    n_prep = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    n_post = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    svc_cnt = {s: int(df_active['Services'].str.contains(s, na=False).sum()) for s in svc_list}

    # --- 2. MISE EN PAGE HAUT (Formulaire | Bloc Teal) ---
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("📝 Configurer une École")
        s1, s2, s3 = st.columns([1, 1, 1.5])
        
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, 
                                 format_func=lambda x: f"{icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                 key="cfg_c")
        with s3:
            if c_sel != "— Sélectionnez —":
                df_comm_schools = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
                school_opts = []
                for _, r in df_comm_schools.iterrows():
                    fase = str(r['Fase école'])
                    match = df_config[df_config['Fase école'] == fase]
                    icon = " ✅" if (not match.empty and match.iloc[0]['Extrascolaire'] == 'Oui') else " ⭕"
                    school_opts.append(f"{r['Ecole']}{icon} — Fase {fase}")
                ecole_label_sel = st.selectbox("3. École", school_opts, key="cfg_e")
                ecole_fase_sel = ecole_label_sel.split(" — Fase ")[-1]
                ecole_name_sel = ecole_label_sel.split(" — Fase ")[0][:-2]
            else:
                st.selectbox("3. École", ["—"], disabled=True)
                ecole_fase_sel = None

        if ecole_fase_sel:
            curr = df_config[df_config['Fase école'] == ecole_fase_sel]
            idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
            curr_pay = curr.iloc[0]['Paiement'] if not curr.empty else "Prépaiement"
            idx_pay = 0 if curr_pay == "Prépaiement" else 1
            curr_serv = curr.iloc[0]['Services'].split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else []

            with st.form("form_ecole_cfg"):
                st.markdown(f"**Modification : {ecole_name_sel}** (FASE {ecole_fase_sel})")
                f1, f2 = st.columns(2)
                with f1: v_extra = st.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                with f2: v_pay = st.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=idx_pay, horizontal=True)
                v_serv = st.multiselect("Services utilisés", svc_list, default=[s for s in curr_serv if s in svc_list])
                if st.form_submit_button("💾 ENREGISTRER CETTE ÉCOLE", use_container_width=True):
                    new_line = pd.DataFrame([{"Fase école": ecole_fase_sel, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_extra, "Paiement": v_pay if v_extra == "Oui" else "-", "Services": "|".join(v_serv) if (v_extra == "Oui" and v_serv) else "-"}])
                    df_upd = pd.concat([df_config[df_config['Fase école'] != ecole_fase_sel], new_line], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

    with col_r:
        teal_html = f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.8;">Total des écoles actives</div>
            <div style="font-size:52px; font-weight:bold; line-height:1;">{n_active}</div>
            <div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); padding:12px 0; margin:12px 0;">
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#ec4899;">{n_prep}</span><small>Pré</small></div>
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#38bdf8;">{n_post}</span><small>Post</small></div>
                <div><span style="display:block; font-size:16px; font-weight:bold; color:#a78bfa;">{n_comm}</span><small>Com.</small></div>
            </div>
        </div>"""
        st.markdown(teal_html, unsafe_allow_html=True)

    # --- 3. FILTRES ET LISTE AVEC GRAPHIQUES ---
    st.divider()
    st.subheader("🔍 Liste et suppression des écoles actives")
    
    f1, f2, f3 = st.columns(3)
    with f1: fl_p = st.multiselect("Par Province", sorted(df_active['Province'].unique()))
    with f2: fl_m = st.multiselect("Par Paiement", ["Prépaiement", "Post-paiement"])
    with f3: fl_s = st.multiselect("Par Service", svc_list)

    df_filt = df_active.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]
    if fl_m: df_filt = df_filt[df_filt['Paiement'].isin(fl_m)]
    for s in fl_s: df_filt = df_filt[df_filt['Services'].str.contains(s, na=False)]

    if not df_filt.empty:
        df_filt = df_filt.merge(df_ecoles[['Fase école', 'Ecole']], on='Fase école', how='left')
        
        col_table, col_viz = st.columns([1.8, 1]) # Augmentation de la place pour le tableau
        
        with col_table:
            # Augmentation de la largeur de la colonne Services (2.5 -> 3)
            h1, h2, h3, h4, h5 = st.columns([1.5, 1.5, 2, 3, 0.5])
            h1.write("**Commune**"); h2.write("**Paiement**"); h3.write("**École**"); h4.write("**Services**")
            
            for _, row in df_filt.iterrows():
                r1, r2, r3, r4, r5 = st.columns([1.5, 1.5, 2, 3, 0.5])
                r1.write(row['Commune'])
                p_c = "#ec4899" if row['Paiement'] == "Prépaiement" else "#38bdf8"
                r2.markdown(f'<b style="color:{p_c}; font-size:13px;">{row["Paiement"]}</b>', unsafe_allow_html=True)
                r3.write(f"{row['Ecole']} ({row['Fase école']})")
                
                # Badges services plus grands
                svs = row['Services'].split('|')
                s_badges = ""
                colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in svs:
                    if s.strip() and s.strip() != "-":
                        # Police à 11px et padding plus généreux (4px 8px)
                        s_badges += f'<span style="background:{colors.get(s,"#999")}; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold; margin-right:4px; display:inline-block; margin-bottom:2px;">{s}</span>'
                r4.markdown(s_badges, unsafe_allow_html=True)
                
                if r5.button("🗑️", key=f"trash_{row['Fase école']}"):
                    safe_write(conn, "EcolesConfig", df_config[df_config['Fase école'] != row['Fase école']])
                    st.cache_data.clear(); st.rerun()

        with col_viz:
            fig_p = px.pie(df_filt, names='Paiement', hole=0.4, title="Modes de Paiement", 
                           color_discrete_map={'Prépaiement': '#ec4899', 'Post-paiement': '#38bdf8'},
                           color='Paiement')
            fig_p.update_layout(height=280, margin=dict(l=0,r=0,t=40,b=0), legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_p, use_container_width=True)
            
            all_s = []
            for s in df_filt['Services'].str.split('|'):
                if isinstance(s, list): all_s.extend([x.strip() for x in s if x.strip() and x != "-"] )
            
            if all_s:
                df_s_plot = pd.DataFrame(all_s, columns=['Service']).value_counts().reset_index()
                df_s_plot.columns = ['Service', 'Nombre']
                fig_s = px.bar(df_s_plot, x='Nombre', y='Service', orientation='h', title="Popularité des Services",
                               color='Service', color_discrete_map=colors)
                fig_s.update_layout(height=280, showlegend=False, margin=dict(l=0,r=0,t=40,b=0), xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Aucune école ne correspond à ces filtres.")
