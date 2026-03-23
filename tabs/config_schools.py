import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb):
    # --- BOUTON ACTUALISER ---
    titre_col, refresh_col = st.columns([0.8, 0.2])
    with refresh_col:
        if st.button("🔄 Actualiser", use_container_width=True, key="btn_ref_config"):
            st.cache_data.clear()
            st.rerun()

    st.header("⚙️ Gestion des Écoles par Commune")

    # --- PRÉPARATION DES DONNÉES ---
    df_config['Fase école'] = df_config['Fase école'].astype(str).str.strip()
    df_config = df_config.drop_duplicates(subset=['Fase école'], keep='last').reset_index(drop=True)
    
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    active_communes = set(df_active['Commune'].unique())
    df_refus = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # --- MISE EN PAGE HAUT (Formulaire et Stats) ---
    col_l, col_r = st.columns([1.8, 1.2])

    with col_l:
        st.subheader("📝 Configuration")
        s1, s2, s3 = st.columns([1, 1, 1.5])
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            c_sel = st.selectbox("2. Commune / PO", ["— Sélectionnez —"] + c_opts, 
                                 format_func=lambda x: f"{'✅' if x in active_communes else '⚪'} {icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                                 key="cfg_c")
        
        if c_sel != "— Sélectionnez —":
            # --- ACTIONS GROUPÉES ---
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.markdown("**1. Premier encodage groupé**")
                g1, g2 = st.columns(2)
                with g1:
                    m_pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True, key="m_p")
                with g2:
                    m_svc = st.multiselect("Services", svc_list, key="m_s")
                
                if st.button(f"🚀 Activer tout {c_sel} à 'OUI'", use_container_width=True):
                    fases = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    new_rows = []
                    for f in fases:
                        new_rows.append({
                            "Fase école": f, "Commune": c_sel, "Province": p_sel,
                            "Extrascolaire": "Oui", "Paiement": m_pay, 
                            "Services": "|".join(m_svc) if m_svc else "-"
                        })
                    df_new = pd.DataFrame(new_rows)
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(fases)], df_new], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear()
                    st.rerun()

                st.markdown("---")
                st.markdown("**2. Actions rapides**")
                ca1, ca2 = st.columns(2)
                with ca1:
                    if st.button(f"Tout {c_sel} à 'NON'", use_container_width=True, key="btn_all_no"):
                        fases = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                        rows_no = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Non", "Paiement": "-", "Services": "-"} for f in fases]
                        df_upd = pd.concat([df_config[~df_config['Fase école'].isin(fases)], pd.DataFrame(rows_no)], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear()
                        st.rerun()
                with ca2:
                    if st.button(f"Réinitialiser {c_sel}", use_container_width=True, key="btn_reset_po"):
                        df_upd = df_config[df_config['Commune'] != c_sel]
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear()
                        st.rerun()

            # --- INDIVIDUEL ---
            df_sch = df_ecoles[df_ecoles['Commune'] == c_sel].copy()
            sch_opts = []
            for _, r in df_sch.iterrows():
                f = str(r['Fase école'])
                m = df_config[df_config['Fase école'] == f]
                icon = " ✅" if (not m.empty and m.iloc[0]['Extrascolaire'] == 'Oui') else (" ❌" if (not m.empty and m.iloc[0]['Extrascolaire'] == 'Non') else " ⭕")
                sch_opts.append(f"{r['Ecole']}{icon} — Fase {f}")
            
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
                    if st.form_submit_button("💾 ENREGISTRER", use_container_width=True):
                        new = pd.DataFrame([{"Fase école": e_fase, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != e_fase], new], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd)
                        st.cache_data.clear()
                        st.rerun()

    with col_r:
        # --- CALCULS POUR LES STATS ---
        n_act = len(df_active)
        n_pre = len(df_active[df_active['Paiement'] == 'Prépaiement'])
        n_post = len(df_active[df_active['Paiement'] == 'Post-paiement'])
        n_com_act = len(active_communes)
        n_ref = len(df_refus)
        n_com_ref = df_refus['Commune'].nunique()

        # BLOC TEAL
        st.markdown(f"""
<div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui Utilisent l'Extrascolaire de Creos</div>
<div style="font-size:64px; font-weight:bold; line-height:1;">{n_act}</div>
<div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
<div style="text-align:center;"><b style="font-size:22px; color:#ec4899; font-weight:900;">{n_pre}</b><br><span style="font-size:22px;">Prépaiement</span></div>
<div style="text-align:center;"><b style="font-size:22px; color:#38bdf8; font-weight:900;">{n_post}</b><br><span style="font-size:22px;">Post-paiement</span></div>
<div style="text-align:center;"><b style="font-size:22px; color:#a78bfa; font-weight:900;">{n_com_act}</b><br><span style="font-size:22px;">Communes</span></div>
</div></div>""", unsafe_allow_html=True)

        # BLOC FUCHSIA
        st.markdown(f"""
<div style="background-color:#FF43D0; padding:20px; border-radius:15px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui n'utilisent pas l'Extrascolaire de Creos</div>
<div style="font-size:64px; font-weight:bold; line-height:1;">{n_ref}</div>
<div style="display:flex; justify-content:center; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
<div style="text-align:center;"><b style="font-size:22px; font-weight:900;">{n_com_ref}</b><br><span style="font-size:22px;">Communes ont dit NON</span></div>
</div></div>""", unsafe_allow_html=True)

    # --- LISTE FILTRÉE ---
    st.divider()
    view = st.radio("Afficher la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True, key="toggle_list")
    target = df_active if "Utilisatrices" in view else df_refus
    theme = "#008080" if "Utilisatrices" in view else "#FF43D0"
    
    fl_p = st.multiselect("Filtrer par Province", sorted(target['Province'].unique()), key="f_p_cfg")
    df_f = target.copy()
    if fl_p: 
        df_f = df_f[df_f['Province'].isin(fl_p)]

    if not df_f.empty:
        df_names = df_ecoles[['Fase école', 'Ecole']].drop_duplicates()
        df_f = df_f.merge(df_names, on='Fase école', how='left').fillna("-")
        h1, h2, h3, h4, h5 = st.columns([1.5, 1.2, 2, 3, 0.5])
        h1.write("**Commune**")
        h2.write("**Status**")
        h3.write("**École**")
        h4.write("**Services**" if "Utilisatrices" in view else "")
        
        for i, (_, row) in enumerate(df_f.iterrows()):
            r1, r2, r3, r4, r5 = st.columns([1.5, 1.2, 2, 3, 0.5])
            r1.write(row['Commune'])
            r2.markdown(f'<b style="color:{theme}">{row["Extrascolaire"]}</b>', unsafe_allow_html=True)
            r3.write(f"{row['Ecole']} ({row['Fase école']})")
            
            if "Utilisatrices" in view:
                badges = ""
                clrs = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
                for s in str(row['Services']).split('|'):
                    if s.strip() and s.strip() != "-":
                        badges += f'<span style="background:{clrs.get(s,"#999")}; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold; margin-right:4px; display:inline-block;">{s}</span>'
