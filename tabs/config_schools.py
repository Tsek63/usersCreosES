import streamlit as st
import pandas as pd
import plotly.express as px
import io
from safe_gsheets import safe_write
from ui_components import icon_po, is_province

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. NETTOYAGE CRITIQUE ET DÉDOUBLONNAGE ---
    # On force le format texte et on supprime les doublons de Fase école dès le départ
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
            # --- ACTION DE MASSE ---
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.warning(f"Passer TOUTES les écoles de {c_sel} à 'NON' ?")
                if st.button(f"Confirmer le refus pour tout {c_sel}", use_container_width=True, key="btn_mass_refuse"):
                    fases_commune = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    new_rows = []
                    for f in fases_commune:
                        new_rows.append({
                            "Fase école": f, "Commune": c_sel, "Province": p_sel,
                            "Extrascolaire": "Non", "Paiement": "-", "Services": "-"
                        })
                    df_batch = pd.DataFrame(new_rows)
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(df_batch['Fase école'])], df_batch], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

            # --- CONFIGURATION INDIVIDUELLE ---
            df_comm_schools = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
            df_comm_schools['Fase école'] = df_comm_schools['Fase école'].astype(str)
            
            school_opts = []
            for _, r in df_comm_schools.iterrows():
                fase = r['Fase école']
                match = df_config[df_config['Fase école'] == fase]
                icon = " ✅" if (not match.empty and match.iloc[0]['Extrascolaire'] == 'Oui') else (" ❌" if (not match.empty and match.iloc[0]['Extrascolaire'] == 'Non') else " ⭕")
                school_opts.append(f"{r['Ecole']}{icon} — Fase {fase}")
            
            ecole_label_sel = st.selectbox("3. École individuelle", school_opts, key="cfg_e")
            ecole_fase_sel = ecole_label_sel.split(" — Fase ")[-1]

            if ecole_fase_sel:
                curr = df_config[df_config['Fase école'] == ecole_fase_sel]
                idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
                curr_pay = curr.iloc[0]['Paiement'] if (not curr.empty and curr.iloc[0]['Paiement'] != "-") else "Prépaiement"
                idx_pay = 0 if curr_pay == "Prépaiement" else 1
                curr_serv = str(curr.iloc[0]['Services']).split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else []

                with st.form("form_ecole_v3"):
                    st.write(f"**Édition FASE : {ecole_fase_sel}**")
                    f1, f2 = st.columns(2)
                    v_ex = f1.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                    v_pa = f2.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=idx_pay, horizontal=True)
                    v_sv = st.multiselect("Services utilisés", svc_list, default=[s for s in curr_serv if s in svc_list])
                    
                    if st.form_submit_button("💾 ENREGISTRER", use_container_width=True):
                        new_line = pd.DataFrame([{"Fase école": ecole_fase_sel, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != ecole_fase_sel], new_line], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear(); st.rerun()

    with col_r:
        # BLOCS STATS
        st.markdown(f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:10px;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.9;">Utilisent l'Extrascolaire</div>
            <div style="font-size:48px; font-weight:bold;">{len(df_active)}</div>
        </div>
        <div style="background-color:#FF43D0; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.9;">N'utilisent pas</div>
            <div style="font-size:48px; font-weight:bold;">{len(df_refus)}</div>
        </div>""", unsafe_allow_html=True)

    # --- 3. FILTRES ET LISTE ---
    st.divider()
    view_mode = st.radio("Afficher la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="view_toggle")
    
    target_df = df_active if "Utilisatrices" in view_mode else df_refus
    color_theme = "#008080" if "Utilisatrices" in view_mode else "#FF43D0"

    f1, f2, f3 = st.columns(3)
    fl_p = f1.multiselect("Par Province", sorted(target_df['Province'].unique()), key="fl_p_v3")
    
    df_filt = target_df.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]

    if not df_filt.empty:
        # Merge ultra-sécurisé pour éviter les doublons de lignes
        df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates(subset=['Fase école'])
        df_filt = df_filt.merge(df_names, on='Fase école', how='left').fillna("-")
        
        # Tableau
        h1, h2, h3, h4, h5 = st.columns([1.5, 1.5, 2, 3, 0.5])
        h1.write("**Commune**"); h2.write("**Status**"); h3.write("**École**"); h4.write("**Services**")
        
        # UTILISATION DE ENUMERATE POUR DES CLÉS UNIQUES
        for i, (_, row) in enumerate(df_filt.iterrows()):
            r1, r2, r3, r4, r5 = st.columns([1.5, 1.5, 2, 3, 0.5])
            r1.write(row['Commune'])
            r2.markdown(f'<b style="color:{color_theme}">{row["Extrascolaire"]}</b>', unsafe_allow_html=True)
            r3.write(f"{row['Ecole']} ({row['Fase école']})")
            
            if "Utilisatrices" in view_mode:
                svs = str(row['Services']).split('|')
                s_badges = ""
                colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in svs:
                    if s.strip() and s.strip() != "-":
                        s_badges += f'<span style="background:{colors.get(s,"#999")}; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold; margin-right:4px; display:inline-block; margin-bottom:2px;">{s}</span>'
                r4.markdown(s_badges, unsafe_allow_html=True)
            
            # CLÉ DE BOUTON UNIQUE BASÉE SUR L'INDEX i
            if r5.button("🗑️", key=f"del_row_{i}_{row['Fase école']}"):
                df_final = df_config[df_config['Fase école'] != str(row['Fase école'])]
                safe_write(conn, "EcolesConfig", df_final)
                st.cache_data.clear(); st.rerun()
    else:
        st.info("Aucune donnée.")
