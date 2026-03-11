import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(layout="wide", page_title="Creos Extrascolaire v4.0")

# Connexion
conn = st.connection("gsheets", type=GSheetsConnection)

# Chargement
df = conn.read(ttl=0).dropna(how="all")

# Interface
st.title("📂 Gestion Partagée - Creos Extrascolaire")

tab1, tab2 = st.tabs(["📊 Tableau de bord", "📝 Encodage & Edition"])

with tab2:
    st.subheader("Modifier une Commune")
    with st.form("form_edit"):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Nom de la commune")
            prov = st.selectbox("Province", ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"])
        with col_b:
            pay = st.radio("Type de paiement", ["Pre", "Post"])
            servs = st.multiselect("Services actifs", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
        
        if st.form_submit_button("Sauvegarder pour l'équipe"):
            # Logique de mise à jour du DataFrame
            new_row = pd.DataFrame([[name, prov, pay, "|".join(servs)]], columns=["Commune", "Province", "Paiement", "Services"])
            updated_df = pd.concat([df[df['Commune'] != name], new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"Données synchronisées pour {name}")
            st.rerun()

with tab1:
    # Filtres
    selected_prov = st.multiselect("Filtrer par Province", df['Province'].unique())
    filtered_df = df if not selected_prov else df[df['Province'].isin(selected_prov)]
    
    # Affichage façon "Badge"
    for _, row in filtered_df.iterrows():
        with st.expander(f"📍 {row['Commune']} ({row['Province']})"):
            c1, c2 = st.columns(2)
            c1.write(f"**Paiement:** {row['Paiement']}")
            # Transformation de la chaîne "A|B" en liste de badges
            badges = row['Services'].split('|') if isinstance(row['Services'], str) else []
            c2.write(f"**Services:** {' / '.join(badges)}")
