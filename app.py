import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard v3.5")

# On cache le menu Streamlit pour une immersion totale
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 2. LECTURE DES DONNÉES GSHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0).dropna(how="all")
    
    # Conversion du DataFrame en dictionnaire pour JavaScript
    # On adapte les données pour qu'elles correspondent à ta structure JS 'selected'
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
except Exception as e:
    st.error(f"Erreur de connexion GSheets : {e}")
    json_data = "{}"

# --- 3. TON CODE HTML COMPLET ---
# J'ai injecté 'json_data' directement dans l'initialisation de ta Map 'selected'
html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
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
        .panel-title {{ font-size: 0.9rem; font-weight: 800; color: var(--creos); text-transform: uppercase; margin-bottom: 12px; border-bottom: 2px solid #fff; padding-bottom: 5px; }}
        .legend-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 20px; }}
        .leg-item {{ display: flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: #334155; }}
        .dot {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.1); }}
        #map-container {{ height: 380px; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.8; cursor: pointer; transition: 0.2s; }}
        .selected {{ stroke: #000 !important; stroke-width: 2.5px !important; }}
        header {{ display: flex; gap: 15px; align-items: center; margin-bottom: 20px; }}
        #searchInput {{ flex: 1; padding: 12px; border-radius: 10px; border: 2px solid #bae6fd; font-size: 1rem; }}
        .filter-bar {{ display: flex; gap: 10px; margin-bottom: 15px; align-items: center; }}
        .filter-bar select {{ padding: 10px; border-radius: 8px; border: 2px solid #bae6fd; color: #1e3a8a; font-weight: 700; flex: 1; background: #f0f9ff; }}
        #list {{ flex: 1; overflow-y: auto; background: white; border-radius: 12px; border: 1px solid #bae6fd; }}
        .province-group-title {{ background: #f8fafc; padding: 8px 20px; color: var(--creos); font-weight: 800; border-bottom: 1px solid #e2e8f0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }}
        .item {{ display: grid; grid-template-columns: 200px 180px 1fr; padding: 12px 20px; border-bottom: 1px solid #f1f5f9; align-items: center; }}
        .service-badge {{ font-size: 0.7rem; padding: 4px 10px; border-radius: 6px; color: white; display: inline-flex; align-items: center; gap: 5px; margin: 2px; font-weight: 700; }}
        .badge-jour {{ background: var(--c-jour); }} .badge-semaine {{ background: var(--c-sem); }} 
        .badge-mois {{ background: var(--c-mois); }} .badge-gard {{ background: var(--c-gard); }} 
        .badge-act {{ background: var(--c-act); }}
        .btn {{ padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; }}
        .btn-blue {{ background: var(--creos); color: white; }}
        .btn-red {{ background: #ef4444; color: white; }}
    </style>
</head>
<body>

<div id="left-panel">
    <div class="panel-title">Légende & Statistiques</div>
    <div class="legend-grid">
        <div class="leg-item"><div class="dot" style="background:var(--color-bxl)"></div> Bruxelles : <span id="stat-bruxelles">0</span></div>
        <div class="leg-item"><div class="dot" style="background:var(--color-bw)"></div> Brabant Wallon : <span id="stat-brabant">0</span></div>
        <div class="leg-item"><div class="dot" style="background:var(--color-hai)"></div> Hainaut : <span id="stat-hainaut">0</span></div>
        <div class="leg-item"><div class="dot" style="background:var(--color-lie)"></div> Liège : <span id="stat-liege">0</span></div>
        <div class="leg-item"><div class="dot" style="background:var(--color-nam)"></div> Namur : <span id="stat-namur">0</span></div>
        <div class="leg-item"><div class="dot" style="background:var(--color-lux)"></div> Luxembourg : <span id="stat-luxembourg">0</span></div>
    </div>
    <div class="panel-title">Situation géographique</div>
    <div id="map-container"><svg id="svg-map" viewBox="0 0 850 650"></svg></div>
    <div style="background: var(--dark); color: white; padding: 15px; border-radius: 12px;">
        <div style="text-align:center;">
            <div style="font-size: 0.6rem; opacity: 0.7;">TOTAL GSHEETS</div>
            <div id="count" style="font-size: 2.2rem; font-weight: 900; color: #38bdf8; line-height: 1;">0</div>
        </div>
        <div id="service-stats" style="margin-top:10px; border-top:1px solid #334155; padding-top:10px; font-size:0.75rem;"></div>
    </div>
</div>

<div id="right-panel">
    <header>
        <h2 style="margin:0; color: #1e3a8a;">Utilisateurs Creos (Live Data)</h2>
        <input type="text" id="searchInput" placeholder="Chercher une commune..." onkeyup="searchMap()">
    </header>

    <div class="filter-bar">
        <select id="fProv" onchange="updateUI()"><option value="">Toutes les Provinces</option></select>
        <select id="fPay" onchange="updateUI()"><option value="">Paiements</option><option value="Pre">Prépaiement</option><option value="Post">Post-paiement</option></select>
        <select id="fServ" onchange="updateUI()"><option value="">Services</option>
            <option value="Cantine Jour">Cantine Jour</option><option value="Cantine Semaine">Cantine Semaine</option>
            <option value="Cantine Mois">Cantine Mois</option><option value="Garderie">Garderie</option><option value="Activités">Activités</option>
        </select>
        <button onclick="window.location.reload()" class="btn btn-blue"><i class="fa-solid fa-sync"></i> Actualiser GSheets</button>
    </div>

    <div id="list"></div>
</div>

<script>
    // --- CHARGEMENT DES DONNÉES DEPUIS PYTHON ---
    let selected = new Map(Object.entries({json_data}));

    const dataFWB = {{
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
        "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
        "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
        "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
    }};

    const sData = {{
        "Cantine Jour": {{ icon: "fa-utensils", c: "badge-jour" }},
        "Cantine Semaine": {{ icon: "fa-calendar-day", c: "badge-semaine" }},
        "Cantine Mois": {{ icon: "fa-calendar-days", c: "badge-mois" }},
        "Garderie": {{ icon: "fa-clock", c: "badge-gard" }},
        "Activités": {{ icon: "fa-volleyball", c: "badge-act" }}
    }};

    function init() {{
        const svg = document.getElementById('svg-map');
        const fProv = document.getElementById('fProv');
        const anchors = {{
            "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], "Hainaut": [40, 200],
            "Liège": [580, 80], "Namur": [280, 320], "Luxembourg": [530, 420]
        }};

        Object.entries(dataFWB).forEach(([prov, list]) => {{
            fProv.innerHTML += `<option value="${{prov}}">${{prov}}</option>`;
            const safe = prov.toLowerCase().split(' ')[0].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            const colorKey = (safe === 'brabant') ? 'bw' : (safe === 'bruxelles' ? 'bxl' : safe.substring(0,3));
            
            list.forEach((name, i) => {{
                const col = i % 8, row = Math.floor(i / 8);
                const x = anchors[prov][0] + (col * 24), y = anchors[prov][1] + (row * 22);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 5);
                r.setAttribute("class", "commune");
                r.style.fill = `var(--color-${{colorKey}})`;
                r.setAttribute("data-name", name);
                if(selected.has(name)) r.classList.add('selected');
                svg.appendChild(r);
            }});
        }});
        updateUI();
    }}

    function updateUI() {{
        const fP = document.getElementById('fProv').value, fY = document.getElementById('fPay').value, fS = document.getElementById('fServ').value;
        const listDiv = document.getElementById('list');
        let total = 0, pStats = {{}}, sStats = {{}};

        let filtered = [];
        selected.forEach((d, name) => {{
            if((!fP || d.prov === fP) && (!fY || d.pay === fY) && (!fS || d.services.includes(fS))) {{
                total++;
                pStats[d.prov] = (pStats[d.prov] || 0) + 1;
                d.services.forEach(s => sStats[s] = (sStats[s] || 0) + 1);
                filtered.push({{name, ...d}});
            }}
        }});

        listDiv.innerHTML = "";
        const provinces = fP ? [fP] : Object.keys(dataFWB);
        provinces.forEach(prov => {{
            const provItems = filtered.filter(i => i.prov === prov).sort((a,b) => a.name.localeCompare(b.name));
            if(provItems.length > 0) {{
                const title = document.createElement('div');
                title.className = "province-group-title";
                title.innerText = prov;
                listDiv.appendChild(title);
                provItems.forEach(d => {{
                    const row = document.createElement('div');
                    row.className = "item";
                    row.innerHTML = `
                        <strong style="color:#1e3a8a">${{d.name}}</strong>
                        <span style="color:var(--creos); font-weight:800; font-size:0.75rem;">
                            <i class="fa-solid ${{d.pay==='Pre'?'fa-piggy-bank':'fa-file-invoice-dollar'}}"></i> ${{d.pay==='Pre'?'Prépaiement':'Post-paiement'}}
                        </span>
                        <div>${{d.services.map(s => `<span class="service-badge ${{sData[s].c}}"><i class="fa-solid ${{sData[s].icon}}"></i> ${{s}}</span>`).join('')}}</div>
                    `;
                    listDiv.appendChild(row);
                }});
            }}
        }});

        document.getElementById('count').innerText = total;
        document.getElementById('service-stats').innerHTML = Object.keys(sData).map(s => `<div>${{s}} : <strong>${{sStats[s] || 0}}</strong></div>`).join('');
        
        ["bruxelles", "brabant", "hainaut", "liege", "namur", "luxembourg"].forEach(s => {{
            const key = Object.keys(dataFWB).find(k => k.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(s));
            document.getElementById('stat-'+s).innerText = pStats[key] || 0;
        }});
    }}

    function searchMap() {{
        const v = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('.commune').forEach(el => {{
            const m = v.length > 1 && el.getAttribute('data-name').toLowerCase().includes(v);
            el.style.stroke = m ? "#fbbf24" : ""; el.style.strokeWidth = m ? "4px" : "";
        }});
    }}

    init();
</script>
</body>
</html>
"""

# --- 4. AFFICHAGE DANS STREAMLIT ---
# On utilise le composant HTML avec une hauteur suffisante
components.html(html_template, height=950, scrolling=False)

st.info("💡 Les données ci-dessus proviennent en temps réel de votre Google Sheet. Pour modifier les données, éditez directement la feuille Excel en ligne puis cliquez sur 'Actualiser'.")
