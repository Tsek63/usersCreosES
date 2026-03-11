import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- COULEURS DES PROVINCES (Basé sur vos images) ---
PROV_COLORS = {
    "Bruxelles": "#FFF2CC",      # Jaune très clair
    "Brabant Wallon": "#D1F7F4", # Turquoise clair
    "Hainaut": "#D9D7FF",       # Lilas
    "Liège": "#CCE5FF",         # Bleu ciel
    "Namur": "#FFD9CC",         # Saumon
    "Luxembourg": "#FFC9F3"      # Rose
}

# --- STYLE CSS AVANCÉ (Fond bleu, points de carte, badges) ---
st.markdown(f"""
    <style>
    /* Fond général bleu clair */
    .stApp {{ background-color: #E3F2FD !important; }}
    
    /* Titres et textes en bleu foncé */
    h1, h2, h3, p, span {{ color: #1A5276 !important; font-family: 'Segoe UI', sans-serif; }}

    /* CARTE : Design en "Dots" (Points) */
    .map-dot {{
        height: 12px; width: 12px;
        border-radius: 3px;
        display: inline-block;
        margin: 1px;
        border: 1px solid rgba(0,0,0,0.05);
        cursor: pointer;
    }}
    .dot-active {{ border: 2px solid #2C3E50 !important; }}

    /* BADGES (Image 3 & 5) */
    .badge {{
        padding: 4px 10px; border-radius: 6px;
        font-size: 11px; font-weight: bold; color: white;
        margin-right: 5px; display: inline-flex; align-items: center;
    }}
    .bg-pre {{ background-color: #4A90E2; }}      /* Bleu Paiement */
    .bg-post {{ background-color: #5D6D7E; }}     /* Gris Post-paiement */
    .bg-cantine {{ background-color: #F39C12; }}   /* Orange */
    .bg-garderie {{ background-color: #3498DB; }}  /* Bleu Service */
    .bg-activites {{ background-color: #2ECC71; }} /* Vert */

    /* Conteneur Blanc pour les sections */
    .white-card {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# Liste complète (doit être exhaustive pour les 281 communes)
@st.cache_data
def get_communes():
    # Ici, mettez votre liste complète. Exemple réduit :
    data = {
        "Bruxelles": ["Evere", "Uccle", "Woluwe-Saint-Lambert"],
        "Brabant Wallon": ["Jodoigne", "Nivelles", "Rixensart", "Walhain"],
        "Hainaut": ["Chapelle-lez-Herlaimont", "Erquelinnes", "Leuze-en-Hainaut"],
        "Liège": ["Baelen", "Spa", "Huy", "Verviers"],
        "Namur": ["Namur", "Dinant", "Ciney"],
        "Luxembourg": ["Arlon", "Bastogne"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_communes = get_communes()

# --- DIALOGUE (POP-UP IMAGE 2) ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    existing = df_db[df_db['Commune'] == name]
    
    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
    st.write("**Services**")
    c1, c2 = st.columns(2)
    s1 = c1.checkbox("Cantine Jour")
    s2 = c1.checkbox("Cantine Semaine")
    s3 = c2.checkbox("Garderie")
    s4 = c2.checkbox("Activités")
    
    st.divider()
    col_b1, col_b2 = st.columns(2)
    if col_b1.button("VALIDER", type="primary", use_container_width=True):
        # Logique de sauvegarde ici
        st.success("Enregistré")
        st.rerun()
    if col_b2.button("ANNULER", use_container_width=True):
        st.rerun()

# --- INTERFACE ---
col_left, col_right = st.columns([0.35, 0.65])

# GAUCHE : LÉGENDE ET CARTE (Image 5)
with col_left:
    with st.container():
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.subheader("LÉGENDE & STATISTIQUES")
        leg1, leg2 = st.columns(2)
        for i, (p, c) in enumerate(PROV_COLORS.items()):
            target = leg1 if i < 3 else leg2
            target.markdown(f"<span style='color:{c}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)
        
        st.markdown("<br><b>SITUATION GÉOGRAPHIQUE</b>", unsafe_allow_html=True)
        # Affichage de la carte en "points"
        for prov, color in PROV_COLORS.items():
            coms = [c for c in all_communes if c['prov'] == prov]
            cols = st.columns(15) # Grille de points
            for idx, com in enumerate(coms):
                with cols[idx % 15]:
                    # On utilise des boutons invisibles par-dessus les points pour le clic
                    if st.button(" ", key=f"dot_{com['name']}", help=com['name']):
                        edit_popup(com['name'], prov)
                    st.markdown(f"<div class='map-dot' style='background-color:{color}; margin-top:-30px;'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# DROITE : LISTE (Image 3 & 5)
with col_right:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # Barre de recherche et Filtres
    search = st.text_input("Chercher une commune...", label_visibility="collapsed")
    f1, f2, f3, f4 = st.columns([2,2,2,1])
    f1.selectbox("Toutes les Provinces", ["Toutes"])
    f2.selectbox("Paiements", ["Tous"])
    f3.selectbox("Services", ["Tous"])
    f4.button("Effacer filtres")

    # Liste détaillée
    for prov in PROV_COLORS.keys():
        st.markdown(f"<h4 style='color:#4A90E2; border-bottom:1px solid #eee; padding:10px 0;'>{prov.upper()}</h4>", unsafe_allow_html=True)
        # Simulation de lignes
        display_data = [c for c in all_communes if c['prov'] == prov]
        for com in display_data:
            c_name, c_pay, c_serv = st.columns([0.3, 0.2, 0.4, 0.1])
            c_name.write(f"**{com['name']}**")
            c_pay.markdown('<span class="badge bg-pre">Prépaiement</span>', unsafe_allow_html=True)
            c_serv.markdown('<span class="badge bg-cantine">Cantine Jour</span><span class="badge bg-garderie">Garderie</span>', unsafe_allow_html=True)
            if c_serv.button("📝", key=f"edit_{com['name']}"):
                edit_popup(com['name'], prov)
    st.markdown("</div>", unsafe_allow_html=True)
