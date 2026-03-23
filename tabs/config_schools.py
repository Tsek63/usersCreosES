import streamlit as st
import pandas as pd
import plotly.express as px
import io
from safe_gsheets import safe_write
from ui_components import icon_po, is_province

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. NETTOYAGE ET PRÉPARATION ---
    df_config['Fase école'] = df_config['Fase école'].astype(str).str.strip()
    df_config = df_config.drop_duplicates(subset=['Fase école'], keep='last').reset_index(drop=True)
    
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_refus = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # --- 2. MISE EN PAGE HAUT (Formulaire | Blocs Stats) ---
    col_l, col_r = st.columns([1.8, 1.2])

    with col_l:
        st.subheader("📝 Configurer une École ou une Commune")
        s1, s2, s3 = st.columns([1, 1, 1.5])
        
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, 
                                 format_func=lambda x: f"{icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                 key="cfg_c")
        
        if c_sel != "— Sélectionnez —":
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button(f"Tout {c_sel} à 'NON'", use_container_width=True, key="btn_mass_non"):
                        fases_commune = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                        new_rows = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Non", "Paiement": "-", "Services": "-"} for f in fases_commune]
                        df_upd = pd.concat([df_config[~df_config['Fase école'].isin(fases_commune)], pd.DataFrame(new_rows)], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear(); st.rerun()
                with c_act2:
                    if st.button(f"Supprimer {c_sel} de la config", use_container_width=True, key="btn_mass_del"):
                        df_upd = df_config[df_config['Commune'] != c_sel]
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear(); st.rerun()

            df_comm_schools = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
            school_opts = [f"{r['Ecole']} {'✅' if not df_config[(df_config['Fase école']==str(r['Fase école'])) & (df_config['Extrascolaire']=='Oui')].empty else ('❌' if not df_config[(df_config['Fase école']==str(r['Fase école'])) & (df_config['Extrascolaire']=='Non')].empty else '⭕')} — Fase {r['Fase école']}" for _, r in df_comm_schools.iterrows()]
            
            ecole_label_sel = st.selectbox("3. École individuelle", school_opts, key="cfg_e")
            ecole_fase_sel = ecole_label_sel.split(" — Fase ")[-1]

            if ecole_fase_sel:
                curr = df_config[df_config['Fase école'] == ecole_fase_sel]
                idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
                with st.form("form_config_final_sync_v2"):
                    f1, f2 = st.columns(2)
                    v_ex = f1.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                    v_pa = f2.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=0 if (curr.empty or curr.iloc[0]['Paiement'] != "Post-paiement") else 1, horizontal=True)
                    v_sv = st.multiselect("Services utilisés", svc_list, default=str(curr.iloc[0]['Services']).split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else [])
                    if st.form_submit_button("💾 ENREGISTRER LA CONFIGURATION", use_container_width=True):
                        new_line = pd.DataFrame([{"Fase école": ecole_fase_sel, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != ecole_fase_sel], new_line], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear(); st.rerun()

    with col_r:
        # --- BLOC TEAL (UTILISATEURS) ---
        n_pre = len(df_active[df_active['Paiement']=='Prépaiement'])
        n_post = len(df_active[df_active['Paiement']=='Post-paiement'])
        n_comm_act = df_active['Commune'].nunique()

        st.markdown(f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui Utilisent l'Extrascolaire de Creos</div>
            <div style="font-size:64px; font-weight:bold; line-height:1;">{len(df_active)}</div>
            <div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
                <div style="text-align:center;">
                    <span style="display:block; font-size:22px; font-weight:900; color:#ec4899;">{n_pre}</span>
                    <span style="font-size:22px;">Prépaiement</span>
                </div>
                <div style="text-align:center;">
                    <span style="display:block; font-size:22px; font-weight:900; color:#38bdf8;">{n_post}</span>
                    <span style="font-size:22px;">Post-paiement</span>
                </div>
                <div style="text-align:center;">
                    <span style="display:block; font-size:22px; font-weight:900; color:#a78bfa;">{n_comm_act}</span>
                    <span style="font-size:22px;">Communes</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # --- BLOC FUCHSIA (REFUS) ---
        n_comm_ref = df_refus['Commune'].nunique()
        st.markdown(f"""
        <div style="background-color:#FF43D0; padding:20px; border-radius:15px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui n'utilisent pas l'Extrascolaire de Creos</div>
            <div style="font-size:64px; font-weight:bold; line-height:1;">{len(df_refus)}</div>
            <div style="display:flex; justify-content:center; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
                <div style="text-align:center;">
                    <span style="display:block; font-size:22px; font-weight:900;">{n_comm_ref}</span>
                    <span style="font-size:22px;">Communes ont dit NON</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # --- 3. FILTRES ET LISTE ---
    st.divider()
    view_mode = st.radio("Afficher la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="toggle_final_check")
    target_df = df_active if "Utilisatrices" in view_mode else df_refus
    color_theme = "#008080" if "Utilisatrices" in view_mode else "#FF43D0"

    f1, f2, f3 = st.columns(3)
    fl_p = f1.multiselect("Filtrer par Province", sorted(target_df['Province'].unique()), key="f_p_check")
    
    df_filt = target_df.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]

    if not df_filt.empty:
        df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates(subset=['Fase école'])
        df_filt = df_filt.merge(df_names, on='Fase école', how='left').fillna("-")
        
        h1, h2, h3, h4, h5 = st.columns([1.5, 1.2, 2, 3, 0.5])
        h1.write("**Commune**"); h2.write("**Status**"); h3.write("**École**"); h4.write("**Services**" if "Utilisatrices" in view_mode else "")
        
        for i, (_, row) in enumerate(df_filt.iterrows()):
            r1, r2, r3, r4, r5 = st.columns([1.5, 1.2, 2, 3, 0.5])
            r1.write(row['Commune'])
            r2.markdown(f'<b style="color:{color_theme}">{row["Extrascolaire"]}</b>', unsafe_allow_html=True)
            r3.write(f"{row['Ecole']} ({row['Fase école']})")
            
            if "Utilisatrices" in view_mode:
                svs = str(row['Services']).split('|')
                s_badges = ""
                colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in svs:
                    if s.strip() and s.strip() != "-":
                        s_badges += f'<span style="background:{colors.get(s,"#999")}; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold; margin-right:4px; display:inline-block;">{s}</span>'
                r4.markdown(s_badges, unsafe_allow_html=True)
            
            if r5.button("🗑️", key=f"del_check_{i}_{row['Fase école']}"):
                df_final = df_config[df_config['Fase école'] != str(row['Fase école'])]
                safe_write(conn, "EcolesConfig", df_final)
                st.cache_data.clear(); st.rerun()
    else:
        st.info("Aucune donnée.")
