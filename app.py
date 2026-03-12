import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard v3.5")
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
df_gsheets = conn.read(ttl=0).dropna(how="all")

# Tri par Province puis par Commune avant traitement
prov_order = {p: i for i, p in enumerate(data_fwb.keys())}
df_gsheets['prov_rank'] = df_gsheets['Province'].map(prov_order).fillna(99)
df_gsheets = df_gsheets.sort_values(by=['prov_rank', 'Commune'])

data_dict = {}
for _, row in df_gsheets.iterrows():
    c = str(row['Commune']).strip()
    if c and c != "nan":
        s = str(row['Services']).split('|') if pd.notna(row['Services']) else []
        data_dict[c] = {
            "prov": str(row['Province']).strip(),
            "pay": str(row['Paiement']).strip(),
            "services": [srv.strip() for srv in s if srv]
        }

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Sync GSheets")
    st.write(f"Communes en base : **{len(data_dict)}**")
    with st.form("save_form"):
        c_name = st.text_input("Commune", key="input_commune")
        c_prov = st.text_input("Province", key="input_province")
        c_pay = st.selectbox("Paiement", ["Pre", "Post"], key="input_pay")
        c_serv = st.text_input("Services (séparés par |)", key="input_services")
        submit = st.form_submit_button("💾 SAUVEGARDER")

if submit and c_name:
    new_entry = pd.DataFrame([{"Commune": c_name, "Province": c_prov, "Paiement": c_pay, "Services": c_serv}])
    updated_df = pd.concat([df_gsheets[df_gsheets['Commune'] != c_name], new_entry], ignore_index=True)
    conn.update(data=updated_df.drop(columns=['prov_rank'], errors='ignore'))
    st.success("Synchronisé !")
    st.rerun()

