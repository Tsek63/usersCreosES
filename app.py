import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- RÉFÉRENTIEL COULEURS (Style Pastel) ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1",      # Jaune
    "Brabant Wallon": "#A9F1EB", # Cyan
    "Hainaut": "#C8B6FF",       # Violet
    "Liège": "#9AE8FF",         # Bleu
    "Namur": "#FFCCB6",         # Corail
    "Luxembourg": "#FF85F3"      # Rose/Magenta
}

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE DES 281 COMMUNES ---
@st.cache_data
def get_full_list():
    # Liste simplifiée pour l'exemple, assurez-vous d'avoir vos 281 entrées ici
    # (Je garde la structure de votre liste complète précédente)
    return [
        # ... (Gardez ici la liste complète des 281 communes de l'étape précédente) ...
        # Assurez-vous que Musson est bien dans le Luxembourg et pas en doublon.
    ]

all_communes = get_full_list()

# --- CSS POUR LES PETITS CARRÉS (20px) ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 20px !important;
        width: 20px !important;
        min-width: 20px !important;
        border-radius: 3px;
        padding: 0px !important;
        margin: 1px !important;
        border: none !important;
    }
    /* Aligner les colonnes de carrés */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- LAYOUT : 40% CARTE / 60% FORMULAIRE ---
col_map, col_form = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte Interactive")
    
    # Organisation schématique des provinces (Nord au Sud, Ouest à Est)
    # Rang 1 : Bruxelles + BW
    r1_1, r1_2 = st.columns(2)
    
    # Rang 2 : Hainaut + Namur + Liège
    r2_1, r2_2, r2_3 = st.columns(3)
    
    # Rang 3 : Luxembourg
    r3_1, r3_2, r3_3 = st.columns(3)

    def draw_province(container, prov_name, nb_cols=5):
        coms = [c for c in all_communes if c['prov'] == prov_name]
        container.caption(f"**{prov_name}**")
        grid = container.columns(nb_cols)
        for i, com in enumerate(coms):
            with grid[i % nb_cols]:
                safe_key = f"btn_{com['name']}_{prov_name}".replace(" ", "_")
                if st.button(" ", key=safe_key, help=f"{com['name']}"):
                    st.session_state.active_com = com['name']
                    st.session_state.active_prov = prov_name
                # Couleur dynamique
                st.markdown(f"<style>button[key='{safe_key}'] {{ background-color: {PROV_COLORS[prov_name]} !important; }}</style>", unsafe_allow_html=True)

    # Placement géographique
    with r1_1: draw_province(st, "Bruxelles", 5)
    with r1_2: draw_province(st, "Brabant Wallon", 5)
    with r2_1: draw_province(st, "Hainaut", 7)
    with r2_2: draw_province(st, "Namur", 6)
    with r2_3: draw_province(st, "Liège", 8)
    with r3_3: draw_province(st, "Luxembourg", 7)

with col_form:
    st.subheader("📝 Détails de l'encode")
    
    target = st.session_state.get('active_com')
    t_prov = st.session_state.get('active_prov')

    if target:
        existing = df_db[df_db['Commune'] == target]
        with st.container(border=True):
            st.title(f"📍 {target}")
            st.write(f"Province de {t_prov}")
            
            with st.form("f_save"):
                c1, c2 = st.columns(2)
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []
                
                with c1:
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if d_pay=="Pre" else 1)
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)
                
                if st.form_submit_button("SAUVEGARDER", use_container_width=True):
                    new_row = pd.DataFrame([[target, t_prov, new_pay, "|".join(new_serv)]], columns=["Commune", "Province", "Paiement", "Services"])
                    up_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=up_df)
                    st.success("Données enregistrées !")
                    st.rerun()
    else:
        st.info("Cliquez sur un carré de couleur à gauche pour commencer.")

    # Barre de recherche et Export en bas à droite
    st.divider()
    search = st.text_input("🔍 Rechercher une commune spécifique")
    if search:
        match = [c for c in all_communes if search.lower() in c['name'].lower()]
        if match:
            st.write(f"Résultat : **{match[0]['name']}** ({match[0]['prov']})")
            if st.button(f"Éditer {match[0]['name']}"):
                st.session_state.active_com = match[0]['name']
                st.session_state.active_prov = match[0]['prov']
                st.rerun()

    if not df_db.empty:
        csv = df_db.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger le CSV", csv, "export_creos.csv", use_container_width=True)
