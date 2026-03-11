import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE PRÉCISION ---
st.markdown("""
    <style>
    /* 1. FOND ET TEXTE GÉNÉRAL */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, div { color: #003366 !important; }

    /* 2. SUPPRESSION DES RECTANGLES ET ESPACES HAUT DE PAGE */
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1rem !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; height: 0px !important; }

    /* 3. FILTRES & RECHERCHE : FOND FONCÉ / TEXTE BLANC FLASH */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #002244 !important; /* Bleu très sombre pour contraste */
        border: 2px solid #BEE3F8 !important;
        height: 45px !important;
    }
    
    /* Forçage du texte blanc dans les champs (Recherche + Select) */
    input { 
        color: #FFFFFF !important; 
        -webkit-text-fill-color: #FFFFFF !important; 
        font-weight: bold !important;
    }
    div[data-baseweb="select"] span { color: #FFFFFF !important; font-weight: bold !important; }

    /* 4. ALIGNEMENT DU BOUTON EFFACER */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 45px !important;
        width: 100% !important;
        border: 2px solid #BEE3F8 !important;
        font-weight: bold !important;
        margin-top: 0px !important; /* Aligné avec les filtres sans label */
    }

    /* 5. CARTE & POINTS */
    .city-dot {
        height: 12px; width: 12px;
        border-radius: 3px;
        display: inline-block;
        margin: 1px;
        border: 1px solid rgba(0,0,0,0.1);
        cursor: help;
    }

    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; color: #003366 !important; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; } .bg-cantine { background-color: #FFD580; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES & RÉFÉRENTIEL ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

@st.cache_data
def get_full_ref():
    # Liste complète des 281 communes (Simulée ici)
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Evere", "Uccle", "Ixelles"],
        "Brabant Wallon": ["Wavre", "Nivelles", "Waterloo", "Braine-l'Alleud"],
        "Liège": ["Liège", "Verviers", "Huy", "Spa", "Oreye", "Sprimont", "Awans"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()

# --- INTERFACE ---
c1, c2 = st.columns([0.35, 0.65])

with c1:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("📍 Légende & Carte")
    l_cols = st.columns(2)
    for i, (p_name, p_col) in enumerate(PROV_COLORS.items()):
        l_cols[i%2].markdown(f"<span style='color:{p_col}; font-size:20px;'>■</span> {p_name}", unsafe_allow_html=True)
    
    st.write("---")
    for p_name, p_col in PROV_COLORS.items():
        st.markdown(f"**{p_name}**", unsafe_allow_html=True)
        coms_p = [c for c in all_ref if c['prov'] == p_name]
        html_dots = "".join([f"<div class='city-dot' style='background-color:{p_col}; {'border:2px solid #003366;' if not df_db[df_db['Commune']==c['name']].empty else ''}' title='{c['name']}'></div>" for c in coms_p])
        st.markdown(f"<div>{html_dots}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("👥 Utilisateurs Creos")
    
    # BARRE DE FILTRES ALIGNÉE (Même hauteur, Contraste maximum)
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    with f1: st.text_input("Recherche", key="search", placeholder="Chercher...")
    with f2: st.selectbox("Prov", ["Toutes"] + list(PROV_COLORS.keys()), key="p")
    with f3: st.selectbox("Pay", ["Tous", "Prépaiement", "Post-paiement"], key="py")
    with f4: st.selectbox("Serv", ["Tous", "Cantine", "Garderie", "Activités"], key="s")
    with f5: 
        if st.button("EFFACER"):
            st.session_state.search = ""
            st.rerun()

    # Liste filtrée
    df_f = df_db.copy()
    if st.session_state.search: 
        df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    
    st.write("---")
    for prov in (PROV_COLORS.keys() if st.session_state.get('p', 'Toutes') == 'Toutes' else [st.session_state.p]):
        p_data = df_f[df_f['Province'] == prov].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4>{prov.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f"<span class='badge bg-pre'>{row['Paiement']}</span>", unsafe_allow_html=True)
                l3.markdown(f"<span class='badge bg-cantine'>{row['Services']}</span>", unsafe_allow_html=True)
                l4.button("📝", key=f"ed_{row['Commune']}")
    st.markdown("</div>", unsafe_allow_html=True)
