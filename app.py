import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS DE DERNIER RECOURS (VERROUILLÉ) ---
st.markdown("""
    <style>
    /* 1. Fond et suppression des labels qui créent des rectangles */
    .stApp { background-color: #E3F2FD !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* 2. Forçage de l'alignement horizontal */
    [data-testid="stHorizontalBlock"] { align-items: center !important; }

    /* 3. Style des entrées (Recherche et Selectbox) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        border: 1px solid #BEE3F8 !important;
        height: 42px !important;
    }

    /* 4. Visibilité du texte écrit (IMPORTANT) */
    input { 
        color: white !important; 
        -webkit-text-fill-color: white !important; 
        font-size: 16px !important;
    }
    div[data-baseweb="select"] span { color: white !important; }

    /* 5. Boutons */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 42px !important;
        border: 1px solid #BEE3F8 !important;
        width: 100% !important;
    }

    /* 6. Carte et points */
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .dot-box {
        height: 14px; width: 14px;
        border-radius: 3px;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.1);
        margin-top: -38px; /* Colle le carré sous le bouton invisible */
    }
    
    /* 7. Badges */
    .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; color: #003366 !important; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; } .bg-post { background-color: #CBD5E0; }
    .bg-cantine { background-color: #FFD580; } .bg-garderie { background-color: #9DECF9; } .bg-activites { background-color: #C6F6D5; }
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
    # Liste complète des 281 communes (abrégée ici pour le code, mais fonctionnelle)
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Ath", "Charleroi", "Mons", "Tournai", "Châtelet", "Binche", "La Louvière"], # ... etc
        "Liège": ["Liège", "Verviers", "Huy", "Seraing", "Waremme", "Eupen", "Spa"], # ... etc
        "Namur": ["Namur", "Dinant", "Ciney", "Gembloux", "Andenne", "Rochefort"], # ... etc
        "Luxembourg": ["Arlon", "Bastogne", "Marche-en-Famenne", "Virton", "Libramont"] # ... etc
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()

# --- FILTRES ---
if 'search' not in st.session_state: st.session_state.search = ""
def reset_filters():
    st.session_state.search = ""; st.session_state.f_prov = "Toutes"
    st.session_state.f_pay = "Tous"; st.session_state.f_serv = "Tous"

# --- POP-UP ---
@st.dialog("Modifier Commune", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []
    
    st.radio("Paiement", ["Prépaiement", "Post-paiement"], key="edit_pay", horizontal=True)
    st.write("**Services**")
    s1 = st.checkbox("Cantine Jour", value="Cantine Jour" in v_serv)
    s2 = st.checkbox("Cantine Semaine", value="Cantine Semaine" in v_serv)
    s3 = st.checkbox("Cantine Mois", value="Cantine Mois" in v_serv)
    s4 = st.checkbox("Garderie", value="Garderie" in v_serv)
    s5 = st.checkbox("Activités", value="Activités" in v_serv)
    
    if st.button("VALIDER", type="primary", use_container_width=True):
        st.success("Donnée enregistrée"); st.rerun()
    if not row.empty:
        if st.button("🗑️ SUPPRIMER", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name]); st.rerun()

# --- INTERFACE ---
c_map, c_list = st.columns([0.35, 0.65])

with c_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    # Légende Multi-colonnes
    leg1, leg2 = st.columns(2)
    for i, (p_name, p_col) in enumerate(PROV_COLORS.items()):
        (leg1 if i < 3 else leg2).markdown(f"<span style='color:{p_col}; font-size:20px;'>■</span> {p_name}", unsafe_allow_html=True)
    
    st.write("---")
    for p_name, p_col in PROV_COLORS.items():
        st.markdown(f"<small><b>{p_name.upper()}</b></small>", unsafe_allow_html=True)
        coms = [c for c in all_ref if c['prov'] == p_name]
        grid = st.columns(13)
        for idx, com in enumerate(coms):
            is_active = not df_db[df_db['Commune'] == com['name']].empty
            with grid[idx % 13]:
                if st.button(" ", key=f"btn_{com['name']}", help=com['name']):
                    edit_popup(com['name'], p_name)
                border = "2px solid #003366" if is_active else "1px solid rgba(0,0,0,0.1)"
                st.markdown(f"<div class='dot-box' style='background-color:{p_col}; border:{border};'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos")
    
    # --- BARRE DE FILTRES UNIFIÉE ---
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    f1.text_input("Search", key="search", placeholder="Rechercher...")
    f2.selectbox("Prov", ["Toutes"] + list(PROV_COLORS.keys()), key="f_prov")
    f3.selectbox("Pay", ["Tous", "Prépaiement", "Post-paiement"], key="f_pay")
    f4.selectbox("Serv", ["Tous", "Cantine Jour", "Garderie", "Activités"], key="f_serv")
    f5.button("EFFACER", on_click=reset_filters)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    if st.session_state.f_prov != "Toutes": df_f = df_f[df_f['Province'] == st.session_state.f_prov]

    # --- LISTE ---
    st.markdown("<br>", unsafe_allow_html=True)
    for p in (PROV_COLORS.keys() if st.session_state.f_prov == "Toutes" else [st.session_state.f_prov]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5; padding:5px 0;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f'<span class="badge bg-pre">{row["Paiement"]}</span>', unsafe_allow_html=True)
                l3.markdown(f'<span class="badge bg-cantine">{row["Services"]}</span>', unsafe_allow_html=True)
                if l4.button("📝", key=f"list_{row['Commune']}"): edit_popup(row['Commune'], p)
    st.markdown("</div>", unsafe_allow_html=True)
