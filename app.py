import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Définition de la charte chromatique pour une réutilisation facile
COLORS = {
    "Cantine Jour": "#FFD700",    # Jaune
    "Cantine Semaine": "#FF8C00", # Orange
    "Cantine Mois": "#FF0000",    # Rouge
    "Garderie": "#38bdf8",        # Bleu ciel
    "Activités": "#4ade80",       # Vert
    "Prépaiement": "#ec4899",     # Rose
    "Post-paiement": "#38bdf8"    # Bleu
}

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

        /* Alignement vertical du bouton Reset */
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

# Sécurité : Si le DF est vide ou colonnes manquantes
if df_gsheets.empty or 'Paiement' not in df_gsheets.columns:
    df_gsheets = pd.DataFrame(columns=['Commune', 'Province', 'Paiement', 'Services'])

data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- 3. HEADER ---
st.markdown("""
    <div style="background-color: #4169E1; padding: 15px 25px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; color: white;">
        <div style="font-size: 24px; font-weight: bold;">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" style="background-color: white; color: #4169E1; padding: 8px 18px; border-radius: 5px; text-decoration: none; font-weight: bold;">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 4. TABS ---
tab_dash, tab_mgt = st.tabs(["📊 Tableau de Bord", "✏️ Gestion des Communes"])

with tab_mgt:
    col_f, col_s = st.columns([6, 4])
    with col_f:
        st.subheader("Ajouter ou Modifier")
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()))
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1: com_sel = st.selectbox("2. Commune", data_fwb[p_sel])
            with c2:
                pay_v = st.radio("3. Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            if st.form_submit_button("Enregistrer la Commune"):
                new_row = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_row], ignore_index=True)
                conn.update(data=df_u); st.rerun()

    with col_s:
        nt = len(df_gsheets)
        p_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement']) if nt > 0 else 0
        po_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement']) if nt > 0 else 0
        st.markdown(f"""
            <div style="background-color:#008080; padding:25px; border-radius:15px; color:white; text-align:center;">
                <div style="font-size:14px; opacity:0.8; margin-bottom:5px;">TOTAL COMMUNES ACTIVES</div>
                <div style="font-size:64px; font-weight:bold; line-height:1;">{nt}</div>
                <div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); margin-top:20px; padding-top:15px;">
                    <div><b style="color:{COLORS['Prépaiement']}; font-size:24px;">{p_stat}</b><br><small>Pré</small></div>
                    <div><b style="color:{COLORS['Post-paiement']}; font-size:24px;">{po_stat}</b><br><small>Post</small></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab_dash:
    if 'rc' not in st.session_state: st.session_state.rc = 0
    f1, f2, f3, f4 = st.columns([2, 1.5, 2, 0.8])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if nt > 0 else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")
    with f4:
        if st.button("❌ RESET", use_container_width=True): 
            st.session_state.rc += 1; st.rerun()

    df_filt = df_gsheets.copy()
    if fl_p: df_filt = df_filt[df_filt['Province'].isin(fl_p)]
    if fl_m: df_filt = df_filt[df_filt['Paiement'].isin(fl_m)]
    for s in fl_s: df_filt = df_filt[df_filt['Services'].str.contains(s, na=False)]
    df_sorted = df_filt.sort_values(['Province', 'Commune'])

    b_ex, b_pr, _ = st.columns([1.5, 1.5, 5])
    with b_ex:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df_sorted.to_excel(wr, index=False)
        st.download_button("📥 EXCEL", buf.getvalue(), "creos_export.xlsx", use_container_width=True)
    
    with b_pr:
        if st.button("📄 IMPRIMER", use_container_width=True):
            f_txt = f"Province: {', '.join(fl_p) if fl_p else 'Toutes'} | Paiement: {', '.join(fl_m) if fl_m else 'Tous'}"
            rows = ""
            for _, r in df_sorted.iterrows():
                p_c = COLORS['Prépaiement'] if r.Paiement == "Prépaiement" else COLORS['Post-paiement']
                rows += f"<tr><td><b>{r.Province}</b></td><td>{r.Commune}</td><td><b style='color:{p_c}'>{r.Paiement}</b></td><td>{r.Services.replace('|', ' • ')}</td></tr>"
            
            st.session_state.print_html = f"""
            <html><head><meta charset="UTF-8"><style>
                body {{ font-family: sans-serif; padding: 40px; }}
                .header-table {{ width: 100%; border-bottom: 4px solid #008080; margin-bottom: 20px; }}
                .logo {{ font-size: 32px; font-weight: bold; color: #4169E1; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background: #008080; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; }}
            </style></head><body>
                <table class="header-table"><tr>
                    <td class="logo">Creos Extrascolaire</td>
                    <td style="text-align:right;">Rapport du {pd.Timestamp.now().strftime('%d/%m/%Y')}</td>
                </tr></table>
                <div style="background:#f0f0f0; padding:10px; border-radius:5px; margin:10px 0;">{f_txt}</div>
                <table><thead><tr><th>Province</th><th>Commune</th><th>Paiement</th><th>Services</th></tr></thead>
                <tbody>{rows}</tbody></table>
                <script>window.onload = function() {{ window.print(); }}</script>
            </body></html>"""

    if 'print_html' in st.session_state:
        st.download_button("💾 TÉLÉCHARGER LE FICHIER D'IMPRESSION", st.session_state.print_html, "impression.html", "text/html", use_container_width=True)
        del st.session_state.print_html

    st.divider()
    
    c_l, c_v = st.columns([6, 4])
    with c_l:
        st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=500)
    
    with c_v:
        if not df_sorted.empty:
            fig_p = px.pie(df_sorted, names='Paiement', hole=0.4, title="Modes de Paiement",
                           color='Paiement', color_discrete_map={'Prépaiement': COLORS['Prépaiement'], 'Post-paiement': COLORS['Post-paiement']})
            st.plotly_chart(fig_p, use_container_width=True)

            all_s_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
            counts = [df_sorted['Services'].str.contains(s, na=False).sum() for s in all_s_list]
            
            fig_s = px.bar(x=all_s_list, y=counts, color=all_s_list, title="Services Actifs",
                           color_discrete_map={
                               "Cantine Jour": COLORS["Cantine Jour"],
                               "Cantine Semaine": COLORS["Cantine Semaine"],
                               "Cantine Mois": COLORS["Cantine Mois"],
                               "Garderie": COLORS["Garderie"],
                               "Activités": COLORS["Activités"]
                           })
            fig_s.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Nombre")
            st.plotly_chart(fig_s, use_container_width=True)
