import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Creos - Gestion Communale")

# --- RÉFÉRENTIEL COULEURS ---
PROV_COLORS = {
    "Bruxelles": "#FFCC00", "Brabant Wallon": "#FF5733", 
    "Hainaut": "#C70039", "Liège": "#900C3F", 
    "Namur": "#581845", "Luxembourg": "#2E86C1"
}

# --- CHARGEMENT DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- INTERFACE 30/70 ---
col_sidebar, col_main = st.columns([0.3, 0.7])

with col_sidebar:
    st.header("🏢 Communes")
    
    # Barre de recherche
    search = st.text_input("Filtrer une commune...", placeholder="Tapez le nom...").strip()
    
    # Simulation de la base complète (Wallonie/Bxl)
    # Note : Idéalement, on charge une liste de toutes les communes belges ici
    all_communes = sorted(["Oreye", "Namur", "Liège", "Mons", "Arlon", "Wavre", "Bruxelles", "Charleroi", "Tournai", "Eupen", "Huy", "Verviers", "Gembloux", "Ottignies"]) # À compléter
    
    if search:
        all_communes = [c for c in all_communes if search.lower() in c.lower()]

    st.write("---")
    
    # GRILLE DE TUILES (Hexagones/Carrés)
    # On crée une grille de 4 colonnes
    grid_cols = st.columns(4)
    selected_from_grid = None
    
    for i, com in enumerate(all_communes):
        # On vérifie si la commune est déjà dans la Google Sheet
        row_data = df_db[df_db['Commune'] == com]
        is_encoded = not row_data.empty
        
        # Couleur : Province si encodé, sinon gris
        bg_color = PROV_COLORS.get(row_data['Province'].iloc[0], "#E0E0E0") if is_encoded else "#E0E0E0"
        text_color = "white" if is_encoded else "black"
        
        with grid_cols[i % 4]:
            # Utilisation de boutons stylisés
            if st.button(com, key=f"btn_{com}", use_container_width=True, 
                         help=f"Cliquer pour gérer {com}"):
                st.session_state.active_com = com

with col_main:
    st.header("📝 Fiche d'encodage")
    
    target = st.session_state.get('active_com')
    
    if target:
        # Récupération des données existantes
        existing = df_db[df_db['Commune'] == target]
        
        with st.container(border=True):
            st.subheader(f"Commune : {target}")
            
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                
                # Pré-remplissage si déjà en base
                val_prov = existing['Province'].iloc[0] if not existing.empty else "Liège"
                val_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                val_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_prov = st.selectbox("Province", list(PROV_COLORS.keys()), index=list(PROV_COLORS.keys()).index(val_prov))
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if val_pay == "Pre" else 1, horizontal=True)
                
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=val_serv)

                st.divider()
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("✅ VALIDER & ENREGISTRER", use_container_width=True):
                        # Logique de sauvegarde
                        new_data = pd.DataFrame([[target, new_prov, new_pay, "|".join(new_serv)]], 
                                              columns=["Commune", "Province", "Paiement", "Services"])
                        df_final = pd.concat([df_db[df_db['Commune'] != target], new_data], ignore_index=True)
                        conn.update(data=df_final)
                        st.success(f"Enregistré : {target} est maintenant à jour.")
                        st.rerun()
                
                with col_btn2:
                    if st.form_submit_button("❌ ANNULER", use_container_width=True):
                        st.session_state.active_com = None
                        st.rerun()
    else:
        st.info("Sélectionnez une commune dans la grille à gauche pour ouvrir sa fiche d'encodage.")

    # Affichage rapide de la DB en dessous
    if not df_db.empty:
        with st.expander("Voir la base de données globale"):
            st.dataframe(df_db, use_container_width=True)
