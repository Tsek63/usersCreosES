import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE VERROUILLAGE TOTAL ---
st.markdown("""
    <style>
    /* 1. Suppression du bandeau haut */
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1.5rem !important; }

    /* 2. RE-STYLISATION DES LABELS (Tes rectangles blancs) */
    /* On leur donne un look de petits titres propres */
    div[data-testid="stWidgetLabel"] p {
        color: #003366 !important;
        font-weight: bold !important;
        font-size: 14px !important;
        margin-bottom: -10px !important; /* Rapproche le titre du champ */
    }

    /* 3. Fond de page */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, div { color: #003366 !important; }

    /* 4. ALIGNEMENT DES FILTRES */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
    }

    /* 5. FILTRES & RECHERCHE */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #002244 !important; 
        border: 2px solid #BEE3F8 !important;
        height: 45px !important;
    }
    input { 
        color: #FFFFFF !important; 
        -webkit-text-fill-color: #FFFFFF !important; 
    }
    div[data-baseweb="select"] span { color: #FFFFFF !important; }

    /* 6. BOUTON EFFACER */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 45px !important;
        width: 100% !important;
        border: 2px solid #BEE3F8 !important;
        font-weight: bold !important;
    }

    /* 7. CARTES ET BADGES */
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .city-dot { height: 12px; width: 12px; border-radius: 2px; display: inline-block; margin: 1px; border: 1px solid rgba(0,0,0,0.1); }
    .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; color: #003366 !important; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; } .bg-cantine { background-color: #FFD580; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

@st.cache_data
def get_full_ref():
    # ... (Ta fonction de référence inchangée)
    data = {"Bruxelles": ["Anderlecht"], "Brabant Wallon": ["Wavre"]} # Simplifié pour l'exemple
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()

# --- INTERFACE ---
c1, c2 = st.columns([0.35, 0.65])

with c1:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("📍 Légende & Carte")
    # ... (Reste de ta carte)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("👥 Utilisateurs Creos")
    
    # ON UTILISE MAINTENANT LES LABELS COMME TITRES
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    with f1: st.text_input("Rechercher une commune", key="search", placeholder="Ex: Mons...")
    with f2: st.selectbox("Province", ["Toutes"] + list(PROV_COLORS.keys()), key="p")
    with f3: st.selectbox("Paiement", ["Tous", "Prépaiement", "Post-paiement"], key="py")
    with f4: st.selectbox("Service", ["Tous", "Cantine", "Garderie", "Activités"], key="s")
    with f5: 
        # Pour le bouton, on ajoute un petit texte vide pour l'aligner avec les autres
        st.markdown("<p style='margin-bottom:12px;'>&nbsp;</p>", unsafe_allow_html=True)
        if st.button("EFFACER"):
            st.session_state.search = ""
            st.rerun()

    # ... (Reste de ton code de filtrage et affichage)
    st.markdown("</div>", unsafe_allow_html=True)
