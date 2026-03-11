import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION STANDARD ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Couleurs pour la légende
PROV_COLORS = {
    "Bruxelles": "🟡", "Brabant Wallon": "🔵", "Hainaut": "🟣",
    "Liège": "🟢", "Namur": "🟠", "Luxembourg": "🔴"
}

# Fonctions pour les filtres (Évite les erreurs de crash)
if "search_input" not in st.session_state:
    st.session_state.search_input = ""

def clear_filters():
    st.session_state.search_input = ""

# --- INTERFACE ---
st.title("👥 Gestion des Utilisateurs Creos")

# BARRE DE FILTRES SIMPLE (Alignée automatiquement par Streamlit)
col_search, col_prov, col_clear = st.columns([2, 1, 0.5])

with col_search:
    search_query = st.text_input("Rechercher une commune", key="search_input")

with col_prov:
    prov_filter = st.selectbox("Filtrer par Province", ["Toutes"] + list(PROV_COLORS.keys()))

with col_clear:
    # Le bouton est naturellement aligné car il y a un label vide au-dessus
    st.write("") 
    st.button("Effacer", on_click=clear_filters, use_container_width=True)

st.divider()

# --- AFFICHAGE ---
c1, c2 = st.columns([0.4, 0.6])

with c1:
    st.subheader("📍 Légende")
    for prov, emoji in PROV_COLORS.items():
        st.write(f"{emoji} **{prov}**")
    
    st.info("La carte détaillée sera réintégrée une fois l'affichage stabilisé.")

with c2:
    st.subheader("📋 Liste des Communes")
    
    # Filtrage simple
    df_f = df_db.copy()
    if search_query:
        df_f = df_f[df_f['Commune'].str.contains(search_query, case=False, na=False)]
    if prov_filter != "Toutes":
        df_f = df_f[df_f['Province'] == prov_filter]

    if df_f.empty:
        st.warning("Aucun résultat trouvé.")
    else:
        # Tableau standard ultra-lisible
        st.dataframe(
            df_f[['Commune', 'Province', 'Paiement', 'Services']], 
            use_container_width=True,
            hide_index=True
        )

# --- BOUTON D'ACTION ---
if not df_f.empty:
    st.write("---")
    st.caption("Sélectionnez une ligne dans le tableau pour voir les détails (Optionnel)")
