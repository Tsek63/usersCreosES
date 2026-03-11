import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json

# --- CONFIGURATION PAGE ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire v4.0")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl=0)
        # Nettoyage des données vides
        df = df.dropna(subset=['Commune'])
        return df
    except:
        return pd.DataFrame(columns=['Commune', 'Province', 'Paiement', 'Services'])

# --- LOGIQUE DE MISE À JOUR ---
def update_commune(commune_name, province, pay, services_list):
    df = load_data()
    services_str = "|".join(services_list)
    
    new_row = pd.DataFrame([{
        "Commune": commune_name,
        "Province": province,
        "Paiement": pay,
        "Services": services_str
    }])
    
    # Supprimer l'ancienne entrée si elle existe
    df = df[df['Commune'] != commune_name]
    # Ajouter la nouvelle
    df = pd.concat([df, new_row], ignore_index=True)
    
    conn.update(data=df)
    st.toast(f"✅ {commune_name} mis à jour dans Google Sheets !")

# --- CHARGEMENT INITIAL ---
df_data = load_data()
# Conversion pour le JS (carte SVG)
selected_dict = {}
for _, row in df_data.iterrows():
    selected_dict[row['Commune']] = {
        "prov": row['Province'],
        "pay": row['Paiement'],
        "services": str(row['Services']).split('|') if row['Services'] else []
    }

# --- INTERFACE STREAMLIT (PANEL DE GAUCHE) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=CREOS+LOGO") # Remplacez par votre logo
    st.title("Configuration")
    
    with st.expander("➕ Ajouter/Modifier une commune", expanded=True):
        with st.form("edit_form"):
            c_name = st.text_input("Nom de la commune")
            c_prov = st.selectbox("Province", ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"])
            c_pay = st.radio("Paiement", ["Pre", "Post"], format_func=lambda x: "Prépaiement" if x=="Pre" else "Post-paiement")
            c_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            
            submit = st.form_submit_button("Enregistrer dans le Cloud")
            if submit and c_name:
                update_commune(c_name, c_prov, c_pay, c_serv)
                st.rerun()

    if st.button("🗑️ Vider la base de données"):
        if st.checkbox("Confirmer la suppression totale"):
            conn.update(data=pd.DataFrame(columns=['Commune', 'Province', 'Paiement', 'Services']))
            st.rerun()

# --- AFFICHAGE PRINCIPAL (CARTE & LISTE) ---
# Ici on réutilise votre CSS et votre SVG original pour ne pas changer vos habitudes
st.markdown(f"""
<style>
    {open('style.css', 'r').read() if 'style.css' in locals() else "/* Insérez votre CSS ici */"}
    .commune {{ stroke: #fff; stroke-width: 0.8; fill: #e2e8f0; }}
    .active {{ stroke: #000; stroke-width: 2px; }}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Statistiques & Carte")
    st.write(f"Total actifs : **{len(df_data)}**")
    # Note: Pour une interactivité totale sur la carte SVG dans Streamlit, 
    # on utilise le panel de gauche pour l'encodage et la liste pour le visuel.
    st.info("Utilisez le formulaire à gauche pour mettre à jour les données.")

with col2:
    st.subheader("Liste des encodages partagés")
    # Filtres Streamlit natifs (plus rapides)
    f_prov = st.multiselect("Filtrer par Province", df_data['Province'].unique())
    
    display_df = df_data.copy()
    if f_prov:
        display_df = display_df[display_df['Province'].isin(f_prov)]
    
    st.dataframe(display_df, use_container_width=True)
