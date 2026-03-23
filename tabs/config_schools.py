import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb):
    # --- BOUTON ACTUALISER ---
    c_title, c_refresh = st.columns([0.8, 0.2])
    with c_refresh:
        if st.button("🔄 Actualiser", use_container_width=True, key="ref_btn_cfg"):
            st.cache_data.clear()
            st.rerun()

    st.header("⚙️ Gestion des Écoles par Commune")

    # --- PRÉPARATION ---
    df_config['Fase école'] = df_config['Fase école'].astype(str).str.strip()
    df_config = df_config.drop_duplicates(subset=['Fase école'], keep='last').reset_index(drop=True)
    
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    active_communes = set(df_active['Commune'].unique())
    df_refus = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # --- MISE EN PAGE HAUT ---
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
                st.markdown("**1. Premier encodage groupé (Démarrer tout le PO)**")
                st.info("Cette action va créer une configuration 'OUI' pour TOUTES les écoles de la commune.")
                
                g1, g2 = st.columns(2)
                with g1:
                    mass_pay = st.radio("Paiement par défaut", ["Prépaiement", "Post-paiement"], horizontal=True, key="m_pay")
                with g2:
                    mass_svc = st.multiselect("Services par défaut", svc_list, key="m_svc")
                
                if st.button(f"🚀 Activer tout {c_sel} à 'OUI'", use_container_width=True):
                    # 1. Identifier TOUTES les écoles de cette commune dans la liste FWB
                    f_list = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                    # 2. Créer les nouvelles lignes
                    new_rows = []
                    for f in f_list:
                        new_rows.append({
                            "Fase école": f, "Commune": c_sel, "Province": p_sel,
                            "Extrascolaire": "Oui", "Paiement": mass_pay, 
                            "Services": "|".join(mass_svc) if mass_svc else "-"
                        })
                    df_new_batch = pd.DataFrame(new_rows)
                    # 3. Fusionner en remplaçant les éventuelles configs existantes pour ces écoles
                    df_upd = pd.concat([df_config[~df_config['Fase école'].isin(f_list)], df_new_batch], ignore_index=True)
                    safe_write(conn, "EcolesConfig", df_upd)
                    st.cache_data.clear(); st.rerun()

                st.markdown("---")
                st.markdown("**2. Actions rapides**")
                ca1, ca2 = st.columns(2)
                with ca1:
                    if st.button(f"Tout {c_sel} à 'NON'", use_container_width=True, key="m_non"):
                        f_list = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                        new_rows = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Non", "Paiement": "-", "Services": "-"} for f in f_list]
                        df_upd = pd.concat([df_config[~df_config['Fase école'].isin(f_list)], pd.DataFrame(new_rows)], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()
                with ca2:
                    if st.button(f"Réinitialiser {c_sel} (Vide)", use_container_width=True, key="m_del"):
                        df_upd = df_config[df_config['Commune'] != c_sel]
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

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
                    if st.form_submit_button("💾 ENREGISTRER L'ÉCOLE", use_container_width=True):
                        new = pd.DataFrame([{"Fase école": e_fase, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != e_fase], new], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

    with col_r:
        # BLOCS STATS
        st.markdown(f"""
<div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center; margin-bottom:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui Utilisent l'Extrascolaire de Creos</div>
<div style="font-size:64px; font-weight:bold; line-height:1;">{len(df_active)}</div>
<div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
<div style="text-align:center;"><b style="font-size:22px; color:#ec4899; font-weight:900;">{len(df_active[df_active['Paiement']=='Prépaiement'])}</b><br><span style="font-size:22px;">Prépaiement</span></div>
<div style="text-align:center;"><b style="font-size:22px; color:#38bdf8; font-weight:900;">{len(df_active[df_active['Paiement']=='Post-paiement'])}</b><br><span style="font-size:22px;">Post-paiement</span></div>
<div style="text-align:center;"><b style="font-size:22px; color:#a78bfa; font-weight:900;">{len(active_communes)}</b><br><span style="font-size:22px;">Communes</span></div>
</div></div>
<div style="background-color:#FF43D0; padding:20px; border-radius:15px; color:white; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
<div style="font-size:16px; font-weight:bold; margin-bottom:10px;">Écoles qui n'utilisent pas l'Extrascolaire de Creos</div>
<div style="font-size:64px; font-weight:bold; line-height:1;">{len(df_refus)}</div>
<div style="display:flex; justify-content:center; border-top:1px solid rgba(255,255,255,0.2); margin-top:15px; padding-top:15px;">
<div style="text-align:center;"><b style="font-size:22px; font-weight:900;">{df_refus['Commune'].nunique()}</b><br><span style="font-size:22px;">Communes ont dit NON</span></div>
</div></div>""", unsafe_allow_html=True)

    # --- LISTE ---
    st.divider()
    view = st.radio("Afficher la liste :", ["✅ Écoles Utilisatrices", "❌ Écoles avec Refus"], horizontal=True)
    target = df_active if "Utilisatrices" in view else df_refus
    theme = "#008080" if "Utilisatrices" in view else "#FF43D0"
    fl_p = st.multiselect("Filtrer par Province", sorted(target['Province'].unique()), key="f_p_cfg_final")
    df_f = target.copy()
    if fl_p: df_f = df_f[df_f['Province'].isin(fl_p)]
    if not df_f.empty:
        df_f =
