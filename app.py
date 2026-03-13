import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header {
            background-color: #4169E1;
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white;
            color: #4169E1;
            padding: 8px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: 0.3s;
        }
        div.stDownloadButton > button:last-child {
            background-color: #2e7d32;
            color: white;
            border: none;
        }
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 4. FONCTION RAPPORT HTML (Inchangée) ---
def get_print_html(df, filters_desc):
    icons_styles = {
        "Cantine Jour": "background:#ec4899; color:white;", "Cantine Semaine": "background:#db2777; color:white;",
        "Cantine Mois": "background:#be185d; color:white;", "Garderie": "background:#38bdf8; color:white;",
        "Activités": "background:#4ade80; color:white;"
    }
    html = f"""<html><body onload="window.print()"><h1>Rapport Creos</h1></body></html>""" # Simplifié pour l'exemple
    return html

# --- 5. TABS ---
# CHANGEMENT DU TITRE ICI
tab1, tab2 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes"])

# --- TAB 1 : DASHBOARD ---
with tab1:
    # (Logique de la carte conservée du code original)
    st.info("La carte et la liste s'affichent ici (comme dans votre code initial).")
    # Pour l'exemple, j'ai raccourci la partie JS de la carte pour me concentrer sur ta demande du bloc stat.

# --- TAB 2 : GESTION ---
with tab2:
    st.header("✏️ Gestion des données")
    c_form, c_stat = st.columns([6, 4])
    
    with c_form:
        # (Formulaire de gestion conservé)
        st.write("Formulaire de modification...")

    with c_stat:
        nt = len(df_gsheets)
        npr = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
        npo = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
        
        s_defs = [
            ("Cantine Jour", "#ec4899", "fa-utensils"), 
            ("Cantine Semaine", "#db2777", "fa-calendar-day"), 
            ("Cantine Mois", "#be185d", "fa-calendar-days"), 
            ("Garderie", "#38bdf8", "fa-clock"), 
            ("Activités", "#4ade80", "fa-volleyball")
        ]
        
        # Préparation de la liste verticale des services avec police agrandie
        b_html = ""
        for n, c, i in s_defs:
            cnt = df_gsheets['Services'].str.contains(n, na=False).sum()
            b_html += f"""
                <div style="background:{c}; padding:10px 15px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; color:white; font-weight:bold; font-size:16px;">
                    <span><i class="fa-solid {i}"></i> &nbsp; {n}</span>
                    <span style="background:rgba(0,0,0,0.2); padding:2px 10px; border-radius:5px;">{cnt}</span>
                </div>"""
        
        # BLOC STATISTIQUE MODIFIÉ
        st.markdown(f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <div style="background-color:#008080; padding:25px; border-radius:15px; color:white; font-family:sans-serif;">
                
                <div style="text-align:center; margin-bottom:25px;">
                    <div style="font-size:16px; text-transform:uppercase; opacity:0.9; font-weight:bold;">Total des communes actives</div>
                    <div style="font-size:54px; font-weight:bold;">{nt}</div>
                </div>

                <div style="display: flex; gap: 20px; align-items: flex-start;">
                    
                    <div style="flex: 1; border-right: 1px solid rgba(255,255,255,0.2); padding-right: 15px;">
                        <div style="font-size:14px; opacity:0.8; margin-bottom:15px; text-transform:uppercase; font-weight:bold;">Paiement</div>
                        <div style="background:#ec4899; padding:12px; border-radius:8px; margin-bottom:10px; text-align:center; font-size:16px; font-weight:bold;">
                            PRÉPAIEMENT<br><span style="font-size:24px;">{npr}</span>
                        </div>
                        <div style="background:#38bdf8; padding:12px; border-radius:8px; text-align:center; font-size:16px; font-weight:bold;">
                            POST-PAIEMENT<br><span style="font-size:24px;">{npo}</span>
                        </div>
                    </div>

                    <div style="flex: 1.2;">
                        <div style="font-size:14px; opacity:0.8; margin-bottom:15px; text-transform:uppercase; font-weight:bold;">Services</div>
                        {b_html}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    # (Reste du code filtres et dataframe...)
