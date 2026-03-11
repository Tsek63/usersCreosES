import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos - Dashboard")

# --- RÉFÉRENTIEL ---
PROV_COLORS = {
    "Bruxelles": "#FFCC00", 
    "Brabant Wallon": "#FF5733", 
    "Hainaut": "#C70039", 
    "Liège": "#900C3F", 
    "Namur": "#581845", 
    "Luxembourg": "#2E86C1"
}
COLOR_DONE = "#00FF00" # Vert Fluo pour les communes validées

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Liste de référence (Extrait - à compléter avec les 281)
if 'all_data' not in st.session_state:
    st.session_state.all_data = [
        {"name": "Oreye", "prov": "Liège"}, {"name": "Namur", "prov": "Namur"},
        {"name": "Liège", "prov": "Liège"}, {"name": "Mons", "prov": "Hainaut"},
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Wavre", "prov": "Brabant Wallon"},
        {"name": "Bruxelles", "prov": "Bruxelles"}, {"name": "Ixelles", "prov": "Bruxelles"}
        # Ajoutez les autres ici...
    ]

# --- INTERFACE (35% / 65%) ---
col_sidebar, col_main = st.columns([0.35, 0.65])

with col_sidebar:
    st.title("🗺️ État d'avancement")
    
    # Légende
    st.markdown("**Légende des Provinces**")
    cols_leg = st.columns(3)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        cols_leg[i % 3].markdown(f"<span style='color:{c};'>■</span> {p}", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{COLOR_DONE};'>■</span> **Terminé**", unsafe_allow_html=True)
    
    st.divider()
    search = st.text_input("🔍 Rechercher une commune...", "").strip().lower()

    # Grille de carrés
    st.markdown("""<style> div.stButton > button { height: 35px; width: 35px; border-radius: 4px; margin: 1px; } </style>""", unsafe_allow_html=True)
    
    display_list = [c for c in st.session_state.all_data if search in c['name'].lower()]
    grid_cols = st.columns(7)
    
    for i, com in enumerate(display_list):
        is_done = com['name'] in df_db['Commune'].values
        # Couleur : Vert Fluo si fait, sinon couleur Province
        tile_color = COLOR_DONE if is_done else PROV_COLORS.get(com['prov'], "#EEE")
        
        with grid_cols[i % 7]:
            if st.button(" ", key=f"t_{com['name']}", help=f"{com['name']} ({com['prov']})"):
                st.session_state.active_com = com['name']
                st.session_state.active_prov = com['prov']
                st.rerun()
            # On dessine le carré de couleur
            st.markdown(f"<div style='background-color:{tile_color}; height:8px; margin-top:-12px;'></div>", unsafe_allow_html=True)

with col_main:
    # --- STATISTIQUES ---
    st.header("📊 Statistiques Globales")
    s1, s2, s3 = st.columns(3)
    
    total_communes = 281
    encodées = len(df_db)
    s1.metric("Communes", f"{encodées} / {total_communes}", f"{int((encodées/total_communes)*100)}%")
    
    if not df_db.empty:
        serv_series = df_db['Services'].str.split('|').explode()
        s2.metric("Services Actifs", len(serv_series[serv_series != ""]))
        s3.metric("Dernier ajout", df_db['Commune'].iloc[-1])
    
    st.divider()

    # --- ENCODAGE ---
    target = st.session_state.get('active_com')
    # Correction de l'erreur : on récupère la province depuis la DB ou la session
    target_prov = st.session_state.get('active_prov', "Inconnue")

    if target:
        existing = df_db[df_db['Commune'] == target]
        with st.container(border=True):
            st.subheader(f"📍 {target} ({target_prov})")
            with st.form("form_val"):
                c1, c2 = st.columns(2)
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if d_pay == "Pre" else 1)
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)

                if st.form_submit_button("✅ VALIDER & ENREGISTRER"):
                    new_row = pd.DataFrame([[target, target_prov, new_pay, "|".join(new_serv)]], 
                                         columns=["Commune", "Province", "Paiement", "Services"])
                    updated_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.toast("Données synchronisées !")
                    st.rerun()
    else:
        st.info("Sélectionnez une commune à gauche pour l'encoder.")

    # Graphique
    if not df_db.empty:
        st.subheader("Répartition des activités")
        st.bar_chart(df_db['Services'].str.split('|').explode().value_counts())
