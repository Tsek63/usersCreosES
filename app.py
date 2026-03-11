import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS RADICAL POUR TOUT VERROUILLER ---
st.markdown("""
    <style>
    /* Fond de page et suppression des textes fantômes */
    .stApp { background-color: #E3F2FD !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* FILTRES : Bleu foncé, texte blanc, alignés */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        border: 1px solid #BEE3F8 !important;
        height: 42px !important;
    }
    input { color: white !important; -webkit-text-fill-color: white !important; }
    div[data-baseweb="select"] span { color: white !important; }

    /* CARTE : Points de couleur sans rectangles noirs */
    .city-dot {
        height: 14px; width: 14px;
        border-radius: 3px;
        display: inline-block;
        margin: 2px;
        border: 1px solid rgba(0,0,0,0.1);
        cursor: help;
    }
    
    /* BOUTONS */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 42px !important;
        border-radius: 6px !important;
    }

    /* BADGES LISIBLES */
    .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; color: #003366 !important; }
    .bg-pre { background-color: #A9D0F5; } 
    .bg-cantine { background-color: #FFD580; }
    
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

# Référentiel complet (extrait pour l'exemple)
@st.cache_data
def get_ref():
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"},
        {"name": "Wavre", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"},
        {"name": "Liège", "prov": "Liège"}, {"name": "Oreye", "prov": "Liège"}, {"name": "Spa", "prov": "Liège"}
    ] # Ajoutez ici vos 281 communes

all_communes = get_ref()

# --- FILTRES ---
if 'search' not in st.session_state: st.session_state.search = ""
def reset(): st.session_state.search = ""; st.session_state.p = "Toutes"; st.session_state.py = "Tous"; st.session_state.s = "Tous"

# --- INTERFACE ---
c1, c2 = st.columns([0.35, 0.65])

with c1:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("📍 Légende & Carte")
    
    # Légende avec vraies couleurs
    cols = st.columns(2)
    for i, (p, col) in enumerate(PROV_COLORS.items()):
        cols[i%2].markdown(f"<span style='color:{col}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.write("---")
    # Affichage des points par province
    for p, col in PROV_COLORS.items():
        st.markdown(f"**{p}**", unsafe_allow_html=True)
        coms_p = [c for c in all_communes if c['prov'] == p]
        html_dots = ""
        for c in coms_p:
            active = "border: 2px solid #003366;" if not df_db[df_db['Commune']==c['name']].empty else ""
            html_dots += f"<div class='city-dot' style='background-color:{col}; {active}' title='{c['name']}'></div>"
        st.markdown(f"<div>{html_dots}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("👥 Utilisateurs Creos")
    
    # Barre de filtres unifiée
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    f1.text_input("Recherche", key="search", placeholder="Filtrer par nom...")
    f2.selectbox("Province", ["Toutes"] + list(PROV_COLORS.keys()), key="p")
    f3.selectbox("Paiement", ["Tous", "Prépaiement", "Post-paiement"], key="py")
    f4.selectbox("Service", ["Tous", "Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key="s")
    f5.button("EFFACER", on_click=reset)

    # Filtrage et Liste
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    
    st.write("---")
    for p in (PROV_COLORS.keys() if st.session_state.p == "Toutes" else [st.session_state.p]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f"<span class='badge bg-pre'>{row['Paiement']}</span>", unsafe_allow_html=True)
                l3.markdown(f"<span class='badge bg-cantine'>{row['Services']}</span>", unsafe_allow_html=True)
                l4.button("📝", key=f"ed_{row['Commune']}")
    st.markdown("</div>", unsafe_allow_html=True)
