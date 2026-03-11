import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos - Dashboard Wallonie-Bruxelles")

# --- RÉFÉRENTIEL DES PROVINCES & COULEURS ---
PROV_COLORS = {
    "Bruxelles": "#FFCC00", 
    "Brabant Wallon": "#FF5733", 
    "Hainaut": "#C70039", 
    "Liège": "#900C3F", 
    "Namur": "#581845", 
    "Luxembourg": "#2E86C1"
}

# --- CHARGEMENT DES DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Simulation de la liste complète (Wallonie 262 + Bxl 19 = 281)
# Pour l'exemple, j'utilise une liste réduite, mais la logique s'adapte à 281
if 'all_data' not in st.session_state:
    # Ici, vous pourriez charger un CSV avec [Commune, Province]
    st.session_state.all_data = [
        {"name": "Oreye", "prov": "Liège"}, {"name": "Namur", "prov": "Namur"},
        {"name": "Liège", "prov": "Liège"}, {"name": "Mons", "prov": "Hainaut"},
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Wavre", "prov": "Brabant Wallon"},
        {"name": "Bruxelles", "prov": "Bruxelles"}, {"name": "Ixelles", "prov": "Bruxelles"},
        {"name": "Charleroi", "prov": "Hainaut"}, {"name": "Dinant", "prov": "Namur"}
    ]

# --- INTERFACE (30% / 70%) ---
col_sidebar, col_main = st.columns([0.35, 0.65])

with col_sidebar:
    st.title("🗺️ Vue d'ensemble")
    
    # --- LÉGENDE ---
    st.markdown("### Légende")
    cols_leg = st.columns(2)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        cols_leg[i % 2].markdown(f" <span style='color:{c}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.divider()

    # --- RECHERCHE ---
    search = st.text_input("🔍 Rechercher une commune...", "").strip().lower()

    # --- GRILLE DE CARRÉS ---
    st.markdown("### Communes (cliquez pour éditer)")
    
    # Filtrage
    display_list = [c for c in st.session_state.all_data if search in c['name'].lower()]
    
    # CSS pour les carrés
    st.markdown("""
        <style>
        div.stButton > button {
            height: 40px;
            width: 40px;
            border-radius: 4px;
            padding: 0;
            margin: 2px;
            border: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

    # Affichage de la grille (8 carrés par ligne)
    grid_cols = st.columns(8)
    for i, com in enumerate(display_list):
        # On vérifie si la commune est encodée
        is_done = com['name'] in df_db['Commune'].values
        color = PROV_COLORS[com['prov']] if is_done else "#F0F2F6" # Gris clair si vide
        
        with grid_cols[i % 8]:
            if st.button(" ", key=f"tile_{com['name']}", help=f"{com['name']} ({com['prov']})"):
                st.session_state.active_com = com['name']
                st.session_state.active_prov = com['prov']
                st.rerun()
            # Petit indicateur visuel sous le bouton si besoin
            st.markdown(f"<div style='background-color:{color}; height:5px; margin-top:-10px; border-radius:2px;'></div>", unsafe_allow_html=True)

with col_main:
    # --- STATISTIQUES ---
    st.header("📊 Statistiques en temps réel")
    s1, s2, s3 = st.columns(3)
    
    total_encodées = len(df_db)
    s1.metric("Communes traitées", f"{total_encodées} / 281")
    
    # Calcul des activités (on compte les services dans la colonne Services)
    if not df_db.empty:
        all_services = df_db['Services'].str.split('|').explode()
        s2.metric("Total Activités", len(all_services[all_services != ""]))
        s3.metric("Province la plus active", df_db['Province'].mode()[0] if not df_db['Province'].mode().empty else "-")
    
    st.divider()

    # --- FICHE D'ENCODAGE ---
    target = st.session_state.get('active_com')
    
    if target:
        existing = df_db[df_db['Commune'] == target]
        
        with st.container(border=True):
            st.subheader(f"📍 {target} ({st.session_state.active_prov})")
            
            with st.form("form_val"):
                c1, c2 = st.columns(2)
                
                # Valeurs par défaut
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_pay = st.radio("Méthode de Paiement", ["Pre", "Post"], index=0 if d_pay == "Pre" else 1, horizontal=True)
                
                with c2:
                    new_serv = st.multiselect("Services Activés", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)

                st.markdown("### Soumission")
                if st.form_submit_button("✅ ENREGISTRER L'ENCODAGE", use_container_width=True):
                    new_row = pd.DataFrame([[target, st.session_state.active_prov, new_pay, "|".join(new_serv)]], 
                                         columns=["Commune", "Province", "Paiement", "Services"])
                    updated_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"Données sauvegardées pour {target}")
                    st.rerun()
    else:
        st.info("Cliquez sur un carré à gauche pour ouvrir la fiche d'une commune.")
        
    # --- GRAPHIQUE DES ACTIVITÉS ---
    if not df_db.empty:
        st.subheader("Répartition des services")
        serv_counts = all_services[all_services != ""].value_counts()
        st.bar_chart(serv_counts)
