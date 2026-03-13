import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

st.markdown("""
    <style>
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
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white;
            color: #4169E1;
            padding: 8px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: 0.3s;
        }
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 2. DONNÉES DE RÉFÉRENCE ---
data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- TAB 1 : DASHBOARD ---
tab1, tab2 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes"])

with tab1:
    t_dash = len(df_gsheets)
    p_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    po_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    s_dash = {
        "Cantine J": (df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum(), "#ec4899"),
        "Cantine S": (df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum(), "#db2777"),
        "Cantine M": (df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum(), "#be185d"),
        "Garderie": (df_gsheets['Services'].str.contains("Garderie", na=False).sum(), "#38bdf8"),
        "Activités": (df_gsheets['Services'].str.contains("Activités", na=False).sum(), "#4ade80")
    }
    json_recs = df_gsheets.to_json(orient='records')
    
    html_map = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
            :root {{ --creos: #4169E1; --dark: #1e293b; --bg: #ffffff; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
            body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: var(--bg); }}
            #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
            #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
            
            #map-box {{ flex: 0 0 280px; background: white; border-radius: 8px; border: 1px solid #eee; margin-bottom: 8px; }}
            svg {{ width: 100%; height: 100%; }}
            .commune {{ stroke: #fff; stroke-width: 0.5; }}
            .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
            #search {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 8px; box-sizing: border-box; }}
            #list {{ flex: 1; overflow-y: auto; }}
            
            .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; }}
            .panel-header {{ text-align: center; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
            .panel-title {{ font-size: 12px; text-transform: uppercase; opacity: 0.7; letter-spacing: 0.5px; }}
            .main-count {{ font-size: 44px; font-weight: bold; color: #ffffff; line-height: 1; margin-top: 4px; }}
            
            .cols-container {{ display: flex; gap: 15px; }}
            .col-half {{ flex: 1; }}
            .stat-header {{ font-size: 10px; text-transform: uppercase; opacity: 0.5; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 2px; text-align: center; }}
            
            .v-item {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
            .v-label {{ font-size: 13px; font-weight: 500; }}
            .v-val {{ font-size: 14px; font-weight: bold; padding: 1px 8px; border-radius: 4px; min-width: 22px; text-align: center; }}
            
            .item-row {{ display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #f1f5f9; font-size: 12px; align-items: center; }}
            .badge {{ padding: 2px 5px; border-radius: 4px; color: white; font-size: 9px; font-weight: bold; display: inline-flex; align-items: center; gap: 3px; }}
        </style></head><body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div class="panel-header">
                <div class="panel-title">Total des communes actives</div>
                <div class="main-count">{t_dash}</div>
            </div>
            <div class="cols-container">
                <div class="col-half">
                    <div class="stat-header">Paiement</div>
                    <div class="v-item"><span class="v-label">Prépaiement</span><span class="v-val" style="background:#ec4899">{p_dash}</span></div>
                    <div class="v-item"><span class="v-label">Post-paiement</span><span class="v-val" style="background:#38bdf8">{po_dash}</span></div>
                </div>
                <div class="col-half">
                    <div class="stat-header">Services</div>
                    { "".join([f'<div class="v-item"><span class="v-label">{k}</span><span class="v-val" style="background:{v[1]}">{v[0]}</span></div>' for k,v in s_dash.items()]) }
                </div>
            </div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()"><div id="list"></div></div>

    <script>
        const dbData = {json_recs}; const mapRef = {json.dumps(data_fwb)}; let db = new Map(); dbData.forEach(r => db.set(r.Commune, r));
        const icons = {{ "Cantine Jour": {{ i: "fa-utensils", c: "#ec4899" }}, "Cantine Semaine": {{ i: "fa-calendar-day", c: "#db2777" }}, "Cantine Mois": {{ i: "fa-calendar-days", c: "#be185d" }}, "Garderie": {{ i: "fa-clock", c: "#38bdf8" }}, "Activités": {{ i: "fa-volleyball", c: "#4ade80" }} }};
        function init() {{
            const svg = document.getElementById('svg'); const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
            Object.entries(mapRef).forEach(([pName, list]) => {{
                const cleanP = pName.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
                list.forEach((name, i) => {{
                    const x = anchors[pName][0] + (i % 8 * 23), y = anchors[pName][1] + (Math.floor(i / 8) * 21);
                    const r = document.createElementNS("http://www.w3.org/2000/svg", "rect"); r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 3);
                    r.setAttribute("class", "commune" + (db.has(name) ? " active" : "")); r.style.fill = `var(--c-${{cleanP}})`;
                    const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name; r.appendChild(t); svg.appendChild(r);
                }});
            }}); render();
        }}
        function render() {{
            const listDiv = document.getElementById('list'); listDiv.innerHTML = "";
            ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"].forEach(p => {{
                const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div'); h.style.background='#f8fafc'; h.style.padding='4px'; h.style.fontSize='10px'; h.innerText = p; listDiv.appendChild(h);
                    filtered.forEach(x => {{ const row = document.createElement('div'); row.className = 'item-row';
                        const badges = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{icons[s]?.c || '#ccc'}}"><i class="fa-solid ${{icons[s]?.i || 'fa-tag'}}"></i></span>`).join(' ');
                        row.innerHTML = `<span><b>${{x.Commune}}</b></span><div>${{badges}}</div>`; listDiv.appendChild(row);
                    }});
                }}
            }});
        }}
        function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => {{ r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'; }}); }}
    </script></body></html>"""
    components.html(html_map, height=750)

# (Le reste du code pour l'onglet Gestion reste inchangé)
