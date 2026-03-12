import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard v3.5")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} .stDeployButton {display:none;}</style>", unsafe_allow_html=True)

# --- 2. LECTURE DES DONNÉES GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

data_dict = {}
for _, row in df.iterrows():
    commune = str(row['Commune']).strip()
    services = str(row['Services']).split('|') if pd.notna(row['Services']) else []
    data_dict[commune] = {
        "prov": str(row['Province']),
        "pay": "Pre" if "Pre" in str(row['Paiement']) else "Post",
        "services": services
    }
json_data = json.dumps(data_dict)

# --- 3. LE CODE HTML/JS ---
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ 
            --creos: #4169E1; --dark: #1e293b; --bg: #e0f2fe;
            --color-bxl: #ffeaa7; --color-bw: #81ecec; --color-hai: #a29bfe; 
            --color-lie: #74b9ff; --color-nam: #fab1a0; --color-lux: #FF43D0; 
            --c-jour: #fb923c; --c-sem: #f59e0b; --c-mois: #d97706;
            --c-gard: #38bdf8; --c-act: #4ade80;
        }}
        body {{ margin: 0; font-family: 'Segoe UI', sans-serif; display: flex; height: 100vh; background: var(--bg); overflow: hidden; }}
        
        #left-panel {{ flex: 0 0 35%; display: flex; flex-direction: column; background: var(--bg); border-right: 2px solid #bae6fd; padding: 20px; box-sizing: border-box; overflow-y: auto; }}
        #right-panel {{ flex: 1; display: flex; flex-direction: column; padding: 25px; box-sizing: border-box; overflow: hidden; }}

        /* Styles de la Carte */
        #map-container {{ height: 380px; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.8; cursor: pointer; transition: 0.2s; }}
        .selected {{ stroke: #000 !important; stroke-width: 2.5px !important; }}
        .highlight-search {{ stroke: #fbbf24 !important; stroke-width: 4px !important; }}

        /* Styles de la Liste et Badges */
        #list {{ flex: 1; overflow-y: auto; background: white; border-radius: 12px; border: 1px solid #bae6fd; }}
        .item {{ display: grid; grid-template-columns: 180px 150px 1fr; padding: 10px 20px; border-bottom: 1px solid #f1f5f9; align-items: center; }}
        .service-badge {{ font-size: 0.65rem; padding: 3px 8px; border-radius: 6px; color: white; margin: 2px; font-weight: 700; display: inline-block; }}
        .badge-jour {{ background: var(--c-jour); }} .badge-semaine {{ background: var(--c-sem); }} 
        .badge-mois {{ background: var(--c-mois); }} .badge-gard {{ background: var(--c-gard); }} 
        .badge-act {{ background: var(--c-act); }}

        /* Popup de Configuration */
        #config-menu {{ 
            position: fixed; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
            padding: 20px; display: none; z-index: 1000; width: 280px; border: 1px solid #ddd; 
        }}
        
        input[type="text"] {{ width: 100%; padding: 12px; border-radius: 10px; border: 2px solid #bae6fd; box-sizing: border-box; }}
        .btn {{ padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; border:none; color:white; }}
        .btn-blue {{ background: var(--creos); }}
    </style>
</head>
<body>

<div id="config-menu">
    <h4 id="menu-title" style="margin:0 0 10px 0; color:var(--creos);">Configuration</h4>
    <div id="config-form"></div>
</div>

<div id="left-panel">
    <div style="font-size: 0.9rem; font-weight: 800; color: var(--creos); text-transform: uppercase; margin-bottom: 15px;">Situation géographique</div>
    <div id="map-container"><svg id="svg-map" viewBox="0 0 850 650"></svg></div>
    <div style="background: var(--dark); color: white; padding: 15px; border-radius: 12px; text-align:center;">
        <div style="font-size: 0.6rem; opacity: 0.7;">COMMUNES ACTIVES</div>
        <div id="count" style="font-size: 2.2rem; font-weight: 900; color: #38bdf8;">0</div>
    </div>
</div>

<div id="right-panel">
    <header style="display:flex; gap:15px; margin-bottom:20px;">
        <input type="text" id="searchInput" placeholder="Chercher une commune (encadre sur la carte)..." onkeyup="searchAndHighlight()">
    </header>
    <div id="list"></div>
</div>

<script>
    let selected = new Map(Object.entries({json_data}));
    let currentCommune = null;

    const dataFWB = {json.dumps(dataFWB_list)}; // Données injectées depuis Python
    const sData = {{
        "Cantine Jour": "badge-jour", "Cantine Semaine": "badge-semaine",
        "Cantine Mois": "badge-mois", "Garderie": "badge-gard", "Activités": "badge-act"
    }};

    function init() {{
        const svg = document.getElementById('svg-map');
        const anchors = {{ "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], "Hainaut": [40, 200], "Liège": [580, 80], "Namur": [280, 320], "Luxembourg": [530, 420] }};

        Object.entries(dataFWB).forEach(([prov, list]) => {{
            const safe = prov.toLowerCase().split(' ')[0].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const colorKey = (safe === 'brabant') ? 'bw' : (safe === 'bruxelles' ? 'bxl' : safe.substring(0,3));
            
            list.forEach((name, i) => {{
                const col = i % 8, row = Math.floor(i / 8);
                const x = anchors[prov][0] + (col * 24), y = anchors[prov][1] + (row * 22);
                
                const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                const t = document.createElementNS("http://www.w3.org/2000/svg", "title");
                
                t.textContent = name; // Nom au survol
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 5);
                r.setAttribute("class", "commune");
                r.setAttribute("data-name", name.toLowerCase());
                r.style.fill = `var(--color-${{colorKey}})`;
                if(selected.has(name)) r.classList.add('selected');
                
                r.onclick = (e) => openConfig(name, e);
                
                g.appendChild(r); g.appendChild(t);
                svg.appendChild(g);
            }});
        }});
        updateUI();
    }}

    function openConfig(name, e) {{
        currentCommune = name;
        const d = selected.get(name) || {{ pay: 'Pre', services: [] }};
        const menu = document.getElementById('config-menu');
        document.getElementById('menu-title').innerText = name;
        document.getElementById('config-form').innerHTML = `
            <div style="font-size:0.85rem; margin-bottom:12px;"><strong>Paiement</strong><br>
                <label><input type="radio" name="pay" value="Pre" ${{d.pay==='Pre'?'checked':''}}> Prépaiement</label>
                <label style="margin-left:10px;"><input type="radio" name="pay" value="Post" ${{d.pay==='Post'?'checked':''}}> Post-paiement</label>
            </div>
            <div style="font-size:0.85rem; margin-bottom:15px;"><strong>Services</strong><br>
                ${{Object.keys(sData).map(s => `<label><input type="checkbox" name="serv" value="${{s}}" ${{d.services.includes(s)?'checked':''}}> ${{s}}</label><br>`).join('')}}
            </div>
            <button onclick="saveAndSend()" class="btn btn-blue" style="width:100%">ENREGISTRER</button>
        `;
        menu.style.display = 'block';
        menu.style.left = Math.min(e.pageX, window.innerWidth - 300) + 'px';
        menu.style.top = Math.min(e.pageY, window.innerHeight - 350) + 'px';
    }}

    function saveAndSend() {{
        // Logique de sauvegarde (peut être reliée à Streamlit via un bouton caché ou API)
        alert("Sauvegarde de " + currentCommune + " enregistrée localement.");
        document.getElementById('config-menu').style.display = 'none';
    }}

    function searchAndHighlight() {{
        const v = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('.commune').forEach(el => {{
            const name = el.getAttribute('data-name');
            if(v.length > 1 && name.includes(v)) {{
                el.classList.add('highlight-search');
            }} else {{
                el.classList.remove('highlight-search');
            }}
        }});
    }}

    function updateUI() {{
        const listDiv = document.getElementById('list');
        listDiv.innerHTML = "";
        let total = 0;
        selected.forEach((d, name) => {{
            total++;
            const row = document.createElement('div');
            row.className = "item";
            row.innerHTML = `
                <strong style="color:#1e3a8a">${{name}}</strong>
                <span style="font-size:0.7rem; color:var(--creos); font-weight:bold;">${{d.pay==='Pre'?'PRÉPAIEMENT':'POST-PAIEMENT'}}</span>
                <div>${{d.services.map(s => `<span class="service-badge ${{sData[s]}}">${{s}}</span>`).join('')}}</div>
            `;
            listDiv.appendChild(row);
        }});
        document.getElementById('count').innerText = total;
    }}

    init();
</script>
</body>
</html>
"""

# Injection de la liste des communes (dataFWB_list doit être défini comme dans ton code précédent)
dataFWB_list = {
    "Bruxelles": ["Anderlecht", "Bruxelles", "Ixelles", "Uccle"], # etc...
    "Brabant Wallon": ["Wavre", "Waterloo", "Nivelles"],
    # Ajoute les autres ici...
}

components.html(html_template, height=850, scrolling=False)
