import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE VERROUILLAGE TOTAL ---
st.markdown("""
    <style>
    /* 1. Suppression du bandeau blanc et optimisation des espaces */
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 2rem !important; }
    
    /* Cache les labels s'ils persistent malgré collapsed */
    div[data-testid="stWidgetLabel"] { display: none !important; }

    /* 2. Fond de page et texte bleu foncé */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, div { color: #003366 !important; }

    /* 3. ALIGNEMENT PARFAIT */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
    }

    /* 4. FILTRES & RECHERCHE : LISIBILITÉ MAXIMALE */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #002244 !important; 
        border: 2px solid #BEE3F8 !important;
        height: 45px !important;
    }
    input { 
        color: #FFFFFF !important; 
        -webkit-text-fill-color: #FFFFFF !important; 
        font-weight: bold !important;
    }
    div[data-baseweb="select"] span { color: #FFFFFF !important; }

    /* 5. BOUTON EFFACER */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 45px !important;
        width: 100% !important;
        border: 2px solid #BEE3F8 !important;
        font-weight: bold !important;
    }

    /* 6. COMPOSANTS PERSONNALISÉS */
    .white-card { 
        background-color: white; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #BEE3F8; 
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }
    .city-dot {
        height: 12px; width: 12px;
        border-radius: 2px;
        display: inline-block;
        margin: 1px;
        border: 1px solid rgba(0,0,0,0.1);
    }
    .badge { 
        padding: 4px 10px; 
        border-radius: 10px; 
        font-size: 11px; 
        font-weight: bold; 
        color: #003366 !important; 
        border: 1px solid rgba(0,0,0,0.1); 
    }
    .bg-pre { background-color: #A9D0F5; } 
    .bg-cantine { background-color: #FFD580; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
# Note: Assure-toi que tes secrets Streamlit sont configurés pour GSheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_db = conn.read(ttl=0).dropna(how="all")
except:
    # Fallback pour test si la connexion échoue
    df_db = pd.DataFrame(columns=["Commune", "Province", "Paiement", "Services"])

PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

@st.cache_data
def get_full_ref():
    data = {
        "Bruxelles": ["Anderlecht", "Bruxelles", "Ixelles", "Uccle"],
        "Brabant Wallon": ["Wavre", "Waterloo", "Nivelles"],
        "Hainaut": ["Charleroi", "Mons", "Tournai"],
        "Liège": ["Liège", "Huy", "Verviers"],
        "Namur": ["Namur", "Dinant"],
        "Luxembourg": ["Arlon", "Bastogne"]
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
        st.markdown(f"**{p_name}**")
        coms_p = [c for c in all_ref if c['prov'] == p_name]
        html_dots = "".join([f"<div class='city-dot' style='background-color:{p_col};' title='{c['name']}'></div>" for c in coms_p])
        st.markdown(f"<div>{html_dots}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("👥 Utilisateurs Creos")
    
    # BARRE DE FILTRES AVEC label_visibility="collapsed"
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    with f1: 
        st.text_input("Recherche", key="search", placeholder="Commune...", label_visibility="collapsed")
    with f2: 
        st.selectbox("Province", ["Toutes"] + list(PROV_COLORS.keys()), key="p", label_visibility="collapsed")
    with f3: 
        st.selectbox("Paiement", ["Tous", "Prépaiement", "Post-paiement"], key="py", label_visibility="collapsed")
    with f4: 
        st.selectbox("Service", ["Tous", "Cantine", "Garderie"], key="s", label_visibility="collapsed")
    with f5: 
        if st.button("EFFACER"):
            st.session_state.search = ""
            st.rerun()

    st.write("---")
    
    # Filtrage simplifié pour l'exemple
    df_f = df_db.copy()
    if st.session_state.search:
        df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]

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