# --- 5. HTML/JS ---
html_template = f"""
<!DOCTYPE html>
<html>
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
        #map-container {{ height: 420px; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.8; cursor: pointer; transition: 0.2s; }}
        .selected {{ stroke: #000 !important; stroke-width: 2.5px !important; }}
        .highlight-search {{ stroke: #fbbf24 !important; stroke-width: 4px !important; }}
        #list {{ flex: 1; overflow-y: auto; background: white; border-radius: 12px; border: 1px solid #bae6fd; }}
        .prov-header {{ background: #f8fafc; padding: 8px 20px; font-weight: 800; font-size: 0.75rem; color: #64748b; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; }}
        .item {{ display: grid; grid-template-columns: 160px 100px 1fr; padding: 10px 20px; border-bottom: 1px solid #f1f5f9; align-items: center; }}
        .service-badge {{ font-size: 0.6rem; padding: 3px 6px; border-radius: 4px; color: white; margin: 2px; font-weight: 700; display: inline-flex; align-items: center; gap: 3px; }}
        .badge-jour {{ background: var(--c-jour); }} .badge-semaine {{ background: var(--c-sem); }} 
        .badge-mois {{ background: var(--c-mois); }} .badge-gard {{ background: var(--c-gard); }} 
        .badge-act {{ background: var(--c-act); }}
        #config-menu {{ position: fixed; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 20px; display: none; z-index: 1000; width: 280px; border: 1px solid #bae6fd; }}
        .btn-save {{ background: var(--creos); color: white; border: none; padding: 10px; border-radius: 8px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; }}
    </style>
</head>
<body>

<div id="config-menu">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h4 id="menu-title" style="margin:0; color:var(--creos);">Configuration</h4>
        <i class="fa-solid fa-times" style="cursor:pointer; color:#94a3b8;" onclick="this.parentElement.parentElement.style.display='none'"></i>
    </div>
    <div id="config-form"></div>
    <button class="btn-save" onclick="saveData()">CONFIRMER MODIF</button>
</div>

<div id="left-panel">
    <div style="font-size: 0.8rem; font-weight: 800; color: var(--creos); text-transform: uppercase; margin-bottom: 10px;">Carte Interactive</div>
    <div id="map-container"><svg id="svg-map" viewBox="0 0 850 650"></svg></div>
    <div style="background: var(--dark); color: white; padding: 15px; border-radius: 12px; text-align:center;">
        <div id="count" style="font-size: 2.2rem; font-weight: 900; color: #38bdf8;">0</div>
    </div>
</div>

<div id="right-panel">
    <header style="margin-bottom:20px;"><input type="text" id="searchInput" style="width:100%; padding:12px; border-radius:10px; border:2px solid #bae6fd;" placeholder="🔍 Chercher une commune..." onkeyup="searchAndHighlight()"></header>
    <div id="list"></div>
</div>

<script>
    let selected = new Map(Object.entries({json.dumps(data_dict)}));
    let dataFWB = {json.dumps(data_fwb)};
    const sData = {{
        "Cantine Jour": {{ icon: "fa-utensils", c: "badge-jour" }},
        "Cantine Semaine": {{ icon: "fa-calendar-day", c: "badge-semaine" }},
        "Cantine Mois": {{ icon: "fa-calendar-days", c: "badge-mois" }},
        "Garderie": {{ icon: "fa-clock", c: "badge-gard" }},
        "Activités": {{ icon: "fa-volleyball", c: "badge-act" }}
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
                t.textContent = name;
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 5);
                r.setAttribute("class", "commune"); r.setAttribute("data-name", name);
                r.style.fill = `var(--color-${{colorKey}})`;
                if(selected.has(name)) r.classList.add('selected');
                r.onclick = (e) => openConfig(name, e);
                g.appendChild(r); g.appendChild(t); svg.appendChild(g);
            }});
        }});
        updateUI();
    }}

    function openConfig(name, e) {{
        let d = selected.get(name) || {{ pay: 'Pre', services: [] }};
        const menu = document.getElementById('config-menu');
        document.getElementById('menu-title').innerText = name;
        document.getElementById('config-form').innerHTML = `
            <div style="font-size:0.85rem; margin-bottom:10px;"><strong>Paiement</strong><br>
                <label><input type="radio" name="pay" value="Pre" ${{d.pay==='Pre'?'checked':''}}> Pre</label>
                <label style="margin-left:10px;"><input type="radio" name="pay" value="Post" ${{d.pay==='Post'?'checked':''}}> Post</label>
            </div>
            <div style="font-size:0.85rem;"><strong>Services</strong><br>
                ${{Object.keys(sData).map(s => `<label style="display:block;"><input type="checkbox" name="serv" value="${{s}}" ${{d.services.includes(s)?'checked':''}}> ${{s}}</label>`).join('')}}
            </div>
        `;
        menu.style.display = 'block'; menu.style.left = Math.min(e.pageX, window.innerWidth-300)+'px'; menu.style.top = Math.min(e.pageY, window.innerHeight-350)+'px';
    }}

    function saveData() {{
        const name = document.getElementById('menu-title').innerText;
        const pay = document.querySelector('input[name="pay"]:checked').value;
        const servs = Array.from(document.querySelectorAll('input[name="serv"]:checked')).map(c => c.value);
        let prov = "";
        for(let [p, list] of Object.entries(dataFWB)) {{ if(list.includes(name)) {{ prov = p; break; }} }}

        const parent = window.parent.document;
        const inputs = parent.querySelectorAll('input[data-testid="stTextInputRootElement"] input');
        if(inputs.length >= 3) {{
            inputs[0].value = name; inputs[0].dispatchEvent(new Event('input', {{bubbles:true}}));
            inputs[1].value = prov; inputs[1].dispatchEvent(new Event('input', {{bubbles:true}}));
            inputs[2].value = servs.join('|'); inputs[2].dispatchEvent(new Event('input', {{bubbles:true}}));
        }}
        selected.set(name, {{ prov, pay, services: servs }});
        document.querySelector(`rect[data-name="${{name}}"]`).classList.add('selected');
        document.getElementById('config-menu').style.display = 'none';
        updateUI();
    }}

    function searchAndHighlight() {{
        const v = document.getElementById('searchInput').value.toLowerCase();
        document.querySelectorAll('.commune').forEach(el => {{
            const name = el.getAttribute('data-name').toLowerCase();
            if(v.length > 1 && name.includes(v)) el.classList.add('highlight-search');
            else el.classList.remove('highlight-search');
        }});
    }}

    function updateUI() {{
        const listDiv = document.getElementById('list');
        listDiv.innerHTML = "";
        let count = 0;
        const provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
        
        provinces.forEach(p => {{
            const filtered = Array.from(selected.entries())
                .filter(([_, d]) => d.prov === p)
                .sort((a,b) => a[0].localeCompare(b[0]));
            
            if(filtered.length > 0) {{
                const header = document.createElement('div');
                header.className = "prov-header";
                header.innerText = p;
                listDiv.appendChild(header);
                
                filtered.forEach(([name, d]) => {{
                    count++;
                    const row = document.createElement('div');
                    row.className = "item";
                    row.innerHTML = `
                        <strong style="color:#1e3a8a; font-size:0.85rem;">${{name}}</strong>
                        <span style="font-size:0.65rem; font-weight:bold; color:var(--creos);">${{d.pay.toUpperCase()}}</span>
                        <div>${{d.services.map(s => `<span class="service-badge ${{sData[s].c}}"><i class="fa-solid ${{sData[s].icon}}"></i> ${{s}}</span>`).join('')}}</div>
                    `;
                    listDiv.appendChild(row);
                }});
            }}
        }});
        document.getElementById('count').innerText = count + " UNITÉS";
    }}
    init();
</script>
</body>
</html>
"""

components.html(html_template, height=850)
