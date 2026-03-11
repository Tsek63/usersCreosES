import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- RÉFÉRENTIEL COULEURS ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1", "Brabant Wallon": "#A9F1EB", "Hainaut": "#C8B6FF",
    "Liège": "#9AE8FF", "Namur": "#FFCCB6", "Luxembourg": "#FF85F3"
}

# --- INJECTION CSS CRITIQUE (Fond bleu, Carrés 14px, Texte noir) ---
st.markdown(f"""
    <style>
    /* Fond de l'application */
    .stApp {{ background-color: #EBF5FB !important; }}
    
    /* Global Text Color */
    h1, h2, h3, h4, p, span, label {{ color: #1B4F72 !important; }}

    /* CARTE : Carrés minuscules (14px) */
    div[data-testid="stColumn"] button {{
        height: 14px !important;
        width: 14px !important;
        min-width: 14px !important;
        max-width: 14px !important;
        padding: 0px !important;
        margin: 1px !important;
        border: 0.5px solid rgba(0,0,0,0.1) !important;
        border-radius: 2px !important;
    }}

    /* POP-UP : Fix Boutons Horizontaux */
    div[data-testid="stDialog"] button {{
        width: 100% !important;
        height: 40px !important;
        min-width: 120px !important;
        font-weight: bold !important;
    }}
    
    /* Badges Style */
    .badge {{ padding: 3px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; color: white; margin-right: 4px; display: inline-block; }}
    .bg-pre {{ background-color: #2E86C1; }}
    .bg-post {{ background-color: #28B463; }}
    .bg-service {{ background-color: #D68910; }}
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Génération des 281 communes (Liste abrégée pour le code, importez la vôtre ici)
@st.cache_data
def load_data():
    # Simulation des 281 communes (remplacez par votre dictionnaire complet)
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Evere", "Uccle", "Ixelles", "Jette"],
        "Brabant Wallon": ["Beauvechain", "Nivelles", "Wavre", "Jodoigne", "Waterloo"],
        "Hainaut": ["Mons", "Charleroi", "Ath", "Tournai", "Chimay", "La Louvière"],
        "Liège": ["Liège", "Baelen", "Spa", "Huy", "Verviers", "Waremme", "Eupen"],
        "Namur": ["Namur", "Dinant", "Ciney", "Andenne", "Gembloux"],
        "Luxembourg": ["Arlon", "Bastogne", "Marche", "Virton", "Bouillon"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_communes = load_data()

# --- POP-UP D'ENCODAGE ---
@st.dialog("Configuration", width="medium")
def edit_commune(name, prov):
    st.markdown(f"## 📍 {name}")
    existing = df_db[df_db['Commune'] == name]
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pré-paiement"
    d_serv = str(existing['Services'].iloc[0]).split('|') if not existing.empty else []

    pay = st.radio("Mode de paiement", ["Pré-paiement", "Post-paiement"], index=0 if d_pay == "Pré-paiement" else 1, horizontal=True)
    st.write("**Services :**")
    choices = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    serv = [c for c in choices if st.checkbox(c, value=(c in d_serv))]

    st.divider()
    c1, c2, c3 = st.columns([1, 1, 0.5])
    if c1.button("✅ VALIDER", type="primary"):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(serv)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if c2.button("❌ ANNULER"):
        st.rerun()
    if not existing.empty:
        if c3.button("🗑️"):
            conn.update(data=df_db[df_db['Commune'] != name])
            st.rerun()

# --- LAYOUT ---
col_map, col_list = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte Interactive")
    
    # LÉGENDE
    st.markdown("---")
    leg = st.columns(3)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        leg[i % 3].markdown(f"<span style='color:{c}; font-size:20px;'>■</span> <small>{p}</small>", unsafe_allow_html=True)
    st.markdown("---")

    # GRILLE DE COMMUNES
    for prov, color in PROV_COLORS.items():
        st.write(f"**{prov}**")
        coms = [c for c in all_communes if c['prov'] == prov]
        grid = st.columns(15) # 15 carrés par ligne pour réduire la taille
        for i, com in enumerate(coms):
            btn_id = f"m_{com['name']}".replace(" ", "_")
            with grid[i % 15]:
                if st.button(" ", key=btn_id, help=com['name']):
                    edit_commune(com['name'], prov)
                st.markdown(f"<style>button[key='{btn_id}'] {{ background-color: {color} !important; }}</style>", unsafe_allow_html=True)

with col_list:
    st.title("Utilisateurs Creos Extrascolaire")
    
    # Filtres
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
    s_prov = f1.selectbox("Provinces", ["Toutes"] + list(PROV_COLORS.keys()))
    s_pay = f2.selectbox("Paiement", ["Tous", "Pré-paiement", "Post-paiement"])
    s_serv = f3.selectbox("Services", ["Tous", "Cantine", "Garderie", "Activités"])
    if f4.button("Effacer"): st.rerun()

    # Affichage Liste
    df_f = df_db.copy()
    if s_prov != "Toutes": df_f = df_f[df_f['Province'] == s_prov]
    
    for p in (PROV_COLORS.keys() if s_prov == "Toutes" else [s_prov]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h3 style='color:#2874A6; border-bottom:1px solid #AED6F1;'>{p.upper()}</h3>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f'<span class="badge {"bg-pre" if row["Paiement"]=="Pré-paiement" else "bg-post"}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                badges = "".join([f'<span class="badge bg-service">{s}</span>' for s in str(row['Services']).split('|') if s])
                l3.markdown(badges, unsafe_allow_html=True)
                if l4.button("📝", key=f"ed_{row['Commune']}"):
                    edit_commune(row['Commune'], p)
