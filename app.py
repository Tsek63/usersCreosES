import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        .main-header {
            background-color: #4169E1; padding: 15px 25px; border-radius: 10px;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white; color: #4169E1; padding: 8px 18px;
            border-radius: 5px; text-decoration: none; font-weight: bold;
        }
        /* Style pour le bouton Excel Bleu Canard */
        div.stDownloadButton > button {
            background-color: #008080 !important; color: white !important;
            border: none !important; width: 100% !important; height: 45px;
        }
        /* Style pour le bouton Impression */
        .print-btn {
            background-color: #6c757d; color: white; border: none;
            padding: 10px; border-radius: 5px; width: 100%; cursor: pointer;
            font-weight: bold; height: 45px; display: flex; align-items: center; justify-content: center; gap: 10px;
        }
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES ---
data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

tab1, tab2 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes"])

# --- TAB 1 (Carte) : Code identique au précédent ---
with tab1:
    # (Affichage de la carte et des statistiques résumé comme précédemment...)
    pass 

# --- TAB 2 : GESTION ET LISTE ---
with tab2:
    # 1. Haut de page (Formulaire et Statistique circulaire)
    c_form, c_stat = st.columns([6, 4])
    with c_form:
        st.subheader("Modifier une commune")
        p_sel = st.selectbox("Province", list(data_fwb.keys()), key="m_p")
        with st.form("edit_form"):
            f1, f2 = st.columns(2)
            with f1: com_sel = st.selectbox("Commune", data_fwb[p_sel])
            with f2:
                pay_v = st.radio("Mode", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            if st.form_submit_button("💾 Sauvegarder"):
                new_r = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_r], ignore_index=True)
                conn.update(data=df_u); st.rerun()

    # 2. Zone Filtres
    st.divider()
    if 'rc' not in st.session_state: st.session_state.rc = 0
    
    col_t, col_r = st.columns([7, 3])
    with col_t: st.subheader("🔍 Filtres & Liste filtrée")
    with col_r:
        st.write("##")
        if st.button("❌ Effacer les filtres", use_container_width=True):
            st.session_state.rc += 1; st.rerun()

    f1, f2, f3 = st.columns([2, 1, 2])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")

    df_r = df_gsheets.copy()
    if not df_r.empty:
        if fl_p: df_r = df_r[df_r['Province'].isin(fl_p)]
        if fl_m: df_r = df_r[df_r['Paiement'].isin(fl_m)]
        if fl_s:
            for s in fl_s: df_r = df_r[df_r['Services'].str.contains(s, na=False)]
        
        df_sorted = df_r.sort_values(['Province', 'Commune'])

        # --- BOUTONS EXPORT ET IMPRESSION ---
        st.write("##")
        b_excel, b_print = st.columns(2)
        
        with b_excel:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_sorted.to_excel(writer, index=False, sheet_name='Export')
            st.download_button(label="📥 Exporter vers Excel", data=buffer.getvalue(), file_name="creos_export.xlsx", use_container_width=True)

        with b_print:
            # Préparation du contenu HTML pour l'impression
            filter_info = f"<b>Provinces:</b> {', '.join(fl_p) if fl_p else 'Toutes'} | <b>Paiement:</b> {', '.join(fl_m) if fl_m else 'Tous'} | <b>Services:</b> {', '.join(fl_s) if fl_s else 'Tous'}"
            
            table_html = ""
            for prov in sorted(df_sorted['Province'].unique()):
                table_html += f"<tr style='background:#f2f2f2;'><td colspan='3'><b>Province : {prov}</b></td></tr>"
                prov_df = df_sorted[df_sorted['Province'] == prov].sort_values('Commune')
                for _, row in prov_df.iterrows():
                    table_html += f"<tr><td>{row['Commune']}</td><td>{row['Paiement']}</td><td>{row['Services'].replace('|', ', ')}</td></tr>"

            print_html = f"""
            <script>
            function printContent() {{
                var win = window.open('', '', 'height=700,width=900');
                win.document.write('<html><head><title>Impression Creos</title>');
                win.document.write('<style>body{{font-family:sans-serif;padding:20px;}} table{{width:100%;border-collapse:collapse;}} td,th{{border:1px solid #ddd;padding:8px;text-align:left;}} .header{{margin-bottom:20px; border-bottom:2px solid #4169E1; padding-bottom:10px;}}</style>');
                win.document.write('</head><body>');
                win.document.write('<div class="header"><h2>Liste des Communes Creos</h2><p>{filter_info}</p></div>');
                win.document.write('<table><thead><tr><th>Commune</th><th>Paiement</th><th>Services</th></tr></thead><tbody>');
                win.document.write(`{table_html}`);
                win.document.write('</tbody></table></body></html>');
                win.document.close();
                win.print();
            }}
            </script>
            <button onclick="printContent()" class="print-btn">🖨️ IMPRESSION</button>
            """
            components.html(print_html, height=45)

        # 4. Affichage des résultats (Tableau et Graphiques)
        c_list, c_viz = st.columns([6, 4])
        with c_list:
            st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=500)
        with c_viz:
            if not df_sorted.empty:
                # Graphique Tartes
                p_c = df_sorted['Paiement'].value_counts().reset_index()
                fig_p = px.pie(p_c, values='count', names='Paiement', hole=0.4, title="Modes de Paiement",
                               color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
                st.plotly_chart(fig_p, use_container_width=True)
