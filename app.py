import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import base64
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# --- CONFIGURATION & IDENTIFIANTS ---
TT_SHEET_ID = "1Eu-k4-jGVfRVNYJcCKV_dIlqkIFaRUK-J5rtV0c6z8E"
TT_SHEET_NAME = "Data"

LISTE_REDACTEURS = ["Véronique Maigrié", "Sylvie Nyssen"]
COULEURS_MAP = {"Véronique Maigrié": "#FF00FF", "Sylvie Nyssen": "#008080"}
LISTE_TACHES = [
    "DEPANNAGE TELEPHONIQUE", "DEPANNAGE MAIL", "SUIVI DEPLOIEMENT TELEPHONIQUE",
    "SUIVI DEPLOIEMENT MAIL", "VISIO DE PRESENTATION", "VISIO DIVERS",
    "MAIL DIVERS", "MODIFICATIONS FICHIER PO", "JOURNEE DE FORMATION",
    "SUIVI ADMIN FORMATION", "MATINEE D'ACCOMPAGNEMENT",
    "SUIVI MATINEE D'ACCOMPAGNEMENT", "ENCODAGE TICKET", "SUIVI FICHIER TICKETS",
    "MODIFICATION - CREATION DOC", "MODIFICATION – CREATION VIDEO",
    "NETTOYAGES DES DONNEES CREOS", "Briefing DEV"
]

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire", page_icon="📊")

# --- FONCTIONS DE CONNEXION ---
@st.cache_resource
def get_tt_gsheet():
    """Connexion via gspread pour l'écriture (Time Tracking)"""
    try:
        # On récupère les infos directement depuis le bloc connections.gsheets
        creds_info = st.secrets["connections"]["gsheets"]
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key(TT_SHEET_ID).worksheet(TT_SHEET_NAME)
    except Exception as e:
        st.error(f"Erreur connexion Gspread : {e}")
        return None

# Initialisation de la connexion standard Streamlit (Lecture seule / Cache)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_tt_data():
    """Charge les données du Time Tracking"""
    try:
        ws = get_tt_gsheet()
        if ws:
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
                return df.dropna(subset=['date'])
    except:
        pass
    return pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])

# --- CHARGEMENT DES DONNÉES ÉCOLES (ONGLET 1, 2, 3) ---
try:
    df_ecoles = conn.read(worksheet="Ecoles", ttl=600).dropna(how="all")
    # Nettoyage des codes FASE et CP
    for col in ['Fase PO', 'Fase école', 'Code postal']:
        if col in df_ecoles.columns:
            df_ecoles[col] = df_ecoles[col].astype(str).str.replace(r'\.0$', '', regex=True)
except Exception as e:
    st.error(f"⚠️ Erreur de lecture de l'onglet 'Ecoles' : {e}")
    df_ecoles = pd.DataFrame()

# --- INTERFACE PRINCIPALE ---
st.title("📊 Creos Extrascolaire - Pilotage")

tab1, tab2, tab3, tab4 = st.tabs(["🏫 Suivi Écoles", "📈 Statistiques", "🗺️ Cartographie", "⏱️ Time Tracking"])

# --- TAB 1 : SUIVI ÉCOLES ---
with tab1:
    if not df_ecoles.empty:
        st.subheader("Base de données des écoles")
        # Filtres simples
        search = st.text_input("Rechercher une école ou une commune :")
        if search:
            mask = df_ecoles.apply(lambda r: search.lower() in str(r).lower(), axis=1)
            display_df = df_ecoles[mask]
        else:
            display_df = df_ecoles
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Chargez des données dans l'onglet 'Ecoles' de votre Google Sheet.")

# --- TAB 2 : STATISTIQUES ---
with tab2:
    st.subheader("Analyse globale")
    if not df_ecoles.empty:
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            if 'Statut' in df_ecoles.columns:
                fig_statut = px.pie(df_ecoles, names='Statut', title="Répartition par Statut", hole=0.4)
                st.plotly_chart(fig_statut)
        with col_stat2:
            if 'Réseau' in df_ecoles.columns:
                fig_reseau = px.bar(df_ecoles['Réseau'].value_counts(), title="Nombre d'écoles par Réseau")
                st.plotly_chart(fig_reseau)
    else:
        st.warning("Données insuffisantes pour les statistiques.")

# --- TAB 3 : CARTOGRAPHIE ---
with tab3:
    st.subheader("Géolocalisation des implantations")
    if not df_ecoles.empty and 'latitude' in df_ecoles.columns and 'longitude' in df_ecoles.columns:
        # Nettoyage coordonnées
        df_map = df_ecoles.dropna(subset=['latitude', 'longitude'])
        st.map(df_map)
    else:
        st.info("Les colonnes 'latitude' et 'longitude' sont nécessaires pour afficher la carte.")

# --- TAB 4 : TIME TRACKING ---
with tab4:
    st.header("⏱️ Gestion du Temps")
    
    # Formulaire d'encodage
    with st.expander("➕ Enregistrer une nouvelle activité", expanded=True):
        with st.form("tt_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("Date", date.today())
                f_intv = st.selectbox("Intervenante", LISTE_REDACTEURS)
            with c2:
                f_tache = st.selectbox("Tâche", LISTE_TACHES)
                f_quant = st.number_input("Quantité (minutes/heures)", min_value=0.0, step=0.5)
            with c3:
                f_nb = st.number_input("Nb écoles impactées", min_value=0, step=1)
            
            if st.form_submit_button("Valider l'encodage"):
                ws = get_tt_gsheet()
                if ws:
                    ws.append_row([str(f_date), f_intv, f_tache, f_quant, f_nb])
                    st.success("Données envoyées avec succès !")
                    st.cache_data.clear()

    # Visualisation et Export
    st.divider()
    df_tt = load_tt_data()
    if not df_tt.empty:
        # Filtres de période
        col_f1, col_f2 = st.columns(2)
        with col_f1: start_d = st.date_input("Depuis le", df_tt['date'].min())
        with col_f2: end_d = st.date_input("Jusqu'au", date.today())
        
        mask_tt = (df_tt['date'] >= start_d) & (df_tt['date'] <= end_d)
        df_filtered = df_tt[mask_tt]

        st.subheader("Historique filtré")
        st.dataframe(df_filtered, use_container_width=True)
        
        # Petit résumé graphique
        fig_tt = px.bar(df_filtered, x='tache', y='quantite', color='intervenante', 
                        title="Temps passé par tâche", barmode='group',
                        color_discrete_map=COULEURS_MAP)
        st.plotly_chart(fig_tt, use_container_width=True)
    else:
        st.info("Aucune donnée de tracking pour le moment.")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: #ffffff; 
        border-radius: 5px; padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)
