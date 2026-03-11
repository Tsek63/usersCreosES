import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# Couleurs par province
PROV_COLORS = {
    "Bruxelles": "#FFCC00",      # Jaune
    "Brabant Wallon": "#FF5733", # Orange/Rouge
    "Hainaut": "#C70039",       # Rouge foncé
    "Liège": "#900C3F",         # Bordeaux
    "Namur": "#581845",         # Violet
    "Luxembourg": "#2E86C1"      # Bleu
}

# --- CONNEXION & DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

# --- INTERFACE (30/70) ---
col_sidebar, col_main = st.columns([0.3, 0.7])

with col_sidebar:
    st.header("🔍 Recherche")
    search_query = st.text_input("Rechercher une commune...", placeholder="Ex: Oreye, Namur...").strip().lower()
    
    st.divider()
    
    # On affiche la grille ici ou en dessous ? 
    # Pour respecter votre demande, la grille est à gauche sous la recherche
    st.subheader("📍 Carte des Communes")
    
    # Création d'une grille de tuiles
    if not df.empty:
        # On filtre si recherche
        grid_df = df.copy()
        if search_query:
            grid_df = grid_df[grid_df['Commune'].str.lower().contains(search_query)]
        
        # Affichage en petites tuiles carrées
        cols_grid = st.columns(5) # 5 tuiles par ligne
        for idx, row in grid_df.iterrows():
            with cols_grid[idx % 5]:
                color = PROV_COLORS.get(row['Province'], "#ddd")
                # Un bouton stylisé pour simuler la tuile
                if st.button(f"■", key=f"btn_{row['Commune']}", help=row['Commune']):
                    st.session_state.selected_commune = row['Commune']
                    st.rerun()
                st.caption(row['Commune'][:8]) # Affiche un nom court sous la tuile

with col_main:
    st.header("⚙️ Configuration & Services")
    
    # Si une recherche est en cours, on propose de l'ajouter si elle n'existe pas
    target_commune = search_query.capitalize() if search_query else st.session_state.get('selected_commune', None)
    
    if target_commune:
        # Chercher si la commune existe déjà
        existing_data = df[df['Commune'] == target_commune]
        
        with st.container(border=True):
            st.subheader(f"Commune : {target_commune}")
            
            with st.form("form_update"):
                c1, c2 = st.columns(2)
                
                # Valeurs par défaut si la commune existe déjà
                curr_prov = existing_data['Province'].iloc[0] if not existing_data.empty else "Liège"
                curr_pay = existing_data['Paiement'].iloc[0] if not existing_data.empty else "Pre"
                curr_serv = existing_data['Services'].iloc[0].split('|') if not existing_data.empty and isinstance(existing_data['Services'].iloc[0], str) else []

                with c1:
                    new_prov = st.selectbox("Province", list(PROV_COLORS.keys()), index=list(PROV_COLORS.keys()).index(curr_prov))
                    new_pay = st.radio("Type de Paiement", ["Pre", "Post"], index=0 if curr_pay == "Pre" else 1, horizontal=True)
                
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=curr_serv)

                submitted = st.form_submit_button("Enregistrer les modifications")
                
                if submitted:
                    # Mise à jour du DataFrame
                    new_row = pd.DataFrame([[target_commune, new_prov, new_pay, "|".join(new_serv)]], 
                                         columns=["Commune", "Province", "Paiement", "Services"])
                    
                    df_updated = pd.concat([df[df['Commune'] != target_commune], new_row], ignore_index=True)
                    conn.update(data=df_updated)
                    st.success(f"Données de {target_commune} synchronisées !")
                    st.rerun()
    else:
        st.info("Sélectionnez une commune dans la grille à gauche ou utilisez la barre de recherche pour commencer.")

    # Affichage récapitulatif en bas
    st.divider()
    st.subheader("📋 Liste globale")
    st.dataframe(df, use_container_width=True)
