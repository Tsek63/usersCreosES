import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64
from safe_gsheets import safe_write
from ui_components import icon_po, is_province

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. PRÉPARATION DES DONNÉES ---
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
        
        # --- LOGIQUE D'ACTION DE MASSE ---
        if c_sel != "— Sélectionnez —":
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.warning(f"Passer TOUTES les écoles de {c_sel} à 'NON' ?")
                if st.button(f"Confirmer le refus pour tout {c_sel}", use_container_width=True):
                    # On récupère toutes les écoles de cette commune dans la liste FWB
                    schools_to_mark = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].unique()
                    new_rows = []
                    for fase in schools_to_mark:
                        new_rows.append({
                            "Fase école": str(fase), "Commune": c_sel, "Province": p_sel,
                            "Extrascolaire": "Non", "Paiement": "-", "Services": "-"
                        })
                    df_new_batch = pd.DataFrame(new_rows)
                    # On met à jour le fichier config (on remplace l'existant)
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(schools_to_mark)], df_new_batch], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

            # --- CONFIGURATION INDIVIDUELLE ---
            df_comm_schools = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
            school_opts = []
            for _, r in df_comm_schools.iterrows():
                fase = str(r['Fase école'])
                match = df_config[df_config['Fase école'] == fase]
                if not match.empty:
                    icon = " ✅" if match.iloc[0]['Extrascolaire'] == 'Oui' else " ❌"
                else:
                    icon = " ⭕"
                school_opts.append(f"{r['Ecole']}{icon} — Fase {fase}")
            
            ecole_label_sel = st.selectbox("3. École individuelle", school_opts, key="cfg_e")
            ecole_fase_sel = ecole_label_sel.split(" — Fase ")[-1]
            ecole_name_sel = ecole_label_sel.split(" — Fase ")[0][:-2]

            if ecole_fase_sel:
                curr = df_config[df_config['Fase école'] == ecole_fase_sel]
                idx_ex = 0 if (not curr.empty and curr.iloc[0]['Extrascolaire'] == 'Oui') else 1
                curr_pay = curr.iloc[0]['Paiement'] if (not curr.empty and curr.iloc[0]['Paiement'] != "-") else "Prépaiement"
                idx_pay = 0 if curr_pay == "Prépaiement" else 1
                curr_serv = curr.iloc[0]['Services'].split('|') if (not curr.empty and curr.iloc[0]['Services'] != "-") else []

                with st.form("form_ecole_cfg"):
                    st.markdown(f"**Modification : {ecole_name_sel}**")
                    f1, f2 = st.columns(2)
                    with f1: v_extra = st.radio("Utilise l'Extrascolaire ?", ["Oui", "Non"], index=idx_ex, horizontal=True)
                    with f2: v_pay = st.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], index=idx_pay, horizontal=True)
                    v_serv = st.multiselect("Services utilisés", svc_list, default=[s for s in curr_serv if s in svc_list])
                    
                    if st.form_submit_button("💾 ENREGISTRER CETTE ÉCOLE", use_container_width=True):
                        new_line = pd.DataFrame([{
                            "Fase école": ecole_fase_sel, "Commune": c_sel, "Province": p_sel,
                            "Extrascolaire": v_extra, "Paiement": v_pay if v_extra == "Oui" else "-",
                            "Services": "|".join(v_serv) if (v_extra == "Oui" and v_serv) else "-"
                        }])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != ecole_fase_sel], new_line], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear(); st.rerun()

    with col_r:
        # --- BLOC TEAL (ACTIVES) ---
        st.markdown(f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:15px;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.9; font-weight:600;">Utilisent l'Extrascolaire</div>
            <div style="font-size:54px; font-weight:bold; line-height:1;">{len(df_active)}</div>
            <div style="font-size:12px; margin-top:5px; opacity:0.8;">{df_active['Commune'].nunique()} communes</div>
        </div>""", unsafe_allow_html=True)

        # --- BLOC FUCHSIA (REFUS) ---
        st.markdown(f"""
        <div style="background-color:#FF43D0; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.9; font-weight:600;">N'utilisent pas l'Extrascolaire</div>
            <div style="font-size:54px; font-weight:bold; line-height:1;">{len(df_refus)}</div>
            <div style="font-size:12px; margin-top:5px; opacity:0.8;">{df_refus['Commune'].nunique()} communes ont dit NON</div>
        </div>""", unsafe_allow_html=True)

    # --- 3. FILTRES ET LISTE ---
    st.divider()
    view_mode = st.radio("Afficher la liste :", ["Écoles Utilisatrices (✅)", "Écoles avec Refus (❌)"], horizontal=True)

    target_df = df_active if "Utilisatrices" in view_mode else df_refus
    color_theme = "#008080" if "Utilisatrices" in view_mode else "#FF43D0"

    f1, f2, f3 = st.columns(3)
    with f1: fl_p = st.multiselect("Filtrer par Province", sorted(target_df['Province'].unique()))
    with f2: fl_m = st.multiselect("Filtrer par Paiement", ["Prépaiement", "Post-paiement"]) if "Utilisatrices" in view_mode else st.empty()
    with f3: fl_s = st.multiselect("Filtrer par Service", svc_list) if "Utilisatrices" in view_mode else st.empty()

    df_filt = target_df.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]
    if not df_filt.empty:
        df_filt = df_filt.merge(df_ecoles[['Fase école', 'Ecole']], on='Fase école', how='left')
        
        # EXPORT & IMPRESSION
        c_ex1, c_ex2 = st.columns([1, 4])
        with c_ex1:
            buf = io.BytesIO()
            df_filt.to_excel(buf, index=False)
            st.download_button(f"📥 Export Excel ({'Actives' if color_theme=='#008080' else 'Refus'})", 
                               buf.getvalue(), "liste_export.xlsx")
        
        # TABLEAU DE SYNTHESE
        h1, h2, h3, h4, h5 = st.columns([1.5, 1.5, 2, 3, 0.5])
        h1.write("**Commune**"); h2.write("**Status**"); h3.write("**École**"); h4.write("**Services**" if color_theme=="#008080" else "")
        
        for _, row in df_filt.iterrows():
            r1, r2, r3, r4, r5 = st.columns([1.5, 1.5, 2, 3, 0.5])
            r1.write(row['Commune'])
            r2.markdown(f'<b style="color:{color_theme}">{row["Extrascolaire"]}</b>', unsafe_allow_html=True)
            r3.write(f"{row['Ecole']} ({row['Fase école']})")
            
            if color_theme == "#008080": # On n'affiche les badges que pour les actives
                svs = str(row['Services']).split('|')
                s_badges = ""
                colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in svs:
                    if s.strip() and s.strip() != "-":
                        s_badges += f'<span style="background:{colors.get(s,"#999")}; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold; margin-right:4px; display:inline-block; margin-bottom:2px;">{s}</span>'
                r4.markdown(s_badges, unsafe_allow_html=True)
            
            if r5.button("🗑️", key=f"del_cfg_{row['Fase école']}"):
                df_new = df_config[df_config['Fase école'] != row['Fase école']]
                safe_write(conn, "EcolesConfig", df_new)
                st.cache_data.clear(); st.rerun()
    else:
        st.info("Aucune donnée pour cette sélection.")
