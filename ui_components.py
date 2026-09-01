import streamlit as st

def is_province(name):
    """Détecte si le nom commence par Province"""
    return str(name).startswith("Province")

def icon_po(name):
    """Retourne l'icône 🏛️ pour une province ou 🏘️ pour une commune"""
    return "🏛️" if is_province(name) else "🏘️"

def audit_card(title, value, color, icon):
    """Crée une carte visuelle pour l'audit en bas du tableau de bord"""
    st.markdown(f"""
        <div style="background-color:white; border:1px solid #e2e8f0; border-left:5px solid {color}; padding:15px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-size:24px; margin-bottom:5px;">{icon}</div>
            <div style="font-size:12px; color:#64748b; font-weight:bold; text-transform:uppercase; letter-spacing:0.5px;">{title}</div>
            <div style="font-size:20px; font-weight:bold; color:#1e293b;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def inject_custom_css():
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; }
            #MainMenu, footer, header {visibility: hidden;}
            .main-header {
                background-color: #4169E1; padding: 15px 25px; border-radius: 10px;
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header-title { font-size: 24px; font-weight: bold; margin: 0; }

            /* --- CORRECTIF ULTIME POUR LE CALENDRIER --- */
            /* On cible le conteneur flottant (popover) qui contient le calendrier */
            div[data-baseweb="popover"] div[data-baseweb="calendar"] {
                background-color: #FFFFFF !important; /* Fond Blanc */
                color: #000000 !important; /* Texte Noir */
            }

            /* On force TOUS les éléments textes et icônes à être noirs à l'intérieur */
            div[data-baseweb="calendar"] *, 
            div[data-baseweb="calendar"] svg,
            div[data-baseweb="calendar"] button {
                color: #000000 !important;
                fill: #000000 !important;
            }

            /* On force le nom du mois et de l'année spécifiquement */
            div[data-baseweb="calendar"] header div {
                color: #000000 !important;
                font-weight: bold !important;
            }

            /* On garde le jour sélectionné en bleu avec le chiffre en blanc */
            div[data-baseweb="calendar"] [aria-selected="true"] {
                background-color: #4169E1 !important;
            }
            div[data-baseweb="calendar"] [aria-selected="true"] * {
                color: #FFFFFF !important;
            }
            
            /* Pour les jours "hors mois" (ex: fin du mois précédent) */
            div[data-baseweb="calendar"] [aria-disabled="true"] {
                color: #cccccc !important;
            }
        </style>
        <div class="main-header"><div class="header-title">Utilisateurs de Creos Extrascolaire</div></div>
    """, unsafe_allow_html=True)
