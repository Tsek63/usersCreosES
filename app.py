import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- STYLE CSS RADICAL (Éviter le noir à l'ouverture) ---
st.markdown("""
    <style>
    /* Fond et Texte Global */
    .stApp { background-color: #E3F2FD !important; }
    h1, h2, h3, h4, p, span, label { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }

    /* FILTRES & INPUTS : Forçage Bleu Foncé */
    /* État fermé et ouvert */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="popover"] ul, 
    div[role="listbox"], 
    li[role="option"] {
        background-color: #003366 !important;
        color: white !important;
    }
    
    /* Texte des options dans le menu ouvert */
    li[role="option"] span, div[data-baseweb="select"] span {
        color: white !important;
    }

    /* Survol des options dans le menu */
    li[role="option"]:hover {
        background-color: #0055A4 !important;
    }

    /* BOUTONS (Bleu foncé, texte blanc) */
    button[kind="secondary"], button[kind="primary"] {
        background-color: #003366 !important;
        color: white !important;
        border: 1px solid #BEE3F8 !important;
    }

    /* CARTE & BADGES */
    .white-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #BEE3F8; margin-bottom: 20px; }
    .dot { height: 14px; width: 14px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.3); display: inline-block; }
    .badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; color: #003366 !important; margin-right: 4px; border: 1px solid rgba(0,0,0,0.1); }
    .bg-pre { background-color: #A9D0F5; }
    .bg-post { background-color: #CBD5E0; }
    .bg-cantine { background-color: #FFD580; }
    .bg-garderie { background-color: #9DECF9; }
    .bg-activites { background-color: #C6F6D5; }
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- INITIALISATION SESSION STATE (Pour bouton Effacer) ---
if 'search_query' not in st.session_state: st.session_state.search_query = ""
if 'f_prov' not in st.session_state: st.session_state.f_prov = "Toutes"
if 'f_pay' not in st.session_state: st.session_state.f_pay = "Tous"
if 'f_serv' not in st.session_state: st.session_state.f_serv = "Tous"

def reset_filters():
    st.session_state.search_query = ""
    st.session_state.f_prov = "Toutes"
    st.session_state.f_pay = "Tous"
    st.session_state.f_serv = "Tous"

# --- POP-UP MODIFICATION ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    v_pay = row['Paiement'].iloc[0] if not row.empty else "Prépaiement"
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []

    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], index=0 if v_pay == "Prépaiement" else 1, horizontal=True)
    
    st.write("**Services**")
    # Liste complète des services demandés
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
        if st.button("🗑️ SUPPRIMER", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name]); st.rerun()

# --- INTERFACE ---
PROV_COLORS = {"Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF", "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"}

col_map, col_list = st.columns([0.35, 0.65])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<span style='color:{color}; font-size:20px;'>■</span> {prov}", unsafe_allow_html=True)
    st.write("---")
    # Carte (Points encodés uniquement pour l'exemple)
    for prov, color in PROV_COLORS.items():
        p_data = df_db[df_db['Province'] == prov]
        grid = st.columns(12)
        for idx, (_, r) in enumerate(p_data.iterrows()):
            with grid[idx % 12]:
                if st.button(" ", key=f"d_{r['Commune']}"): edit_popup(r['Commune'], prov)
                st.markdown(f"<div class='dot' style='background-color:{color}; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos")
    
    # --- FILTRES ---
    st.text_input("🔍 Rechercher...", key="search_query")
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1.2])
    s_prov = f1.selectbox("Provinces", ["Toutes"] + list(PROV_COLORS.keys()), key="f_prov")
    s_pay = f2.selectbox("Paiements", ["Tous", "Prépaiement", "Post-paiement"], key="f_pay")
    s_serv = f3.selectbox("Services", ["Tous", "Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key="f_serv")
    
    f4.button("EFFACER", on_click=reset_filters, use_container_width=True)

    # Filtrage
    df_f = df_db.copy()
    if st.session_state.search_query: df_f = df_f[df_f['Commune'].str.contains(st.session_state.search_query, case=False, na=False)]
    if s_prov != "Toutes": df_f = df_f[df_f['Province'] == s_prov]
    if s_pay != "Tous": df_f = df_f[df_f['Paiement'] == s_pay]
    if s_serv != "Tous": df_f = df_f[df_f['Services'].str.contains(s_serv, case=False, na=False)]

    # --- LISTE ---
    for prov in (PROV_COLORS.keys() if s_prov == "Toutes" else [s_prov]):
        p_rows = df_f[df_f['Province'] == prov].sort_values("Commune")
        if not p_rows.empty:
            st.markdown(f"<h4 style='border-bottom:2px solid #A9D0F5;'>{prov.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_rows.iterrows():
                c1, c2, c3, c4 = st.columns([0.3, 0.2, 0.4, 0.1])
                c1.write(f"**{row['Commune']}**")
                c2.markdown(f'<span class="badge {"bg-pre" if row["Paiement"]=="Prépaiement" else "bg-post"}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                # Badges services
                s_badges = "".join([f'<span class="badge bg-cantine">{s}</span>' if "Cantine" in s else f'<span class="badge bg-garderie">{s}</span>' for s in str(row['Services']).split('|') if s])
                c3.markdown(s_badges, unsafe_allow_html=True)
                if c4.button("📝", key=f"ed_{row['Commune']}"): edit_popup(row['Commune'], prov)
    st.markdown("</div>", unsafe_allow_html=True)
