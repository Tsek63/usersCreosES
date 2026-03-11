import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos - Wallonie & Bruxelles")

# --- RÉFÉRENTIEL DES PROVINCES & COULEURS ---
PROV_COLORS = {
    "Bruxelles": "#FFCC00", 
    "Brabant Wallon": "#FF5733", 
    "Hainaut": "#C70039", 
    "Liège": "#900C3F", 
    "Namur": "#581845", 
    "Luxembourg": "#2E86C1"
}

# --- CHARGEMENT DES DONNÉES GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE SIMPLIFIÉE (EXEMPLE - À ÉTENDRE) ---
# En pratique, vous pouvez importer ici un CSV contenant les 281 communes
if 'all_communes' not in st.session_state:
    # Liste abrégée pour l'exemple, à remplir avec les 281 noms
    st.session_state.all_communes = sorted([
        "Oreye", "Namur", "Liège", "Mons", "Arlon", "Wavre", "Bruxelles", "Schaerbeek", 
        "Anderlecht", "Charleroi", "Tournai", "Huy", "Verviers", "Gembloux", "Ottignies",
        "Chaudfontaine", "Nivelles", "Dinant", "Bastogne", "Marche-en-Famenne"
    ])

# --- INTERFACE (30% / 70%) ---
col_sidebar, col_main = st.columns([0.3, 0.7])

with col_sidebar:
    st.header("🔍 Communes")
    search = st.text_input("Rechercher...", placeholder="Nom de la commune").strip()
    
    # Filtrage de la liste
    display_list = st.session_state.all_communes
    if search:
        display_list = [c for c in display_list if search.lower() in c.lower()]

    st.markdown("---")
    
    # AFFICHAGE DE LA GRILLE
    # On utilise un container avec scroll pour ne pas allonger la page à l'infini
    with st.container(height=600):
        grid_cols = st.columns(3) # 3 colonnes pour le 30% de largeur
        for i, com in enumerate(display_list):
            # Vérifier si déjà en DB
            data_com = df_db[df_db['Commune'] == com]
            is_done = not data_com.empty
            
            # Style du bouton : Coloré si fait, gris si vide
            btn_label = f"📍 {com}" if is_done else com
            
            with grid_cols[i % 3]:
                if st.button(btn_label, key=f"btn_{com}", use_container_width=True):
                    st.session_state.active_com = com
                    st.rerun()

with col_main:
    st.header("📝 Fiche d'Encodage")
    
    target = st.session_state.get('active_com')
    
    if target:
        # Récupération des infos existantes
        existing = df_db[df_db['Commune'] == target]
        
        with st.container(border=True):
            st.title(f"📍 {target}")
            
            with st.form("form_val"):
                c1, c2 = st.columns(2)
                
                # Valeurs par défaut
                d_prov = existing['Province'].iloc[0] if not existing.empty else "Liège"
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_prov = st.selectbox("Province", list(PROV_COLORS.keys()), index=list(PROV_COLORS.keys()).index(d_prov))
                    new_pay = st.radio("Méthode de Paiement", ["Pre", "Post"], index=0 if d_pay == "Pre" else 1, horizontal=True)
                
                with c2:
                    new_serv = st.multiselect("Services Activés", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)

                st.markdown("### Soumission")
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.form_submit_button("✅ VALIDER L'ENCODAGE", use_container_width=True):
                        # Préparation des données
                        new_row = pd.DataFrame([[target, new_prov, new_pay, "|".join(new_serv)]], 
                                             columns=["Commune", "Province", "Paiement", "Services"])
                        # Fusion avec la DB existante (remplace l'ancienne ligne)
                        updated_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                        
                        # Envoi vers Google Sheets
                        conn.update(data=updated_df)
                        st.success(f"Données pour {target} enregistrées avec succès !")
                        st.rerun()
                
                with col_cancel:
                    if st.form_submit_button("❌ FERMER", use_container_width=True):
                        st.session_state.active_com = None
                        st.rerun()
    else:
        st.info("Sélectionnez une commune dans la liste à gauche pour commencer l'encodage.")
        
    # Petit récapitulatif visuel en bas
    if not df_db.empty:
        st.divider()
        st.subheader("📊 État d'avancement")
        progression = (len(df_db) / 281) * 100
        st.progress(len(df_db) / 281, text=f"{len(df_db)} communes sur 281 ({progression:.1f}%)")
