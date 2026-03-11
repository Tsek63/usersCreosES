import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE LISIBILITÉ FORCÉE (JAUNE ET NOIR) ---
st.markdown("""
    <style>
    /* 1. Nettoyage du haut de page */
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1rem !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; height: 0px !important; }

    /* 2. Fond de page bleu ciel et texte général NOIR pour être sûr de voir */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, div, b { color: #000000 !important; }

    /* 3. FILTRES : FOND JAUNE PALE / TEXTE NOIR (Impossible de ne pas lire) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #FFFFE0 !important; /* Jaune clair */
        border: 2px solid #000000 !important;
        height: 45px !important;
    }
    input { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
    }
    div[data-baseweb="select"] span { 
        color: #000000 !important; 
        font-weight: bold !important; 
    }

    /* 4. ALIGNEMENT DU BOUTON EFFACER */
    [data-testid="stHorizontalBlock"] { align-items: flex-end !important; }
    .stButton > button {
        background-color: #CC0000 !important; /* Rouge pour bien le voir */
        color: white !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: bold !important;
        border: 2px solid #000000 !important;
    }

    /* 5. CARTE (CARRES COULEUR) */
    .city-dot { height: 12px; width: 12px; border-radius: 2px; display: inline-block; margin: 1px; border: 1px solid #000; cursor: help; }
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 2px solid #003366; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

PROV_COLORS = {
    "Bruxelles": "#FFFF00", "Brabant Wallon": "#00FFFF", "Hainaut": "#FF00FF",
    "Liège": "#00FF00", "Namur": "#FF8000", "Luxembourg": "#FF0000"
}

def clear_filters():
    st.session_state["search_val"] = ""
    st.session_state["prov_val"] = "Toutes"

@st.cache_data
def get_full_ref():
    # Liste simplifiée pour le test, remettez la liste complète si ça marche
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"},
        {"name": "Wavre", "prov": "Brabant Wallon"}, {"name": "Liège", "prov": "Liège"},
        {"name": "Namur", "prov": "Namur"}, {"name": "Arlon", "prov": "Luxembourg"}
    ]

all_ref = get_full_ref()

# --- INTERFACE ---
c1, c2 = st.columns([0.35, 0.65])

with c1:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("📍 Carte & Légende")
    for p_name, p_col in PROV_COLORS.items():
        st.markdown(f"<b style='color:{p_col}; background:black; padding:2px;'> ■ </b> <b>{p_name}</b>", unsafe_allow_html=True)
        coms_p = [c for c in all_ref if c['prov'] == p_name]
        dots = "".join([f"<div class='city-dot' style='background-color:{p_col};' title='{c['name']}'></div>" for c in coms_p])
        st.markdown(f"<div>{dots}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("LISTE DES UTILISATEURS")
    
    # BARRE DE FILTRES
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: st.text_input("RECHERCHE", key="search_val")
    with f2: st.selectbox("PROVINCE", ["Toutes"] + list(PROV_COLORS.keys()), key="prov_val")
    with f3: st.button("EFFACER", on_click=clear_filters)

    st.write("---")
    # Liste
    search = st.session_state.get("search_val", "")
    df_f = df_db[df_db['Commune'].str.contains(search, case=False, na=False)] if search else df_db

    if not df_f.empty:
        for _, row in df_f.iterrows():
            st.write(f"**{row['Commune']}** - {row['Province']} | {row['Paiement']}")
    st.markdown("</div>", unsafe_allow_html=True)
