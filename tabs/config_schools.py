import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb):
    st.header("⚙️ Gestion des Écoles par Commune")

    # --- 1. PRÉPARATION ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    active_communes = set(df_active['Commune'].unique())
    df_refus = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    svc_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]

    # --- 2. MISE EN PAGE HAUT ---
    col_l, col_r = st.columns([1.8, 1.2])

    with col_l:
        st.subheader("📝 Configurer une École ou une Commune")
        s1, s2, s3 = st.columns([1, 1, 1.5])
        with s1:
            p_sel = st.selectbox("1. Province", sorted(list(data_fwb.keys())), key="cfg_p")
        with s2:
            c_opts = sorted(data_fwb.get(p_sel, []))
            # ICÔNE DYNAMIQUE ICI AUSSI
            c_sel = st.selectbox(
                "2. Commune / PO", 
                ["— Sélectionnez —"] + c_opts, 
                format_func=lambda x: f"{'✅' if x in active_communes else '⚪'} {icon_po(x)} {x}" if x != "— Sélectionnez —" else x,
                key="cfg_c"
            )
        
        if c_sel != "— Sélectionnez —":
            # (Reste du formulaire, Expanders, et liste individuelle avec ✅/❌/⭕ restent identiques)
            # ... (Copiez le contenu que vous avez déjà dans ce fichier) ...
