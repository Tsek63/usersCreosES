import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Couleurs
color_creos = "#4169E1"
color_canard = "#008080"

st.markdown(f"""
    <style>
        #MainMenu, footer, header {{visibility: hidden;}}
        .main-header {{
            background-color: {color_creos};
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }}
        .stats-duck-blue {{
            background-color: {color_canard};
            color: white;
            border-radius: 10px;
            padding: 20px;
        }}
        .stat-badge {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 2px;
            margin-right: 8px;
        }}
    </style>
    <div class="main-header">
        <h2 style="margin:0;">Utilisateurs de Creos Extrascolaire</h2>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

# --- 3. ONGLETS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord", "✏️ Gestion des Communes"])

with tab2:
    # --- CALCULS DYNAMIQUES ---
    total = len(df)
    pre = len(df[df['Paiement'] == 'Prépaiement'])
    post = len(df[df['Paiement'] == 'Post-paiement'])
    
    # On compte les services dans la colonne 'Services'
    s_c_jour = df['Services'].str.contains("Cantine Jour", na=False).sum()
    s_c_sem = df['Services'].str.contains("Cantine Semaine", na=False).sum()
    s_c_mois = df['Services'].str.contains("Cantine Mois", na=False).sum()
    s_gard = df['Services'].str.contains("Garderie", na=False).sum()
    s_act = df['Services'].str.contains("Activités", na=False).sum()

    col_form, col_stats = st.columns([1.5, 1])

    with col_form:
        st.subheader("✏️ Gestion des données")
        st.write("Le formulaire de modification s'affiche ici.")
        # (Votre code de formulaire habituel peut être placé ici)

    with col_stats:
        # L'utilisation de f-string avec st.markdown(..., unsafe_allow_html=True) 
        # est cruciale pour que le code HTML soit "dessiné" et non "écrit".
        st.markdown(f"""
            <div class="stats-duck-blue">
                <div style="font-size: 0.9em; opacity: 0.8; text-transform: uppercase;">Total des communes actives</div>
                <div style="font-size: 3em; font-weight: bold; margin-bottom: 15px;">{total}</div>
                
                <div style="display: flex; gap: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.8em; font-weight: bold; margin-bottom: 10px;">PAIEMENT</div>
                        <div style="margin-bottom: 5px;"><span class="stat-badge" style="background:#fb923c"></span>Pré : <b>{pre}</b></div>
                        <div><span class="stat-badge" style="background:#38bdf8"></span>Post : <b>{post}</b></div>
                    </div>
                    <div style="flex: 1.2;">
                        <div style="font-size: 0.8em; font-weight: bold; margin-bottom: 10px;">SERVICES</div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#fb923c"></span>Cantine Jour : <b>{s_c_jour}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#f59e0b"></span>Cantine Semaine : <b>{s_c_sem}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#d97706"></span>Cantine Mois : <b>{s_c_mois}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#38bdf8"></span>Garderie : <b>{s_gard}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#4ade80"></span>Activités : <b>{s_act}</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
