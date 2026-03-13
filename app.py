import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ET DESIGN ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Restauration de votre Header Original
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        .main-header {
            background-color: #4169E1;
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            color: white;
        }
        .tt-button {
            background-color: white; color: #4169E1; padding: 8px 18px;
            border-radius: 5px; text-decoration: none; font-weight: bold;
        }
    </style>
    <div class="main-header">
        <div style="font-size: 24px; font-weight: bold;">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES DE RÉFÉRENCE ---
data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord & Carte", "✏️ Gestion & Liste"])

# --- TAB 1 : DASHBOARD & CARTE ---
with tab1:
    # Statistiques
    t_count = len(df_gsheets)
    
    # Carte interactive originale
    json_recs = df_gsheets.to_json(orient='records')
    html_map = f"""
    <!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; background: #f8fafc; overflow: hidden; }}
        #left {{ flex: 4; padding: 15px; display: flex; flex-direction: column; }}
        #right {{ flex: 6; padding: 15px; overflow-y: auto; background: white; border-left: 1px solid #e2e8f0; }}
        #map-box {{ flex: 0 0 380px; background: #262730; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .stats-panel {{ background: var(--dark); color: white; padding: 20px; border-radius: 15px; text-align: center; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #f1f5f9; align-items: center; }}
    </style></head><body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650" style="width:100%; height:100%;"></svg></div>
        <div class="stats-panel">
            <div style="font-size:45px; font-weight:bold;">{t_count}</div>
            <div style="font-size:14px; opacity:0.8; letter-spacing: 1px;">COMMUNES ACTIVES</div>
        </div>
    </div>
    <div id="right">
        <input type="text" id="search" placeholder="🔍 Rechercher une commune..." style="width:96%; padding:12px; border:1px solid #cbd5e1; border-radius:8px; margin-bottom:15px;" onkeyup="doSearch()">
        <div id="list"></div>
    </div>
    <script>
        const db = {json_recs}; const mapRef = {json.dumps(data_fwb)};
        function init() {{
            const svg = document.getElementById('svg');
            const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
            Object.entries(mapRef).forEach(([p, list]) => {{
                list.forEach((name, i) => {{
                    const x = anchors[p][0] + (i % 8 * 23), y = anchors[p][1] + (Math.floor(i / 8) * 22);
                    const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 4);
                    const active = db.find(d => d.Commune === name);
                    r.style.fill = active ? "#ffffff" : "rgba(255,255,255,0.1)";
                    svg.appendChild(r);
                }});
            }});
            const listDiv = document.getElementById('list');
            db.sort((a,b) => a.Commune.localeCompare(b.Commune)).forEach(x => {{
                const row = document.createElement('div'); row.className = 'item-row';
                row.innerHTML = `<div><b style="color:#4169E1;">${{x.Commune}}</b><br><small style="color:#64748b;">${{x.Province}}</small></div><span style="font-size:11px; background:#f1f5f9; padding:4px 8px; border-radius:4px;">${{x.Paiement}}</span>`;
                listDiv.appendChild(row);
            }});
        }}
        function doSearch() {{
            const v = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.item-row').forEach(r => r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none');
        }}
    </script></body></html>
    """
    components.html(html_map, height=750)

# --- TAB 2 : GESTION & LISTE ---
with tab2:
    st.header("✏️ Gestion des données")
    
    col_form, col_graph = st.columns([6, 4])
    
    with col_form:
        p_sel = st.selectbox("Sélectionner la Province", list(data_fwb.keys()))
        with st.form("form_saisie"):
            c1, c2 = st.columns(2)
            with c1: com_sel = st.selectbox("Commune", data_fwb[p_sel])
            with c2: 
                pay_v = st.radio("Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            
            if st.form_submit_button("💾 ENREGISTRER / METTRE À JOUR", use_container_width=True):
                new_row = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_row], ignore_index=True)
                conn.update(data=df_u)
                st.success(f"Données pour {com_sel} enregistrées !")
                st.rerun()

    with col_graph:
        if not df_gsheets.empty:
            fig = px.pie(df_gsheets, names='Paiement', hole=0.4, title="Répartition des modes de paiement",
                         color_discrete_sequence=['#4169E1', '#F0F2F6'])
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- FILTRES ET TABLEAU ---
    st.subheader("🔍 Liste filtrée et Export")
    
    c_f1, c_f2, c_print = st.columns([3, 3, 2])
    with c_f1: fl_p = st.multiselect("Filtrer par Province", sorted(df_gsheets['Province'].unique()))
    with c_f2: fl_m = st.multiselect("Filtrer par Paiement", ["Prépaiement", "Post-paiement"])
    with c_print:
        st.write("##")
        if st.button("🖨️ IMPRIMER LA PAGE", use_container_width=True):
            components.html("<script>window.print();</script>", height=0)

    # Filtrage et Tri
    df_display = df_gsheets.copy()
    if fl_p: df_display = df_display[df_display['Province'].isin(fl_p)]
    if fl_m: df_display = df_display[df_display['Paiement'].isin(fl_m)]
    
    # TRI PAR PROVINCE PUIS COMMUNE
    df_display = df_display.sort_values(by=['Province', 'Commune'])

    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Export Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_display.to_excel(writer, index=False, sheet_name='Utilisateurs')
    st.download_button("📥 Télécharger la sélection en Excel", output.getvalue(), "creos_export.xlsx", use_container_width=True)
