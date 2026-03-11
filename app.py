import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- STYLE CSS (Carrés et Badges) ---
st.markdown("""
    <style>
    /* Carrés de la carte */
    div.stButton > button {
        height: 15px !important; width: 15px !important; min-width: 15px !important;
        padding: 0px !important; margin: 1px !important; border: none !important; border-radius: 2px;
    }
    /* Style des badges dans la liste */
    .badge { padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; color: white; margin-right: 4px; }
    .bg-pre { background-color: #4e73df; }
    .bg-post { background-color: #1cc88a; }
    .bg-service { background-color: #36b9cc; }
    </style>
""", unsafe_allow_html=True)

# --- COULEURS PROVINCES ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1", "Brabant Wallon": "#A9F1EB", "Hainaut": "#C8B6FF",
    "Liège": "#9AE8FF", "Namur": "#FFCCB6", "Luxembourg": "#FF85F3"
}

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# (La liste all_communes doit contenir vos 281 communes comme précédemment)
# Pour le test, je simule la fonction get_full_list()
from data_list import get_full_list 
all_communes = get_full_list()

# --- LOGIQUE DE POP-UP (Dialog) ---
@st.dialog("Configuration de la commune")
def edit_commune(name, prov):
    existing = df_db[df_db['Commune'] == name]
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pré-paiement"
    d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []
    
    st.subheader(f"📍 {name}")
    st.write(f"Province : {prov}")
    
    pay = st.radio("Paiement", ["Pré-paiement", "Post-paiement"], index=0 if d_pay == "Pré-paiement" else 1)
    serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)
    
    col1, col2 = st.columns(2)
    if col1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(serv)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if col2.button("ANNULER", use_container_width=True):
        st.rerun()

# --- INTERFACE PRINCIPALE ---
col_left, col_right = st.columns([0.4, 0.6])

# --- GAUCHE : LA CARTE ---
with col_left:
    st.subheader("🗺️ Carte")
    # On définit des zones pour placer les provinces "géographiquement"
    zones = {
        "Haut": ["Bruxelles", "Brabant Wallon"],
        "Milieu": ["Hainaut", "Namur", "Liège"],
        "Bas": ["Luxembourg"]
    }
    
    for zone, provs in zones.items():
        cols_zone = st.columns(len(provs))
        for i, p_name in enumerate(provs):
            with cols_zone[i]:
                st.caption(p_name)
                coms = [c for c in all_communes if c['prov'] == p_name]
                inner_cols = st.columns(6) # Grille de 6 carrés de large
                for idx, com in enumerate(coms):
                    btn_key = f"map_{com['name']}_{p_name}"
                    with inner_cols[idx % 6]:
                        if st.button(" ", key=btn_key):
                            edit_commune(com['name'], p_name)
                        st.markdown(f"<style>button[key='{btn_key}'] {{ background-color: {PROV_COLORS[p_name]} !important; }}</style>", unsafe_allow_html=True)

# --- DROITE : GESTION ET FILTRES ---
with col_right:
    st.subheader("Utilisateurs Creos Extrascolaire")
    
    # Barre de recherche et Filtres
    search = st.text_input("🔍 Chercher une commune...", label_visibility="collapsed")
    f_col1, f_col2, f_col3 = st.columns(3)
    f_prov = f_col1.selectbox("Toutes les Provinces", ["Toutes"] + list(PROV_COLORS.keys()))
    f_pay = f_col2.selectbox("Paiements", ["Tous", "Pré-paiement", "Post-paiement"])
    f_serv = f_col3.selectbox("Services", ["Tous", "Cantine", "Garderie", "Activités"])

    # Filtrage du DataFrame
    display_df = df_db.copy()
    if search: display_df = display_df[display_df['Commune'].str.contains(search, case=False)]
    if f_prov != "Toutes": display_df = display_df[display_df['Province'] == f_prov]
    if f_pay != "Tous": display_df = display_df[display_df['Paiement'] == f_pay]
    if f_serv != "Tous": display_df = display_df[display_df['Services'].str.contains(f_serv, case=False)]

    # Affichage façon Liste (Image 2)
    for prov in (list(PROV_COLORS.keys()) if f_prov == "Toutes" else [f_prov]):
        prov_data = display_df[display_df['Province'] == prov].sort_values("Commune")
        if not prov_data.empty:
            st.markdown(f"#### :blue[{prov.upper()}]")
            for _, row in prov_data.iterrows():
                c1, c2, c3 = st.columns([0.3, 0.2, 0.5])
                c1.write(f"**{row['Commune']}**")
                
                # Badge Paiement
                pay_class = "bg-pre" if row['Paiement'] == "Pré-paiement" else "bg-post"
                c2.markdown(f'<span class="badge {pay_class}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                # Badges Services
                servs = row['Services'].split('|')
                serv_html = "".join([f'<span class="badge bg-service">{s}</span>' for s in servs if s])
                c3.markdown(serv_html, unsafe_allow_html=True)
            st.divider()
