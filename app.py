import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS SÉLECTIF : SEULS LES FILTRES SONT EN BLANC ---
st.markdown("""
    <style>
    /* 1. FOND ET TEXTE GLOBAL (Bleu foncé partout) */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, li, div, span { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }

    /* 2. SUPPRESSION DES LABELS (Grands rectangles) */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* 3. FILTRES & RECHERCHE (Fond bleu foncé, Texte blanc) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        border: 1px solid #BEE3F8 !important;
        height: 42px !important;
    }
    
    /* Forçage du blanc UNIQUEMENT dans les inputs et selectbox */
    input { color: white !important; -webkit-text-fill-color: white !important; }
    div[data-baseweb="select"] span { color: white !important; }

    /* 4. CARTE (Points sans rectangles noirs) */
    .city-dot {
        height: 14px; width: 14px;
        border-radius: 3px;
        display: inline-block;
        margin: 2px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    /* 5. BOUTONS */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 42px !important;
        border: 1px solid #BEE3F8 !important;
    }

    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    
    /* 6. BADGES */
    .badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-right: 4px; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; color: #003366 !important; }
    .bg-cantine { background-color: #FFD580; color: #003366 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

# Référentiel complet des 281 communes (Exemple réduit)
@st.cache_data
def get_ref():
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"},
        {"name": "Wavre", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"},
        {"name": "Charleroi", "prov": "Hainaut"}, {"name": "Mons", "prov": "Hainaut"},
        {"name": "Liège", "prov": "Liège"}, {"name": "Spa", "prov": "Liège"},
        {"name": "Namur", "prov": "Namur"}, {"name": "Dinant", "prov": "Namur"},
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Bastogne", "prov": "Luxembourg"}
    ] # À compléter avec vos 281 noms

all_communes = get_ref()

# --- FILTRES ---
if 'search' not in st.session_state: st.session_state.search = ""
def reset():
    st.session_state.search = ""; st.session_state.p = "Toutes"
    st.session_state.py = "Tous"; st.session_state.s = "Tous"

# --- INTERFACE ---
c1, c2 = st.columns([0.35, 0.65])

with c1:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("📍 Légende & Carte")
    
    # Légende avec les couleurs distinctes
    l_cols = st.columns(2)
    for i, (p_name, p_col) in enumerate(PROV_COLORS.items()):
        l_cols[i%2].markdown(f"<span style='color:{p_col}; font-size:20px;'>■</span> {p_name}", unsafe_allow_html=True)
    
    st.write("---")
    # Carte avec Tooltip au survol
    for p_name, p_col in PROV_COLORS.items():
        st.markdown(f"**{p_name}**", unsafe_allow_html=True)
        coms_p = [c for c in all_communes if c['prov'] == p_name]
        html_dots = ""
        for c in coms_p:
            active = "border: 2px solid #003366;" if not df_db[df_db['Commune']==c['name']].empty else ""
            # Le titre 'title' crée l'infobulle au survol
            html_dots += f"<div class='city-dot' style='background-color:{p_col}; {active}' title='{c['name']}'></div>"
        st.markdown(f"<div>{html_dots}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("👥 Utilisateurs Creos")
    
    # Filtres alignés sur une seule ligne
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    f1.text_input("Search", key="search", placeholder="Rechercher...")
    f2.selectbox("Province", ["Toutes"] + list(PROV_COLORS.keys()), key="p")
    f3.selectbox("Paiement", ["Tous", "Prépaiement", "Post-paiement"], key="py")
    f4.selectbox("Service", ["Tous", "Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key="s")
    f5.button("EFFACER", on_click=reset)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    if st.session_state.p != "Toutes": df_f = df_f[df_f['Province'] == st.session_state.p]

    st.write("---")
    # Liste par province
    for prov in (PROV_COLORS.keys() if st.session_state.p == "Toutes" else [st.session_state.p]):
        p_data = df_f[df_f['Province'] == prov].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5;'>{prov.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f"<span class='badge bg-pre'>{row['Paiement']}</span>", unsafe_allow_html=True)
                l3.markdown(f"<span class='badge bg-cantine'>{row['Services']}</span>", unsafe_allow_html=True)
                l4.button("📝", key=f"btn_{row['Commune']}")
    st.markdown("</div>", unsafe_allow_html=True)
