import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE VERROUILLAGE FINAL ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 1rem !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; height: 0px !important; }
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, div { color: #003366 !important; }

    /* ALIGNEMENT VERTICAL DES FILTRES */
    [data-testid="stHorizontalBlock"] { align-items: flex-end !important; }

    /* FILTRES : TEXTE BLANC / FOND BLEU NUIT */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #002244 !important; 
        border: 2px solid #BEE3F8 !important;
        height: 45px !important;
    }
    input { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; font-weight: bold !important; }
    div[data-baseweb="select"] span { color: #FFFFFF !important; }

    /* BOUTON EFFACER */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 45px !important;
        width: 100% !important;
        border: 2px solid #BEE3F8 !important;
        font-weight: bold !important;
    }

    /* CARTE */
    .city-dot { height: 12px; width: 12px; border-radius: 2px; display: inline-block; margin: 1px; border: 1px solid rgba(0,0,0,0.1); cursor: help; }
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
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

# Fonction pour vider les filtres proprement (Évite l'erreur API)
def clear_filters():
    st.session_state["search_val"] = ""
    st.session_state["prov_val"] = "Toutes"
    st.session_state["pay_val"] = "Tous"
    st.session_state["serv_val"] = "Tous"

# Référentiel complet des 281 communes
@st.cache_data
def get_full_ref():
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Belœil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Écaussinnes", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Honnelles", "Jurbise", "La Louvière", "Le Rœulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
        "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Bullange", "Burdinne", "Burg-Reuland", "Bütgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "La Calamine", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
        "Namur": ["Andenne", "Anhée", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Éghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hastière", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "La Bruyère", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
        "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Érezée", "Étalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
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
    
    # BARRE DE FILTRES
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    with f1: st.text_input("Recherche", key="search_val", placeholder="Rechercher...")
    with f2: st.selectbox("Prov", ["Toutes"] + list(PROV_COLORS.keys()), key="prov_val")
    with f3: st.selectbox("Pay", ["Tous", "Prépaiement", "Post-paiement"], key="pay_val")
    with f4: st.selectbox("Serv", ["Tous", "Cantine", "Garderie", "Activités"], key="serv_val")
    with f5: st.button("EFFACER", on_click=clear_filters)

    # Filtrage
    df_f = df_db.copy()
    search = st.session_state.get("search_val", "")
    if search: df_f = df_f[df_f['Commune'].str.contains(search, case=False, na=False)]
    
    st.write("---")
    # Liste
    for prov in (PROV_COLORS.keys() if st.session_state.get("prov_val", "Toutes") == "Toutes" else [st.session_state["prov_val"]]):
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
