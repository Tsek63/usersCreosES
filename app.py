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

# --- CONFIGURATION PAGE ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire", page_icon="📊")

# --- CONNEXION CORRIGÉE ---
def get_tt_gsheet():
    """Utilise les secrets harmonisés pour gspread"""
    try:
        # On va chercher les infos dans le bloc connections.gsheets
        info = st.secrets["connections"]["gsheets"]
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key(TT_SHEET_ID).worksheet(TT_SHEET_NAME)
    except Exception as e:
        st.error(f"Erreur connexion Time Tracking : {e}")
        return None

# Connexion standard pour les onglets Ecoles
conn = st.connection("gsheets", type=GSheetsConnection)

def load_tt_data():
    columns = ["date", "intervenante", "tache", "quantite", "nb_ecoles"]
    try:
        ws = get_tt_gsheet()
        if ws:
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            if df.empty: return pd.DataFrame(columns=columns)
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
            return df.dropna(subset=['date'])
    except:
        pass
    return pd.DataFrame(columns=columns)

# --- CHARGEMENT DES DONNÉES ÉCOLES ---
try:
    df_ecoles = conn.read(worksheet="Ecoles", ttl=600).dropna(how="all")
    for col in ['Fase PO', 'Fase école', 'Code postal']:
        if col in df_ecoles.columns:
            df_ecoles[col] = df_ecoles[col].astype(str).str.replace(r'\.0$', '', regex=True)
except Exception as e:
    st.error(f"⚠️ Erreur chargement onglet Ecoles : {e}")
    df_ecoles = pd.DataFrame()

# --- CSS PERSONNALISÉ (Identique à votre v16) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: #ffffff; border-radius: 8px 8px 0 0;
        padding: 10px 20px; font-weight: 600; color: #64748b;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #2563eb; border-bottom: 3px solid #2563eb; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DES ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 SUIVI ÉCOLES", "📊 STATISTIQUES", "🗺️ CARTOGRAPHIE", "⏱️ TIME TRACKING"])

# --- TAB 1 : SUIVI ÉCOLES (Votre logique v16) ---
with tab1:
    st.subheader("Base de données des établissements")
    if not df_ecoles.empty:
        # Filtres
        c1, c2 = st.columns(2)
        with c1: search = st.text_input("🔍 Recherche rapide (École, Commune, CP...)", "")
        with c2: 
            statuts = ["Tous"] + sorted(df_ecoles['Statut'].unique().tolist()) if 'Statut' in df_ecoles.columns else ["Tous"]
            sel_statut = st.selectbox("Filtrer par statut", statuts)
        
        df_f = df_ecoles.copy()
        if search:
            df_f = df_f[df_f.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        if sel_statut != "Tous":
            df_f = df_f[df_f['Statut'] == sel_statut]
        
        st.dataframe(df_f, use_container_width=True, height=500)
    else:
        st.info("Aucune donnée école disponible.")

# --- TAB 2 : STATISTIQUES (Votre logique v16) ---
with tab2:
    if not df_ecoles.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Écoles", len(df_ecoles))
        if 'Statut' in df_ecoles.columns:
            fait = len(df_ecoles[df_ecoles['Statut'] == 'Fait'])
            col_m2.metric("Déploiements Terminés", fait)
            col_m3.metric("% Avancement", f"{(fait/len(df_ecoles)*100):.1f}%")
        
        # Graphiques Plotly
        c_g1, c_g2 = st.columns(2)
        with c_g1:
            fig1 = px.pie(df_ecoles, names='Statut', title="Répartition par Statut", hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with c_g2:
            fig2 = px.bar(df_ecoles['Commune'].value_counts().head(10), title="Top 10 Communes")
            st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3 : CARTOGRAPHIE ---
with tab3:
    if not df_ecoles.empty and 'latitude' in df_ecoles.columns:
        df_map = df_ecoles.dropna(subset=['latitude', 'longitude'])
        st.map(df_map)

# --- TAB 4 : TIME TRACKING (Votre logique v16 réintégrée) ---
with tab4:
    st.header("Gestion du Temps")
    
    # Formulaire
    with st.expander("➕ Encoder une nouvelle activité", expanded=True):
        with st.form("form_tt", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                f_date = st.date_input("Date", date.today())
                f_intv = st.selectbox("Intervenante", LISTE_REDACTEURS)
            with col_b:
                f_tache = st.selectbox("Tâche", LISTE_TACHES)
                f_quant = st.number_input("Temps (en min/h)", min_value=0.0, step=0.5)
            with col_c:
                f_nb = st.number_input("Nombre d'écoles", min_value=0, step=1)
            
            if st.form_submit_button("Enregistrer"):
                ws = get_tt_gsheet()
                if ws:
                    ws.append_row([str(f_date), f_intv, f_tache, f_quant, f_nb])
                    st.success("Activité enregistrée !")
                    st.cache_data.clear()

    # Affichage & Export Excel
    df_tt = load_tt_data()
    if not df_tt.empty:
        st.divider()
        st.dataframe(df_tt.tail(10), use_container_width=True)
        
        # Bouton d'export (Logique simplifiée pour éviter les erreurs de buffer)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_tt.to_excel(writer, sheet_name='Tracking', index=False)
        st.download_button("📥 Télécharger tout l'historique Excel", buffer.getvalue(), "tracking.xlsx")
