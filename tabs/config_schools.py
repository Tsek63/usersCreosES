import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb):
    # BOUTON REFRESH EN HAUT À DROITE
    c_title, c_refresh = st.columns([0.85, 0.15])
    with c_refresh:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 1. PRÉPARATION ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    active_communes = set(df_active['Commune'].unique())
    df_refus = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # --- 2. MISE EN PAGE HAUT ---
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
            with st.expander(f"⚡ Actions groupées pour {c_sel}"):
                st.markdown("---")
                # ACTION 1 : SERVICES GROUPÉS
                st.markdown("**Appliquer les mêmes services à TOUTES les écoles actives du PO**")
                mass_svc = st.multiselect("Choisir les services", svc_list, key="mass_svc_sel")
                if st.button(f"Appliquer à tout {c_sel}", key="btn_mass_svc"):
                    # On ne modifie que les écoles déjà marquées à "Oui"
                    mask = (df_config['Commune'] == c_sel) & (df_config['Extrascolaire'] == 'Oui')
                    df_config.loc[mask, 'Services'] = "|".join(mass_svc)
                    safe_write(conn, "EcolesConfig", df_config)
                    st.cache_data.clear(); st.rerun()
                
                st.markdown("---")
                ca1, ca2 = st.columns(2)
                with ca1:
                    if st.button(f"Tout {c_sel} à 'NON'", key="mass_non"):
                        f_list = df_ecoles[df_ecoles['Commune'] == c_sel]['Fase école'].astype(str).unique()
                        new_rows = [{"Fase école": f, "Commune": c_sel, "Province": p_sel, "Extrascolaire": "Non", "Paiement": "-", "Services": "-"} for f in f_list]
                        df_upd = pd.concat([df_config[~df_config['Fase école'].isin(f_list)], pd.DataFrame(new_rows)], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()
                with ca2:
                    if st.button(f"Supprimer de la config", key="mass_del"):
                        df_upd = df_config[df_config['Commune'] != c_sel]
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

            # ... (Suite du code pour école individuelle identique au message précédent) ...
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
                    if st.form_submit_button("💾 ENREGISTRER"):
                        new = pd.DataFrame([{"Fase école": e_fase, "Commune": c_sel, "Province": p_sel, "Extrascolaire": v_ex, "Paiement": v_pa if v_ex == "Oui" else "-", "Services": "|".join(v_sv) if (v_ex == "Oui" and v_sv) else "-"}])
                        df_upd = pd.concat([df_config[df_config['Fase école'] != e_fase], new], ignore_index=True)
                        safe_write(conn, "EcolesConfig", df_upd); st.cache_data.clear(); st.rerun()

    with col_r:
        # On remet les blocs Stats (Teal/Fuchsia) ici
        # ... (Identiques à ta version précédente) ...
