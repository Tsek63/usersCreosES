import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- STYLE CSS (Unification Recherche, Filtres et Couleurs) ---
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, label { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }

    /* FORÇAGE COULEUR : Input Recherche ET Selectbox */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        color: white !important;
        border: 1px solid #BEE3F8 !important;
        height: 45px !important; /* Force la même hauteur pour l'alignement */
    }

    /* Texte à l'intérieur des champs */
    input, div[data-baseweb="select"] span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Liste déroulante ouverte (Pop-over) */
    div[data-baseweb="popover"] ul {
        background-color: #003366 !important;
    }
    li[role="option"] {
        color: white !important;
        background-color: #003366 !important;
    }
    li[role="option"]:hover {
        background-color: #0055A4 !important;
    }

    /* Boutons */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 45px !important;
        border: 1px solid #BEE3F8 !important;
        width: 100%;
    }

    /* Carte et Badges */
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .dot { height: 14px; width: 14px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.2); display: inline-block; }
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

# RÉFÉRENTIEL DES 281 COMMUNES (Indispensable pour la carte à gauche)
@st.cache_data
def get_full_ref():
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Belœil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Écaussinnes", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Honnelles", "Jurbise", "La Louvière", "Le Rœulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
        "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Bullange", "Burdinne", "Burg-Reuland", "Bütgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "La Calamine", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
        "Namur": ["Andenne", "Anhée", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Éghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamelois", "Hastière", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "La Bruyère", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
        "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Érezée", "Étalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()
PROV_COLORS = {"Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF", "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"}

# --- LOGIQUE FILTRES ---
if 'search' not in st.session_state: st.session_state.search = ""
if 'prov' not in st.session_state: st.session_state.prov = "Toutes"
if 'pay' not in st.session_state: st.session_state.pay = "Tous"
if 'serv' not in st.session_state: st.session_state.serv = "Tous"

def clear_filters():
    st.session_state.search = ""
    st.session_state.prov = "Toutes"
    st.session_state.pay = "Tous"
    st.session_state.serv = "Tous"

# --- POP-UP CONFIGURATION ---
@st.dialog("Configuration Commune", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    v_pay = row['Paiement'].iloc[0] if not row.empty else "Prépaiement"
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []

    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], index=0 if v_pay == "Prépaiement" else 1, horizontal=True)
    st.write("**Services activés**")
    c1, c2 = st.columns(2)
    s1 = c1.checkbox("Cantine Jour", value="Cantine Jour" in v_serv)
    s2 = c1.checkbox("Cantine Semaine", value="Cantine Semaine" in v_serv)
    s3 = c1.checkbox("Cantine Mois", value="Cantine Mois" in v_serv)
    s4 = c2.checkbox("Garderie", value="Garderie" in v_serv)
    s5 = c2.checkbox("Activités", value="Activités" in v_serv)
    
    selected = [s for s, v in zip(["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], [s1, s2, s3, s4, s5]) if v]

    st.divider()
    b1, b2 = st.columns(2)
    if b1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(selected)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if b2.button("ANNULER", use_container_width=True): st.rerun()
    if not row.empty:
        if st.button("🗑️ SUPPRIMER CETTE COMMUNE", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name]); st.rerun()

# --- LAYOUT PRINCIPAL ---
c_map, c_list = st.columns([0.35, 0.65])

with c_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    for p, color in PROV_COLORS.items():
        st.markdown(f"<span style='color:{color}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)
    st.write("---")
    for p, color in PROV_COLORS.items():
        st.markdown(f"<small><b>{p}</b></small>", unsafe_allow_html=True)
        coms = [c for c in all_ref if c['prov'] == p]
        grid = st.columns(13)
        for idx, com in enumerate(coms):
            is_active = not df_db[df_db['Commune'] == com['name']].empty
            with grid[idx % 13]:
                if st.button(" ", key=f"map_{com['name']}"): edit_popup(com['name'], p)
                border = "2px solid #003366" if is_active else "1px solid rgba(0,0,0,0.1)"
                st.markdown(f"<div class='dot' style='background-color:{color}; border:{border}; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # --- FILTRES ALIGNÉS (Recherche + Selectbox sur une ligne) ---
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    f1.text_input("🔍 Recherche", key="search", label_visibility="collapsed")
    f2.selectbox("Provinces", ["Toutes"] + list(PROV_COLORS.keys()), key="prov", label_visibility="collapsed")
    f3.selectbox("Paiements", ["Tous", "Prépaiement", "Post-paiement"], key="pay", label_visibility="collapsed")
    f4.selectbox("Services", ["Tous", "Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key="serv", label_visibility="collapsed")
    f5.button("EFFACER", on_click=clear_filters)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    if st.session_state.prov != "Toutes": df_f = df_f[df_f['Province'] == st.session_state.prov]
    if st.session_state.pay != "Tous": df_f = df_f[df_f['Paiement'] == st.session_state.pay]
    if st.session_state.serv != "Tous": df_f = df_f[df_f['Services'].str.contains(st.session_state.serv, case=False, na=False)]

    # --- LISTE PAR PROVINCE ---
    st.markdown("<br>", unsafe_allow_html=True)
    for p in (PROV_COLORS.keys() if st.session_state.prov == "Toutes" else [st.session_state.prov]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5; padding-top:10px;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                p_cls = "bg-pre" if row['Paiement'] == "Prépaiement" else "bg-post"
                l2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                s_badges = "".join([f'<span class="badge bg-cantine">{s}</span>' if "Cantine" in s else f'<span class="badge bg-garderie">{s}</span>' for s in str(row['Services']).split('|') if s])
                l3.markdown(s_badges, unsafe_allow_html=True)
                if l4.button("📝", key=f"list_{row['Commune']}"): edit_popup(row['Commune'], p)
    st.markdown("</div>", unsafe_allow_html=True)
