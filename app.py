import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- STYLE CSS (Zéro Noir, Alignement et Tooltips) ---
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, label { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }

    /* Nettoyage des rectangles fantômes et labels vides */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    .stSelectbox, .stTextInput { margin-top: -15px; }

    /* FILTRES & RECHERCHE : Bleu foncé, texte blanc lisible */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        color: white !important;
        border: 1px solid #BEE3F8 !important;
        height: 40px !important;
    }
    
    /* Forçage de la couleur du texte saisi */
    input { color: white !important; -webkit-text-fill-color: white !important; }
    div[data-baseweb="select"] span { color: white !important; }

    /* CARTE : Carrés de couleur uniquement */
    .map-container { display: flex; flex-wrap: wrap; gap: 4px; padding: 10px 0; }
    .dot-btn {
        height: 16px; width: 16px;
        border-radius: 3px;
        border: 1px solid rgba(0,0,0,0.1);
        display: inline-block;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .dot-btn:hover { transform: scale(1.3); border: 1px solid #003366; }

    /* BOUTONS LISTE */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 6px !important;
        height: 40px !important;
    }

    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; color: #003366 !important; margin-right: 4px; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; }
    .bg-post { background-color: #CBD5E0; }
    .bg-cantine { background-color: #FFD580; }
    .bg-garderie { background-color: #9DECF9; }
    .bg-activites { background-color: #C6F6D5; }
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
    # Liste simplifiée pour le code (gardez votre dictionnaire complet de 281 ici)
    data = {
        "Bruxelles": ["Anderlecht", "Evere", "Uccle"],
        "Liège": ["Baelen", "Spa", "Huy", "Verviers"],
        "Namur": ["Namur", "Dinant", "Ciney"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()

# --- FILTRES STATE ---
if 'search' not in st.session_state: st.session_state.search = ""
def clear_filters():
    st.session_state.search = ""
    st.session_state.prov = "Toutes"
    st.session_state.pay = "Tous"
    st.session_state.serv = "Tous"

# --- POP-UP ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []
    
    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
    st.write("**Services**")
    s1 = st.checkbox("Cantine Jour", value="Cantine Jour" in v_serv)
    s2 = st.checkbox("Cantine Semaine", value="Cantine Semaine" in v_serv)
    s3 = st.checkbox("Cantine Mois", value="Cantine Mois" in v_serv)
    s4 = st.checkbox("Garderie", value="Garderie" in v_serv)
    s5 = st.checkbox("Activités", value="Activités" in v_serv)
    
    st.divider()
    if st.button("VALIDER", type="primary", use_container_width=True):
        st.rerun()
    if not row.empty:
        if st.button("🗑️ SUPPRIMER", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name]); st.rerun()

# --- INTERFACE ---
c_map, c_list = st.columns([0.35, 0.65])

with c_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("SITUATION GÉOGRAPHIQUE")
    
    for p, color in PROV_COLORS.items():
        st.markdown(f"**{p}**", unsafe_allow_html=True)
        coms = [c for c in all_ref if c['prov'] == p]
        
        # On utilise des colonnes Streamlit très serrées pour simuler la grille
        grid = st.columns(12)
        for idx, com in enumerate(coms):
            with grid[idx % 12]:
                # On utilise help pour le survol du nom
                if st.button(" ", key=f"m_{com['name']}", help=com['name']):
                    edit_popup(com['name'], p)
                # Le CSS 'margin-top' vient coller la couleur sous le bouton invisible
                st.markdown(f"<div class='dot-btn' style='background-color:{color}; margin-top:-32px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos")
    
    # --- FILTRES ALIGNÉS ---
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    f1.text_input("Recherche", key="search", placeholder="Nom...")
    f2.selectbox("Prov", ["Toutes"] + list(PROV_COLORS.keys()), key="prov")
    f3.selectbox("Pay", ["Tous", "Prépaiement", "Post-paiement"], key="pay")
    f4.selectbox("Serv", ["Tous", "Cantine Jour", "Garderie", "Activités"], key="serv")
    f5.button("EFFACER", on_click=clear_filters)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    
    # --- LISTE ---
    st.markdown("<br>", unsafe_allow_html=True)
    for p in (PROV_COLORS.keys() if st.session_state.prov == "Toutes" else [st.session_state.prov]):
        p_rows = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_rows.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_rows.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f'<span class="badge bg-pre">{row["Paiement"]}</span>', unsafe_allow_html=True)
                l3.markdown(f'<span class="badge bg-cantine">{row["Services"]}</span>', unsafe_allow_html=True)
                if l4.button("📝", key=f"l_{row['Commune']}"): edit_popup(row['Commune'], p)
    st.markdown("</div>", unsafe_allow_html=True)
