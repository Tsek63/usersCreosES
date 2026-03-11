import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS COMPLET ---
st.markdown("""
    <style>
    /* Carte : Carrés de 16px colorés */
    .stButton > button {
        border: none !important;
        height: 16px !important;
        width: 16px !important;
        min-width: 16px !important;
        padding: 0 !important;
        margin: 1px !important;
        border-radius: 3px !important;
    }
    /* Couleurs de fond forcées pour la carte */
    button[kind="secondary"] { background-color: #f0f2f6; } /* fallback */
    
    /* Badges de la liste de droite */
    .badge { padding: 3px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; color: white; margin-right: 4px; display: inline-block; }
    .bg-pre { background-color: #4A90E2; }
    .bg-post { background-color: #2ECC71; }
    .bg-service { background-color: #F39C12; }
    .prov-label { font-size: 14px; font-weight: bold; color: #1f4e79; margin-top: 15px; border-bottom: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION COULEURS & DATA ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1", "Brabant Wallon": "#A9F1EB", "Hainaut": "#C8B6FF",
    "Liège": "#9AE8FF", "Namur": "#FFCCB6", "Luxembourg": "#FF85F3"
}

conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Récupération de la liste complète (Assurez-vous qu'elle contient les 281 communes)
# Importée ou définie ici
def get_full_list():
    # ... (Votre liste complète de communes ici) ...
    return [{"name": "Evere", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"}, 
            {"name": "Jodoigne", "prov": "Brabant Wallon"}, {"name": "Baelen", "prov": "Liège"}] # Exemple

all_communes = get_full_list()

# --- FONCTION POP-UP (Small Width) ---
@st.dialog("Configuration", width="small")
def edit_commune(name, prov):
    st.subheader(f":blue[{name}]")
    existing = df_db[df_db['Commune'] == name]
    
    # Valeurs par défaut
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pré-paiement"
    d_serv = str(existing['Services'].iloc[0]).split('|') if not existing.empty else []

    st.write("**Paiement**")
    pay = st.radio("Pay", ["Pré-paiement", "Post-paiement"], index=0 if d_pay == "Pré-paiement" else 1, horizontal=True, label_visibility="collapsed")
    
    st.write("**Services**")
    choices = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    serv = [c for c in choices if st.checkbox(c, value=(c in d_serv))]

    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    if c1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(serv)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if c2.button("ANNULER", use_container_width=True):
        st.rerun()
    if not existing.empty:
        if c3.button("🗑️", help="Supprimer l'encodage", use_container_width=True):
            up_df = df_db[df_db['Commune'] != name]
            conn.update(data=up_df)
            st.rerun()

# --- INTERFACE PRINCIPALE ---
col_map, col_list = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte Interactive")
    # Affichage groupé par province pour respecter la "forme" géographique
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<div style='font-size:12px; font-weight:bold; margin-top:10px;'>{prov}</div>", unsafe_allow_html=True)
        coms = [c for c in all_communes if c['prov'] == prov]
        grid = st.columns(10)
        for i, com in enumerate(coms):
            with grid[i % 10]:
                btn_id = f"m_{com['name']}".replace(" ", "_")
                if st.button(" ", key=btn_id):
                    edit_commune(com['name'], prov)
                # Injection CSS spécifique pour la couleur de CHAQUE bouton
                st.markdown(f"<style>button[key='{btn_id}'] {{ background-color: {color} !important; }}</style>", unsafe_allow_html=True)

with col_list:
    st.header("Utilisateurs Creos Extrascolaire")
    
    # --- FILTRES ---
    search = st.text_input("Rechercher une commune...", placeholder="Tapez le nom...")
    
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
    s_prov = f1.selectbox("Provinces", ["Toutes les Provinces"] + list(PROV_COLORS.keys()), key="f_prov")
    s_pay = f2.selectbox("Paiements", ["Tous", "Pré-paiement", "Post-paiement"], key="f_pay")
    s_serv = f3.selectbox("Services", ["Tous", "Cantine Jour", "Garderie", "Activités"], key="f_serv")
    
    if f4.button("Effacer filtres", style="margin-top:28px"):
        # Reset simple via rerun (ou on pourrait utiliser le session_state)
        st.rerun()

    # --- LOGIQUE FILTRAGE ---
    df_f = df_db.copy()
    if search: df_f = df_f[df_f['Commune'].str.contains(search, case=False)]
    if s_prov != "Toutes les Provinces": df_f = df_f[df_f['Province'] == s_prov]
    if s_pay != "Tous": df_f = df_f[df_f['Paiement'] == s_pay]
    if s_serv != "Tous": df_f = df_f[df_f['Services'].str.contains(s_serv, case=False)]

    # --- LISTE STYLE IMAGE 2 ---
    for p in (PROV_COLORS.keys() if s_prov == "Toutes les Provinces" else [s_prov]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<div class='prov-label'>{p.upper()}</div>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3 = st.columns([0.3, 0.2, 0.5])
                l1.markdown(f"**{row['Commune']}**")
                
                p_cls = "bg-pre" if row['Paiement'] == "Pré-paiement" else "bg-post"
                l2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                s_badges = "".join([f'<span class="badge bg-service">{s}</span>' for s in str(row['Services']).split('|') if s])
                l3.markdown(s_badges, unsafe_allow_html=True)
