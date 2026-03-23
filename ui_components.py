import streamlit as st

def icon_po(name):
    return "🏛️" if str(name).startswith("Province") else "🏘️"

def audit_card(title, value, color, icon):
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
        </style>
        <div class="main-header"><div class="header-title">Utilisateurs de Creos Extrascolaire</div></div>
    """, unsafe_allow_html=True)
