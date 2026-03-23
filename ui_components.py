import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
            /* Supprime l'espace blanc en haut */
            .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
            #MainMenu, footer, header {visibility: hidden;}
            
            .main-header {
                background-color: #4169E1;
                padding: 15px 25px;
                border-radius: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        </style>
        <div class="main-header">
            <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        </div>
    """, unsafe_allow_html=True)
