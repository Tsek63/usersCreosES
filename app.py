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

# --- STYLE & CARTE ---
st.markdown("""
<style>
    .province-box {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        cursor: pointer;
    }
    .province-box:hover { background-color: #f0f2f6; }
    .stBadge { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# Création des colonnes pour l'affichage
col_map, col_details = st.columns([1, 1])

with col_map:
    st.subheader("📍 Sélection par Province")
    # On crée des boutons stylisés pour simuler le clic sur la carte par province
    provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"]
    
    # On utilise des boutons pour filtrer
    selected_p = None
    for p in provinces:
        count = len(df[df['Province'] == p])
        if st.button(f"{p} ({count} communes)", key=p, use_container_width=True):
            selected_p = p

with col_details:
    st.subheader("🔍 Détails")
    if selected_p:
        st.write(f"Communes encodées en **{selected_p}** :")
        sub_df = df[df['Province'] == selected_p]
        
        if sub_df.empty:
            st.info("Aucune commune encodées pour cette province.")
        else:
            for _, row in sub_df.iterrows():
                with st.expander(f"🏙️ {row['Commune']}"):
                    st.write(f"**Paiement :** {row['Paiement']}")
                    servs = row['Services'].split('|') if row['Services'] else []
                    st.write(f"**Services :** {', '.join(servs)}")
    else:
        st.info("Cliquez sur une province à gauche pour voir les détails.")
