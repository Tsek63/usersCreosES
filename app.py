import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- COULEURS DES PROVINCES (Exactement selon votre image) ---
PROV_COLORS = {
    "Bruxelles": "#FFF2CC",      # Jaune
    "Brabant Wallon": "#D1F7F4", # Turquoise
    "Hainaut": "#D9D7FF",       # Lilas
    "Liège": "#CCE5FF",         # Bleu
    "Namur": "#FFD9CC",         # Saumon
    "Luxembourg": "#FFC9F3"      # Rose
}

# --- CSS : FOND BLEU, TEXTE NOIR ET CARRÉS ARRONDIS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E3F2FD !important; }}
    h1, h2, h3, h4, p, span, label {{ color: #1A5276 !important; font-family: 'Segoe UI', sans-serif; }}
    
    /* Conteneur blanc pour les blocs */
    .white-card {{
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}

    /* CARTE : Carrés de 14px arrondis */
    .map-grid {{ display: flex; flex-wrap: wrap; gap: 3px; margin-bottom: 15px; }}
    .dot {{
        height: 14px; width: 14px; border-radius: 4px;
        border: 1px solid rgba(0,0,0,0.1); display: inline-block;
    }}

    /* BADGES FILTRÉS (Image 3) */
    .badge {{
        padding: 4px 12px; border-radius: 15px; font-size: 11px; font-weight: bold;
        color: white; margin-right: 5px; display: inline-flex; align-items: center;
    }}
    .bg-pre {{ background-color: #4A90E2; }}
    .bg-post {{ background-color: #34495E; }}
    .bg-cantine {{ background-color: #F39C12; }}
    .bg-garderie {{ background-color: #00C2FF; }}
    .bg-activites {{ background-color: #2ECC71; }}
    </style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# LISTE DES 281 COMMUNES (Génération par province)
@st.cache_data
def get_all_communes():
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Belœil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Écaussinnes", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Honnelles", "Jurbise", "La Louvière", "Le Rœulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
        "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Bullange", "Burdinne", "Burg-Reuland", "Bütgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "La Calamine", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
        "Namur": ["Andenne", "Anhée", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Éghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "La Bruyère", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
        "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Érezée", "Étalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_communes = get_all_communes()

# --- POP-UP CONFIGURATION ---
@st.dialog("Configuration", width="small")
def open_config(name, prov):
    st.markdown(f"### :blue[{name}]")
    existing = df_db[df_db['Commune'] == name]
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Prépaiement"
    
    st.write("**Paiement**")
    pay = st.radio("Pay", ["Prépaiement", "Post-paiement"], index=0 if d_pay == "Prépaiement" else 1, horizontal=True, label_visibility="collapsed")
    
    st.write("**Services**")
    c1, c2 = st.columns(2)
    s1 = c1.checkbox("Cantine Jour")
    s2 = c1.checkbox("Cantine Semaine")
    s3 = c2.checkbox("Garderie")
    s4 = c2.checkbox("Activités")
    
    st.divider()
    b1, b2 = st.columns(2)
    if b1.button("VALIDER", type="primary", use_container_width=True):
        st.rerun()
    if b2.button("ANNULER", use_container_width=True):
        st.rerun()

# --- INTERFACE PRINCIPALE ---
col_map, col_list = st.columns([0.38, 0.62])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    
    # Légende (Image 5)
    l1, l2 = st.columns(2)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        (l1 if i < 3 else l2).markdown(f"<span style='color:{c}; font-size:18px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.markdown("<br><b>SITUATION GÉOGRAPHIQUE</b>", unsafe_allow_html=True)
    
    # Dessin de la carte province par province
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<small>{prov}</small>", unsafe_allow_html=True)
        coms = [c for c in all_communes if c['prov'] == prov]
        grid = st.columns(14) # 14 petits carrés par ligne
        for idx, com in enumerate(coms):
            with grid[idx % 14]:
                if st.button(" ", key=f"dot_{com['name']}", help=com['name']):
                    open_config(com['name'], prov)
                st.markdown(f"<div class='dot' style='background-color:{color}; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # Filtres
    search = st.text_input("Chercher une commune...", placeholder="Tapez ici...")
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
    f1.selectbox("Provinces", ["Toutes"])
    f2.selectbox("Paiements", ["Tous"])
    f3.selectbox("Services", ["Tous"])
    if f4.button("Effacer", use_container_width=True): st.rerun()

    # Liste des communes (Image 3)
    for prov in PROV_COLORS.keys():
        st.markdown(f"<h4 style='color:#4A90E2; border-bottom:1px solid #eee; padding-top:15px;'>{prov.upper()}</h4>", unsafe_allow_html=True)
        # Affichage de quelques exemples (remplacez par boucle sur df_db)
        display_list = [c for c in all_communes if c['prov'] == prov][:3]
        for com in display_list:
            c1, c2, c3, c4 = st.columns([0.3, 0.2, 0.4, 0.1])
            c1.write(f"**{com['name']}**")
            c2.markdown('<span class="badge bg-pre">Prépaiement</span>', unsafe_allow_html=True)
            c3.markdown('<span class="badge bg-cantine">Cantine Jour</span><span class="badge bg-garderie">Garderie</span>', unsafe_allow_html=True)
            if c4.button("📝", key=f"edit_{com['name']}"):
                open_config(com['name'], prov)
    st.markdown("</div>", unsafe_allow_html=True)
