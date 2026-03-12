import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard - Retour Stable")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

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
df = conn.read(ttl=0).dropna(how="all")
json_records = df.to_json(orient='records')

# --- 4. HTML / JS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ 
            --creos: #4169E1; --dark: #1e293b; --bg: #f8fafc;
            --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; 
            --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; 
        }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: var(--bg); }}
        #left {{ flex: 0 0 45%; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #ddd; }}
        #right {{ flex: 1; padding: 20px; background: white; display: flex; flex-direction: column; }}
        #map-box {{ flex: 1; background: white; border-radius: 12px; border: 1px solid #eee; margin-bottom: 15px; overflow: hidden; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.5; cursor: pointer; }}
        .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
        #search {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 15px; font-size: 14px; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 13px; align-items: center; }}
        .badge {{ padding: 3px 7px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; margin-left: 3px; display: inline-flex; align-items: center; gap: 4px; }}
        .prov-label {{ background: #f8fafc; padding: 8px; font-weight: bold; font-size: 12px; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #eee; }}
    </style>
</head>
<body>

<div id="left">
    <div id="map-box"><svg id="svg" viewBox="0 0 950 700"></svg></div>
    <div style="background:var(--dark); color:white; padding:20px; border-radius:12px; text-align:center;">
        <div id="total" style="font-size:32px; font-weight:bold; color:#38bdf8;">0</div>
        <div style="font-size:11px; letter-spacing:1px">COMMUNES ENREGISTRÉES</div>
    </div>
</div>

<div id="right">
    <input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()">
    <div id="list"></div>
</div>

<script>
    const dbData = {json_records};
    const fwb = {json.dumps(data_fwb)};
    let db = new Map();
    dbData.forEach(r => db.set(r.Commune, r));

    const icons = {{
        "Cantine Jour": {{ i: "fa-utensils", c: "#fb923c" }},
        "Cantine Semaine": {{ i: "fa-calendar-day", c: "#f59e0b" }},
        "Cantine Mois": {{ i: "fa-calendar-days", c: "#d97706" }},
        "Garderie": {{ i: "fa-clock", c: "#38bdf8" }},
        "Activités": {{ i: "fa-volleyball", c: "#4ade80" }}
    }};

    function init() {{
        const svg = document.getElementById('svg');
        const anchors = {{ 
            "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], 
            "Hainaut": [40, 200], "Liège": [580, 80], 
            "Namur": [280, 320], "Luxembourg": [530, 420] 
        }};

        Object.entries(fwb).forEach(([pName, list]) => {{
            const cKey = pName.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
            list.forEach((name, i) => {{
                const x = anchors[pName][0] + (i % 8 * 24), y = anchors[pName][1] + (Math.floor(i / 8) * 22);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 4);
                r.setAttribute("class", "commune" + (db.has(name) ? " active" : ""));
                r.style.fill = `var(--c-${{cKey}})`;
                
                const t = document.createElementNS("http://www.w3.org/2000/svg", "title");
                t.textContent = name;
                r.appendChild(t); svg.appendChild(r);
            }});
        }});
        renderList();
    }}

    function renderList() {{
        const listDiv = document.getElementById('list');
        listDiv.innerHTML = "";
        let count = 0;
        const provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];

        provinces.forEach(p => {{
            const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
            if(filtered.length > 0) {{
                const h = document.createElement('div'); h.className = 'prov-label'; h.innerText = p;
                listDiv.appendChild(h);
                filtered.forEach(x => {{
                    count++;
                    const row = document.createElement('div'); row.className = 'item-row';
                    const badges = (x.Services || "").split('|').filter(s => s).map(s => `
                        <span class="badge" style="background:${{icons[s]?.c || '#ccc'}}">
                            <i class="fa-solid ${{icons[s]?.i || 'fa-tag'}}"></i> ${{s}}
                        </span>
                    `).join('');
                    row.innerHTML = `<span><strong>${{x.Commune}}</strong> <small>(${{x.Paiement}})</small></span><div>${{badges}}</div>`;
                    listDiv.appendChild(row);
                }});
            }}
        }});
        document.getElementById('total').innerText = count;
    }}

    function doSearch() {{
        const val = document.getElementById('search').value.toLowerCase();
        document.querySelectorAll('.item-row').forEach(r => {{
            r.style.display = r.innerText.toLowerCase().includes(val) ? 'flex' : 'none';
        }});
    }}

    init();
</script>
</body>
</html>
"""

components.html(html_code, height=850)
