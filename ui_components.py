import streamlit as st

def inject_style():
    st.markdown("""
        <style>
            .main-header { background:#4169E1; padding:15px; border-radius:10px; color:white; font-size:24px; font-weight:bold; margin-bottom:20px; }
            .school-card { background:white; border:1px solid #e2e8f0; border-left:5px solid #4169E1; border-radius:10px; padding:15px; margin-bottom:10px; }
            .badge { padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold; color:white; margin-right:4px; }
        </style>
        <div class="main-header">🏫 Creos Extrascolaire</div>
    """, unsafe_allow_html=True)

def get_badge(text, type_pay):
    color = "#ec4899" if "Pré" in str(type_pay) else "#38bdf8"
    return f'<span class="badge" style="background:{color}">{text}</span>'

def service_badges(services_str):
    colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
    html = ""
    for s in str(services_str).split("|"):
        if s.strip() and s.strip() != 'nan':
            html += f'<span class="badge" style="background:{colors.get(s.strip(),"#999")}">{s.strip()}</span>'
    return html
