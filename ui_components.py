import streamlit as st

def is_province(name):
    return str(name).startswith("Province")

def icon_po(name):
    return "🏛️" if is_province(name) else "🏘️"

def audit_card(title, value, color, icon):
    st.markdown(f"""
        <div style="background-color:white; border:1px solid #e2e8f0; border-left:5px solid {color}; padding:15px; border-radius:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-size:24px; margin-bottom:5px;">{icon}</div>
            <div style="font-size:12px; color:#64748b; font-weight:bold; text-transform:uppercase;">{title}</div>
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
                margin-bottom: 15px; color: white;
            }
            .header-title { font-size: 24px; font-weight: bold; margin: 0; }

            /* --- CORRECTIF CALENDRIER --- */
            /* Force tous les éléments du calendrier en blanc pour être visibles sur fond noir */
            div[data-baseweb="calendar"] * {
                color: white !important;
                fill: white !important;
            }
        </style>
        <div class="main-header"><div class="header-title">Utilisateurs de Creos Extrascolaire</div></div>
    """, unsafe_allow_html=True)
