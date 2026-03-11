import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- RÉFÉRENTIEL ---
PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

# --- STYLE CSS (Texte bleu foncé & Carrés) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E3F2FD !important; }}
    h1, h2, h3, h4, p, span, label {{ color: #003366 !important; font-family: 'Segoe UI', sans-serif; font-weight: 500; }}
    .white-card {{ background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #BEE3F8; }}
    
    /* CARTE : Points */
    .dot {{ height: 14px; width: 14px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.3); display: inline-block; }}
    
    /* BADGES : Texte foncé sur fond pastel */
    .badge {{ padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; color: #003366 !important; margin-right: 4px; display: inline-flex; border: 1px solid rgba(0,0,0,0.1); }}
    .bg-pre {{ background-color: #A9D0F5; }}
    .bg-post {{ background-color: #CBD5E0; }}
    .bg-cantine {{ background-color: #FFD580; }}
    .bg-garderie {{ background-color: #9DECF9; }}
    .bg-activites {{ background-color: #C6F6D5; }}
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- DIALOGUE DE MODIFICATION ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    row = df_db[df_db['Commune'] == name]
    
    v_pay = row['Paiement'].iloc[0] if not row.empty else "Prépaiement"
    v_serv = str(row['Services'].iloc[0]).split('|') if not row.empty else []

    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], index=0 if v_pay == "Prépaiement" else 1, horizontal=True)
    st.write("**Services**")
    s1 = st.checkbox("Cantine Jour", value="Cantine Jour" in v_serv)
    s2 = st.checkbox("Cantine Semaine", value="Cantine Semaine" in v_serv)
    s3 = st.checkbox("Garderie", value="Garderie" in v_serv)
    s4 = st.checkbox("Activités", value="Activités" in v_serv)
    
    selected = [s for s, v in zip(["Cantine Jour", "Cantine Semaine", "Garderie", "Activités"], [s1, s2, s3, s4]) if v]

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(selected)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    if c2.button("ANNULER", use_container_width=True): st.rerun()
    
    if not row.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ SUPPRIMER LA DONNÉE", use_container_width=True):
            conn.update(data=df_db[df_db['Commune'] != name])
            st.rerun()

# --- INTERFACE ---
col_map, col_list = st.columns([0.35, 0.65])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    l1, l2 = st.columns(2)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        (l1 if i < 3 else l2).markdown(f"<span style='color:{c}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.write("---")
    # Simulation Carte (Boucle sur les données encodées pour l'exemple)
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<small><b>{prov}</b></small>", unsafe_allow_html=True)
        p_data = df_db[df_db['Province'] == prov]
        grid = st.columns(12)
        for idx, (_, r) in enumerate(p_data.iterrows()):
            with grid[idx % 12]:
                if st.button(" ", key=f"d_{r['Commune']}"): edit_popup(r['Commune'], prov)
                st.markdown(f"<div class='dot' style='background-color:{color}; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # --- BARRE DE RECHERCHE ET FILTRES (Image 3 & 5) ---
    search = st.text_input("🔍 Rechercher une commune...", placeholder="Entrez un nom...")
    
    f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
    s_prov = f1.selectbox("Provinces", ["Toutes"] + list(PROV_COLORS.keys()))
    s_pay = f2.selectbox("Paiements", ["Tous", "Prépaiement", "Post-paiement"])
    s_serv = f3.selectbox("Services", ["Tous", "Cantine", "Garderie", "Activités"])
    
    if f4.button("Effacer", use_container_width=True):
        st.rerun()

    # Logique de filtrage
    df_f = df_db.copy()
    if search: df_f = df_f[df_f['Commune'].str.contains(search, case=False, na=False)]
    if s_prov != "Toutes": df_f = df_f[df_f['Province'] == s_prov]
    if s_pay != "Tous": df_f = df_f[df_f['Paiement'] == s_pay]
    if s_serv != "Tous": df_f = df_f[df_f['Services'].str.contains(s_serv, case=False, na=False)]

    # --- LISTE DES DONNÉES ---
    st.markdown("<br>", unsafe_allow_html=True)
    view_provinces = list(PROV_COLORS.keys()) if s_prov == "Toutes" else [s_prov]
    for p in view_provinces:
        p_rows = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_rows.empty:
            st.markdown(f"<h4 style='color:#003366; border-bottom:2px solid #A9D0F5; padding:5px 0;'>{p.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_rows.iterrows():
                c1, c2, c3, c4 = st.columns([0.3, 0.2, 0.4, 0.1])
                c1.write(f"**{row['Commune']}**")
                
                # Badge Paiement
                p_cls = "bg-pre" if row['Paiement'] == "Prépaiement" else "bg-post"
                c2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                # Badges Services
                s_list = str(row['Services']).split('|')
                s_html = ""
                for s in s_list:
                    if "Cantine" in s: s_html += f'<span class="badge bg-cantine">{s}</span>'
                    elif "Garderie" in s: s_html += f'<span class="badge bg-garderie">{s}</span>'
                    elif "Activités" in s: s_html += f'<span class="badge bg-activites">{s}</span>'
                c3.markdown(s_html, unsafe_allow_html=True)
                
                if c4.button("📝", key=f"ed_l_{row['Commune']}"): edit_popup(row['Commune'], p)
    st.markdown("</div>", unsafe_allow_html=True)
