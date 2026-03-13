import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# CSS : Alignement Reset + Couleurs boutons
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Boutons Bleu Canard */
        div.stButton > button:not(.reset-btn), div.stDownloadButton > button {
            background-color: #008080 !important;
            color: white !important;
            border: none !important;
            height: 3em !important;
        }
        
        /* Bouton Reset Rouge */
        .reset-btn {
            background-color: #ff4b4b !important;
            color: white !important;
            border: none !important;
        }

        /* Alignement vertical du bouton Reset avec les filtres */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES & CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 3. HEADER ---
st.markdown("""
    <div style="background-color: #4169E1; padding: 15px 25px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; color: white;">
        <div style="font-size: 24px; font-weight: bold;">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" style="background-color: white; color: #4169E1; padding: 8px 18px; border-radius: 5px; text-decoration: none; font-weight: bold;">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 4. FILTRES ALIGNÉS ---
if 'rc' not in st.session_state: st.session_state.rc = 0

f1, f2, f3, f4 = st.columns([2, 1.5, 2, 0.8])
with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")
with f4:
    if st.button("❌ RESET", use_container_width=True, help="Réinitialiser les filtres"): 
        st.session_state.rc += 1
        st.rerun()

# --- 5. LOGIQUE DE FILTRAGE ---
df_filtered = df_gsheets.copy()
if fl_p: df_filtered = df_filtered[df_filtered['Province'].isin(fl_p)]
if fl_m: df_filtered = df_filtered[df_filtered['Paiement'].isin(fl_m)]
for s in fl_s: df_filtered = df_filtered[df_filtered['Services'].str.contains(s, na=False)]
df_sorted = df_filtered.sort_values(['Province', 'Commune'])

# --- 6. ACTIONS EXPORT (SOUS LES FILTRES) ---
st.write("") # Petit espacement
b_exp1, b_exp2, _ = st.columns([1.5, 1.5, 5])

with b_exp1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_sorted.to_excel(writer, index=False)
    st.download_button("📥 EXPORTER EXCEL", buffer.getvalue(), "creos_export.xlsx", use_container_width=True)

with b_exp2:
    if st.button("📄 GÉNÉRER IMPRESSION", use_container_width=True):
        # Construction du rapport HTML détaillé
        f_info = f"Filtres : Province ({', '.join(fl_p) if fl_p else 'Toutes'}) | Mode ({', '.join(fl_m) if fl_m else 'Tous'})"
        
        rows = ""
        for _, r in df_sorted.iterrows():
            pay_color = "#ec4899" if r.Paiement == "Prépaiement" else "#38bdf8"
            serv_styled = r.Services.replace('|', ' • ')
            rows += f"<tr><td><b>{r.Province}</b></td><td>{r.Commune}</td><td><b style='color:{pay_color}'>{r.Paiement}</b></td><td>{serv_styled}</td></tr>"
        
        st.session_state.print_html = f"""
        <html><head><meta charset="UTF-8"><style>
            body {{ font-family: 'Segoe UI', sans-serif; padding: 30px; }}
            .header {{ color: #4169E1; border-bottom: 3px solid #008080; padding-bottom: 10px; }}
            .filters {{ background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 14px; border-left: 5px solid #008080; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #008080; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style></head><body>
            <div class="header"><h1>Rapport Creos Extrascolaire</h1></div>
            <div class="filters"><b>{f_info}</b><br>Total : {len(df_sorted)} commune(s)</div>
            <table><thead><tr><th>Province</th><th>Commune</th><th>Mode de Paiement</th><th>Services Actifs</th></tr></thead>
            <tbody>{rows}</tbody></table>
            <script>window.onload = function() {{ window.print(); }}</script>
        </body></html>"""

if 'print_html' in st.session_state:
    st.download_button("💾 TÉLÉCHARGER LE FICHIER D'IMPRESSION", st.session_state.print_html, "impression_creos.html", "text/html", use_container_width=True)
    del st.session_state.print_html

# --- 7. AFFICHAGE : LISTE & GRAPHIQUES ---
st.divider()
c_list, c_viz = st.columns([6, 4])

with c_list:
    st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=500)

with c_viz:
    if not df_sorted.empty:
        # Pie Chart avec les couleurs exactes
        fig_p = px.pie(df_sorted, names='Paiement', hole=0.4, title="Modes de Paiement",
                       color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
        fig_p.update_layout(height=280, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_p, use_container_width=True)

        # Bar Chart avec les couleurs exactes
        all_s = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
        counts = [df_sorted['Services'].str.contains(s, na=False).sum() for s in all_s]
        df_bars = pd.DataFrame({'Service': all_s, 'Nombre': counts})
        
        fig_s = px.bar(df_bars, x='Service', y='Nombre', color='Service', title="Services Actifs",
                       color_discrete_map={
                           "Cantine Jour": "#ec4899", "Cantine Semaine": "#db2777",
                           "Cantine Mois": "#be185d", "Garderie": "#38bdf8", "Activités": "#4ade80"
                       })
        fig_s.update_layout(height=280, showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_s, use_container_width=True)
