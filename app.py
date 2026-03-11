import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- STYLE CSS (Carrés, Badges et Pop-up) ---
st.markdown("""
    <style>
    /* Carrés de la carte */
    div.stButton > button {
        height: 18px !important; width: 18px !important; min-width: 18px !important;
        padding: 0px !important; margin: 1px !important; border: none !important; border-radius: 3px;
    }
    /* Style des badges dans la liste */
    .badge { padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: bold; color: white; margin-right: 5px; display: inline-block; }
    .bg-pre { background-color: #4A90E2; } /* Bleu */
    .bg-post { background-color: #50E3C2; } /* Vert/Cyan */
    .bg-service { background-color: #F5A623; } /* Orange */
    .prov-header { color: #1f4e79; font-weight: bold; border-bottom: 2px solid #eee; margin-top: 20px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- COULEURS PROVINCES (Pastel) ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1", "Brabant Wallon": "#A9F1EB", "Hainaut": "#C8B6FF",
    "Liège": "#9AE8FF", "Namur": "#FFCCB6", "Luxembourg": "#FF85F3"
}

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE DES 281 COMMUNES (Extraits pour l'exemple, à compléter si besoin) ---
def get_full_list():
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Auderghem", "prov": "Bruxelles"}, {"name": "Berchem-Sainte-Agathe", "prov": "Bruxelles"}, {"name": "Bruxelles", "prov": "Bruxelles"}, {"name": "Etterbeek", "prov": "Bruxelles"}, {"name": "Evere", "prov": "Bruxelles"}, {"name": "Forest", "prov": "Bruxelles"}, {"name": "Ganshoren", "prov": "Bruxelles"}, {"name": "Ixelles", "prov": "Bruxelles"}, {"name": "Jette", "prov": "Bruxelles"}, {"name": "Koekelberg", "prov": "Bruxelles"}, {"name": "Molenbeek-Saint-Jean", "prov": "Bruxelles"}, {"name": "Saint-Gilles", "prov": "Bruxelles"}, {"name": "Saint-Josse-ten-Noode", "prov": "Bruxelles"}, {"name": "Schaerbeek", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"}, {"name": "Watermael-Boitsfort", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Lambert", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Pierre", "prov": "Bruxelles"},
        {"name": "Beauvechain", "prov": "Brabant Wallon"}, {"name": "Braine-l'Alleud", "prov": "Brabant Wallon"}, {"name": "Braine-le-Château", "prov": "Brabant Wallon"}, {"name": "Chastre", "prov": "Brabant Wallon"}, {"name": "Chaumont-Gistoux", "prov": "Brabant Wallon"}, {"name": "Court-Saint-Étienne", "prov": "Brabant Wallon"}, {"name": "Genappe", "prov": "Brabant Wallon"}, {"name": "Grez-Doiceau", "prov": "Brabant Wallon"}, {"name": "Hélécine", "prov": "Brabant Wallon"}, {"name": "Incourt", "prov": "Brabant Wallon"}, {"name": "Ittre", "prov": "Brabant Wallon"}, {"name": "Jodoigne", "prov": "Brabant Wallon"}, {"name": "La Hulpe", "prov": "Brabant Wallon"}, {"name": "Lasne", "prov": "Brabant Wallon"}, {"name": "Mont-Saint-Guibert", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"}, {"name": "Orp-Jauche", "prov": "Brabant Wallon"}, {"name": "Ottignies-Louvain-la-Neuve", "prov": "Brabant Wallon"}, {"name": "Perwez", "prov": "Brabant Wallon"}, {"name": "Ramillies", "prov": "Brabant Wallon"}, {"name": "Rebecq", "prov": "Brabant Wallon"}, {"name": "Rixensart", "prov": "Brabant Wallon"}, {"name": "Tubize", "prov": "Brabant Wallon"}, {"name": "Villers-la-Ville", "prov": "Brabant Wallon"}, {"name": "Walhain", "prov": "Brabant Wallon"}, {"name": "Waterloo", "prov": "Brabant Wallon"}, {"name": "Wavre", "prov": "Brabant Wallon"},
        # ... Ajoutez ici le reste de vos communes (Hainaut, Liège, etc.)
    ]

all_communes = get_full_list()

# --- POP-UP D'ENCODAGE (Image 1) ---
@st.dialog("Configuration")
def edit_commune(name, prov):
    existing = df_db[df_db['Commune'] == name]
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pré-paiement"
    d_serv = str(existing['Services'].iloc[0]).split('|') if not existing.empty and not pd.isna(existing['Services'].iloc[0]) else []
    
    st.title(f":blue[{name}]")
    st.write("**Paiement**")
    pay = st.radio("Paiement", ["Pré-paiement", "Post-paiement"], index=0 if d_pay == "Pré-paiement" else 1, label_visibility="collapsed")
    
    st.write("**Services**")
    choices = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    serv = []
    for choice in choices:
        if st.checkbox(choice, value=(choice in d_serv)):
            serv.append(choice)
    
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(serv)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if c2.button("ANNULER", use_container_width=True):
        st.rerun()

# --- INTERFACE PRINCIPALE ---
col_map, col_list = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte")
    # Affichage par province pour recréer l'aspect "groupé"
    for prov_name in PROV_COLORS.keys():
        st.caption(f"**{prov_name}**")
        coms_in_prov = [c for c in all_communes if c['prov'] == prov_name]
        grid = st.columns(8) # 8 carrés par ligne
        for idx, com in enumerate(coms_in_prov):
            btn_key = f"m_{com['name']}_{prov_name}".replace(" ", "_")
            with grid[idx % 8]:
                if st.button(" ", key=btn_key):
                    edit_commune(com['name'], prov_name)
                st.markdown(f"<style>button[key='{btn_key}'] {{ background-color: {PROV_COLORS[prov_name]} !important; }}</style>", unsafe_allow_html=True)

with col_list:
    st.title("Utilisateurs Creos Extrascolaire")
    
    # Barre de recherche et filtres
    search = st.text_input("🔍 Chercher une commune...", placeholder="Ex: Evere")
    
    f1, f2, f3 = st.columns(3)
    sel_prov = f1.selectbox("Provinces", ["Toutes les Provinces"] + list(PROV_COLORS.keys()))
    sel_pay = f2.selectbox("Paiements", ["Tous", "Pré-paiement", "Post-paiement"])
    sel_serv = f3.selectbox("Services", ["Tous", "Cantine", "Garderie", "Activités"])

    # Filtrage
    df_filt = df_db.copy()
    if search: df_filt = df_filt[df_filt['Commune'].str.contains(search, case=False)]
    if sel_prov != "Toutes les Provinces": df_filt = df_filt[df_filt['Province'] == sel_prov]
    if sel_pay != "Tous": df_filt = df_filt[df_filt['Paiement'] == sel_pay]
    if sel_serv != "Tous": df_filt = df_filt[df_filt['Services'].str.contains(sel_serv, case=False)]

    # Liste détaillée (Image 2)
    for p in (list(PROV_COLORS.keys()) if sel_prov == "Toutes les Provinces" else [sel_prov]):
        p_df = df_filt[df_filt['Province'] == p].sort_values("Commune")
        if not p_df.empty:
            st.markdown(f"<div class='prov-header'>{p.upper()}</div>", unsafe_allow_html=True)
            for _, row in p_df.iterrows():
                l1, l2, l3 = st.columns([0.3, 0.2, 0.5])
                l1.write(f"**{row['Commune']}**")
                
                # Badge Paiement
                p_cls = "bg-pre" if row['Paiement'] == "Pré-paiement" else "bg-post"
                l2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                # Badges Services
                s_list = str(row['Services']).split('|')
                s_html = "".join([f'<span class="badge bg-service">{s}</span>' for s in s_list if s and s != "nan"])
                l3.markdown(s_html, unsafe_allow_html=True)
