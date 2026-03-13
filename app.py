import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

COLORS = {
    "Cantine Jour": "#fb923c",
    "Cantine Semaine": "#f59e0b",
    "Cantine Mois": "#d97706",
    "Garderie": "#38bdf8",
    "Activités": "#4ade80",
    "Prépaiement": "#fb923c",
    "Post-paiement": "#38bdf8",
    "Bleu-Creos": "#4169E1",
    "Bleu-Canard": "#008080"
}

st.markdown(f"""
    <style>
        #MainMenu, footer, header {{visibility: hidden;}}
        .main-header {{
            background-color: {COLORS['Bleu-Creos']};
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            color: white;
        }}
        .header-title {{ font-size: 24px; font-weight: bold; margin: 0; }}
        .stats-duck-blue {{
            background-color: {COLORS['Bleu-Canard']};
            color: white;
            border-radius: 10px;
            padding: 20px;
        }}
        .stat-badge {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 3. ONGLETS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord", "✏️ Gestion des Communes"])

# (Partie Dashboard omise ici pour rester focalisé sur votre demande de stats)

with tab2:
    # --- CALCULS DYNAMIQUES (Les chiffres se mettent à jour ici) ---
    total_com = len(df_gsheets)
    pre_count = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    post_count = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    
    # Comptage automatique des services
    c_jour = df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum()
    c_sem = df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum()
    c_mois = df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum()
    garderie = df_gsheets['Services'].str.contains("Garderie", na=False).sum()
    activites = df_gsheets['Services'].str.contains("Activités", na=False).sum()

    col_form, col_stats = st.columns([1.5, 1])

    with col_form:
        st.subheader("✏️ Gestion des données")
        # ... (Votre formulaire habituel ici) ...
        st.info("Utilisez le formulaire pour ajouter ou modifier une commune.")

    with col_stats:
        # Affichage du bloc avec les variables dynamiques {total_com}, {pre_count}, etc.
        st.markdown(f"""
            <div class="stats-duck-blue">
                <div style="font-size: 0.85em; opacity: 0.9; text-transform: uppercase; letter-spacing:1px; margin-bottom: 5px;">Total des communes actives</div>
                <div style="font-size: 3.5em; font-weight: bold; margin-bottom: 20px;">{total_com}</div>
                
                <div style="display: flex; gap: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">PAIEMENT</div>
                        <div style="font-size: 0.95em; margin-bottom: 8px;"><span class="stat-badge" style="background:#fb923c"></span>Pré : <b>{pre_count}</b></div>
                        <div style="font-size: 0.95em;"><span class="stat-badge" style="background:#38bdf8"></span>Post : <b>{post_count}</b></div>
                    </div>
                    <div style="flex: 1.2;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">SERVICES</div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#fb923c"></span>Cantine Jour : <b>{c_jour}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#f59e0b"></span>Cantine Semaine : <b>{c_sem}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#d97706"></span>Cantine Mois : <b>{c_mois}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#38bdf8"></span>Garderie : <b>{garderie}</b></div>
                        <div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:#4ade80"></span>Activités : <b>{activites}</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
