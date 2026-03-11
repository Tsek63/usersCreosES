import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS RADICAL : ALIGNEMENT ET LISIBILITÉ ---
st.markdown("""
    <style>
    /* Fond et suppression des labels fantômes */
    .stApp { background-color: #E3F2FD !important; }
    div[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* ALIGNEMENT PARFAIT DE LA LIGNE DE FILTRES */
    [data-testid="stHorizontalBlock"] {
        align-items: end !important;
        gap: 10px !important;
    }

    /* FORÇAGE TEXTE BLANC ET FOND BLEU FONCÉ (Champs et Recherche) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        background-color: #003366 !important;
        border: 1px solid #BEE3F8 !important;
        height: 42px !important;
    }
    
    /* Couleur du texte écrit (Important pour la recherche) */
    input { 
        color: white !important; 
        -webkit-text-fill-color: white !important; 
    }
    div[data-baseweb="select"] span, div[role="option"] { 
        color: white !important; 
    }

    /* BOUTONS (Effacer, Valider) */
    .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        height: 42px !important;
        border: 1px solid #BEE3F8 !important;
        width: 100% !important;
        font-weight: bold !important;
    }

    /* CARTE ET POINTS */
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .dot-box {
        height: 16px; width: 16px;
        border-radius: 3px;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.1);
        margin-top: -35px; /* Aligne le carré sous le bouton invisible */
    }

    /* BADGES */
    .badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; color: #003366 !important; margin-right: 4px; border: 1px solid rgba(0,0,0,0.1); }
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

# Référentiel complet des 281 communes (Version écourtée pour le code, à compléter)
@st.cache_data
def get_full_ref():
    data = {
        "Bruxelles": ["Anderlecht", "Evere", "Uccle", "Ixelles", "Jette"],
        "Brabant Wallon": ["Wavre", "Nivelles", "Waterloo", "Braine-l'Alleud"],
        "Hainaut": ["Charleroi", "Mons", "Tournai", "La Louvière"],
        "Liège": ["Liège", "Verviers", "Huy", "Seraing", "Waremme"],
        "Namur": ["Namur", "Dinant", "Ciney", "Gembloux"],
        "Luxembourg": ["Arlon", "Bastogne", "Marche-en-Famenne"]
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_full_ref()

# --- LOGIQUE FILTRES ---
if 'search' not in st.session_state: st.session_state.search = ""
def reset_filters():
    st.session_state.search = ""
    st.session_state.f_prov = "Toutes"
    st.session_state.f_pay = "Tous"
    st.session_state.f_serv = "Tous"

# --- POP-UP CONFIGURATION ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    v_pay = row['Paiement'].iloc[0] if not row.empty else "Prépaiement"
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []

    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], index=0 if v_pay == "Prépaiement" else 1, horizontal=True)
    st.write("**Services**")
    c1, c2 = st.columns(2)
    s1 = c1.checkbox("Cantine Jour", value="Cantine Jour" in v_serv)
    s2 = c1.checkbox("Cantine Semaine", value="Cantine Semaine" in v_serv)
    s3 = c1.checkbox("Cantine Mois", value="Cantine Mois" in v_serv)
    s4 = c2.checkbox("Garderie", value="Garderie" in v_serv)
    s5 = c2.checkbox("Activités", value="Activités" in v_serv)
    
    selected = [s for s, v in zip(["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], [s1, s2, s3, s4, s5]) if v]
    st.divider()
    if st.button("VALIDER", type="primary", use_container_width=True):
        new_data = pd.DataFrame([[name, prov, pay, "|".join(selected)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_data], ignore_index=True)
        conn.update(data=up_df); st.rerun()
    if not row.empty:
        if st.button("🗑️ SUPPRIMER", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name]); st.rerun()

# --- INTERFACE ---
col_map, col_list = st.columns([0.35, 0.65])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    # Légende avec les vraies couleurs
    l1, l2 = st.columns(2)
    for i, (prov_name, prov_col) in enumerate(PROV_COLORS.items()):
        target_col = l1 if i < 3 else l2
        target_col.markdown(f"<span style='color:{prov_col}; font-size:20px;'>■</span> {prov_name}", unsafe_allow_html=True)
    
    st.write("---")
    # Affichage des 281 points
    for p_name, p_col in PROV_COLORS.items():
        st.markdown(f"<small><b>{p_name}</b></small>", unsafe_allow_html=True)
        coms = [c for c in all_ref if c['prov'] == p_name]
        grid = st.columns(13)
        for idx, com in enumerate(coms):
            is_active = not df_db[df_db['Commune'] == com['name']].empty
            with grid[idx % 13]:
                if st.button(" ", key=f"m_{com['name']}", help=com['name']):
                    edit_popup(com['name'], p_name)
                # Carré de couleur
                border = "2px solid #003366" if is_active else "1px solid rgba(0,0,0,0.1)"
                st.markdown(f"<div class='dot-box' style='background-color:{p_col}; border:{border};'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # --- LIGNE DE FILTRES UNIFIÉE (Pas de labels, même hauteur) ---
    f1, f2, f3, f4, f5 = st.columns([1.5, 1, 1, 1, 0.8])
    with f1: st.text_input("Recherche", key="search", placeholder="Rechercher...")
    with f2: st.selectbox("Prov", ["Toutes"] + list(PROV_COLORS.keys()), key="f_prov")
    with f3: st.selectbox("Pay", ["Tous", "Prépaiement", "Post-paiement"], key="f_pay")
    with f4: st.selectbox("Serv", ["Tous", "Cantine Jour", "Garderie", "Activités"], key="f_serv")
    with f5: st.button("EFFACER", on_click=reset_filters)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search, case=False, na=False)]
    if st.session_state.f_prov != "Toutes": df_f = df_f[df_f['Province'] == st.session_state.f_prov]
    if st.session_state.f_pay != "Tous": df_f = df_f[df_f['Paiement'] == st.session_state.f_pay]
    if st.session_state.f_serv != "Tous": df_f = df_f[df_f['Services'].str.contains(st.session_state.f_serv, case=False, na=False)]

    # --- LISTE ---
    st.markdown("<br>", unsafe_allow_html=True)
    for p in (PROV_COLORS.keys() if st.session_state.f_prov == "Toutes" else [st.session_state.f_prov]):
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5; padding-top:10px;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.3, 0.2, 0.4, 0.1])
                l1.write(f"**{row['Commune']}**")
                l2.markdown(f'<span class="badge {"bg-pre" if row["Paiement"]=="Prépaiement" else "bg-post"}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                s_list = str(row['Services']).split('|')
                s_badges = "".join([f'<span class="badge {"bg-cantine" if "Cantine" in s else "bg-garderie"}">{s}</span>' for s in s_list if s and s != 'nan'])
                l3.markdown(s_badges, unsafe_allow_html=True)
                if l4.button("📝", key=f"l_{row['Commune']}"): edit_popup(row['Commune'], p)
    st.markdown("</div>", unsafe_allow_html=True)
