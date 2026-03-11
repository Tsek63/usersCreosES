import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- COULEURS DES PROVINCES ---
PROV_COLORS = {
    "Bruxelles": "#FFF2CC", "Brabant Wallon": "#D1F7F4", "Hainaut": "#D9D7FF",
    "Liège": "#CCE5FF", "Namur": "#FFD9CC", "Luxembourg": "#FFC9F3"
}

# --- STYLE CSS (Fond bleu, points, badges) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E3F2FD !important; }}
    .white-card {{ background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
    .dot {{ height: 14px; width: 14px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.1); display: inline-block; }}
    .badge {{ padding: 4px 12px; border-radius: 15px; font-size: 11px; font-weight: bold; color: white; margin-right: 5px; display: inline-flex; align-items: center; }}
    .bg-pre {{ background-color: #4A90E2; }} .bg-post {{ background-color: #34495E; }}
    .bg-cantine {{ background-color: #F39C12; }} .bg-garderie {{ background-color: #00C2FF; }} .bg-activites {{ background-color: #2ECC71; }}
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- RÉFÉRENTIEL DES 281 COMMUNES (Statique pour la structure de la carte) ---
@st.cache_data
def get_ref_communes():
    # Insérez ici votre dictionnaire complet des 281 communes
    # Pour l'exemple, j'utilise une structure simplifiée
    data = {
        "Bruxelles": ["Evere", "Uccle", "Anderlecht"],
        "Liège": ["Baelen", "Spa", "Huy"],
        # ... à compléter avec les 281 noms
    }
    return [{"name": n, "prov": p} for p, names in data.items() for n in names]

all_ref = get_ref_communes()

# --- POP-UP MODIFIER / SUPPRIMER ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
    # On cherche si la commune existe déjà dans votre Google Sheet
    existing_row = df_db[df_db['Commune'] == name]
    
    val_pay = existing_row['Paiement'].iloc[0] if not existing_row.empty else "Prépaiement"
    val_serv = str(existing_row['Services'].iloc[0]).split('|') if not existing_row.empty else []

    pay = st.radio("Paiement", ["Prépaiement", "Post-paiement"], index=0 if val_pay == "Prépaiement" else 1, horizontal=True)
    
    st.write("**Services**")
    s1 = st.checkbox("Cantine Jour", value="Cantine Jour" in val_serv)
    s2 = st.checkbox("Cantine Semaine", value="Cantine Semaine" in val_serv)
    s3 = st.checkbox("Garderie", value="Garderie" in val_serv)
    s4 = st.checkbox("Activités", value="Activités" in val_serv)
    
    selected_services = [s for s, val in zip(["Cantine Jour", "Cantine Semaine", "Garderie", "Activités"], [s1, s2, s3, s4]) if val]

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("VALIDER", type="primary", use_container_width=True):
        new_data = pd.DataFrame([[name, prov, pay, "|".join(selected_services)]], columns=["Commune", "Province", "Paiement", "Services"])
        # Mise à jour : on enlève l'ancienne ligne et on ajoute la nouvelle
        updated_df = pd.concat([df_db[df_db['Commune'] != name], new_data], ignore_index=True)
        conn.update(data=updated_df)
        st.rerun()
    
    if c2.button("ANNULER", use_container_width=True):
        st.rerun()

    if not existing_row.empty:
        st.write("---")
        if st.button("🗑️ Supprimer cette commune", type="secondary", use_container_width=True):
            updated_df = df_db[df_db['Commune'] != name]
            conn.update(data=updated_df)
            st.rerun()

# --- INTERFACE ---
col_map, col_list = st.columns([0.38, 0.62])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    # Légende
    l1, l2 = st.columns(2)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        (l1 if i < 3 else l2).markdown(f"<span style='color:{c}; font-size:18px;'>■</span> {p}", unsafe_allow_html=True)
    
    # Carte
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<small><b>{prov}</b></small>", unsafe_allow_html=True)
        coms = [c for c in all_ref if c['prov'] == prov]
        grid = st.columns(12)
        for idx, com in enumerate(coms):
            # Si la commune est dans la Google Sheet, on peut mettre un contour noir au point
            is_active = not df_db[df_db['Commune'] == com['name']].empty
            with grid[idx % 12]:
                if st.button(" ", key=f"dot_{com['name']}"):
                    edit_popup(com['name'], prov)
                border = "2px solid black" if is_active else "1px solid rgba(0,0,0,0.1)"
                st.markdown(f"<div class='dot' style='background-color:{color}; border:{border}; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # FILTRES DYNAMIQUES
    f_prov = st.selectbox("Provinces", ["Toutes les Provinces"] + list(PROV_COLORS.keys()))
    f_pay = st.selectbox("Paiements", ["Tous", "Prépaiement", "Post-paiement"])
    
    # Filtrage du DataFrame de la Google Sheet
    df_filtered = df_db.copy()
    if f_prov != "Toutes les Provinces":
        df_filtered = df_filtered[df_filtered['Province'] == f_prov]
    if f_pay != "Tous":
        df_filtered = df_filtered[df_filtered['Paiement'] == f_pay]

    # Liste
    for prov in (PROV_COLORS.keys() if f_prov == "Toutes les Provinces" else [f_prov]):
        p_data = df_filtered[df_filtered['Province'] == prov].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<h4 style='color:#4A90E2; border-bottom:1px solid #eee; padding-top:15px;'>{prov.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                c1, c2, c3, c4 = st.columns([0.3, 0.2, 0.4, 0.1])
                c1.write(f"**{row['Commune']}**")
                p_class = "bg-pre" if row['Paiement'] == "Prépaiement" else "bg-post"
                c2.markdown(f'<span class="badge {p_class}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                # Badges services
                servs = str(row['Services']).split('|')
                serv_html = "".join([f'<span class="badge bg-garderie">{s}</span>' for s in servs if s and s != 'nan'])
                c3.markdown(serv_html, unsafe_allow_html=True)
                
                if c4.button("📝", key=f"btn_edit_{row['Commune']}"):
                    edit_popup(row['Commune'], prov)
    st.markdown("</div>", unsafe_allow_html=True)
