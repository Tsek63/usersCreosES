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

# --- STYLE CSS (Texte Bleu Foncé & Badges Contrastés) ---
st.markdown(f"""
    <style>
    /* Fond de l'application */
    .stApp {{ background-color: #E3F2FD !important; }}
    
    /* TOUT LE TEXTE EN BLEU FONCÉ */
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ 
        color: #003366 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }}

    /* Cartes blanches pour le contraste */
    .white-card {{ 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 20px; 
        border: 1px solid #BEE3F8;
    }}

    /* CARTE : Points */
    .dot {{ 
        height: 14px; width: 14px; 
        border-radius: 4px; 
        border: 1px solid rgba(0,0,0,0.2); 
        display: inline-block; 
    }}

    /* BADGES : Texte foncé sur fond coloré (Image 3 & 5) */
    .badge {{ 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 11px; 
        font-weight: bold; 
        color: #003366 !important; /* Texte bleu foncé systématique */
        margin-right: 5px; 
        display: inline-flex; 
        align-items: center;
        border: 1px solid rgba(0,0,0,0.1);
    }}
    .bg-pre {{ background-color: #A9D0F5; }}      /* Bleu clair */
    .bg-post {{ background-color: #CBD5E0; }}     /* Gris perle */
    .bg-cantine {{ background-color: #FFD580; }}   /* Orange clair */
    .bg-garderie {{ background-color: #9DECF9; }}  /* Cyan clair */
    .bg-activites {{ background-color: #C6F6D5; }} /* Vert clair */

    /* Suppression du texte blanc par défaut de Streamlit */
    .stButton>button {{ color: #003366 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION & FILTRAGE DYNAMIQUE ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- POP-UP MODIFIER / SUPPRIMER ---
@st.dialog("Configuration", width="small")
def edit_popup(name, prov):
    st.markdown(f"### :blue[{name}]")
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
        updated_df = pd.concat([df_db[df_db['Commune'] != name], new_data], ignore_index=True)
        conn.update(data=updated_df)
        st.rerun()
    
    if c2.button("ANNULER", use_container_width=True):
        st.rerun()

    if not existing_row.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ SUPPRIMER CETTE COMMUNE", use_container_width=True):
            updated_df = df_db[df_db['Commune'] != name]
            conn.update(data=updated_df)
            st.rerun()

# --- INTERFACE ---
col_map, col_list = st.columns([0.38, 0.62])

with col_map:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.subheader("LÉGENDE & CARTE")
    
    # Légende avec texte foncé
    l1, l2 = st.columns(2)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        (l1 if i < 3 else l2).markdown(f"<span style='color:{c}; font-size:20px;'>■</span> <span style='color:#003366'>{p}</span>", unsafe_allow_html=True)
    
    st.markdown("<br><b>SITUATION GÉOGRAPHIQUE</b>", unsafe_allow_html=True)
    
    # Génération des points (doit boucler sur votre référentiel de 281 communes)
    # Pour l'exemple, j'affiche les communes déjà encodées dans la Sheet
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<small><b>{prov}</b></small>", unsafe_allow_html=True)
        p_data = df_db[df_db['Province'] == prov]
        grid = st.columns(12)
        for idx, (_, row) in enumerate(p_data.iterrows()):
            with grid[idx % 12]:
                if st.button(" ", key=f"dot_{row['Commune']}"):
                    edit_popup(row['Commune'], prov)
                st.markdown(f"<div class='dot' style='background-color:{color}; border: 1.5px solid #003366; margin-top:-28px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_list:
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    st.title("Utilisateurs Creos Extrascolaire")
    
    # Filtres
    f_prov = st.selectbox("Provinces", ["Toutes les Provinces"] + list(PROV_COLORS.keys()))
    
    df_filtered = df_db.copy()
    if f_prov != "Toutes les Provinces":
        df_filtered = df_filtered[df_filtered['Province'] == f_prov]

    # Liste détaillée
    for prov in (PROV_COLORS.keys() if f_prov == "Toutes les Provinces" else [f_prov]):
        p_rows = df_filtered[df_filtered['Province'] == prov].sort_values("Commune")
        if not p_rows.empty:
            st.markdown(f"<h4 style='color:#003366; border-bottom:2px solid #A9D0F5; padding-top:10px;'>{prov.upper()}</h4>", unsafe_allow_html=True)
            for _, row in p_rows.iterrows():
                c1, c2, c3, c4 = st.columns([0.3, 0.2, 0.4, 0.1])
                c1.write(f"**{row['Commune']}**")
                
                # Badges avec texte foncé
                p_cls = "bg-pre" if row['Paiement'] == "Prépaiement" else "bg-post"
                c2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                servs = str(row['Services']).split('|')
                s_html = ""
                for s in servs:
                    if "Cantine" in s: s_html += f'<span class="badge bg-cantine">{s}</span>'
                    elif "Garderie" in s: s_html += f'<span class="badge bg-garderie">{s}</span>'
                    elif "Activités" in s: s_html += f'<span class="badge bg-activites">{s}</span>'
                c3.markdown(s_html, unsafe_allow_html=True)
                
                if c4.button("📝", key=f"edit_list_{row['Commune']}"):
                    edit_popup(row['Commune'], prov)
    st.markdown("</div>", unsafe_allow_html=True)
