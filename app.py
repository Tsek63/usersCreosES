import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")
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

# --- 3. GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")
df['Commune'] = df['Commune'].astype(str).str.strip()
df['Province'] = df['Province'].astype(str).str.strip()
json_data = df.to_json(orient='records')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("💾 Enregistrement")
    with st.form("sync_form"):
        # Labels simplifiés pour le pont JS
        c_in = st.text_input("Commune")
        p_in = st.text_input("Province")
        y_in = st.selectbox("Paiement", ["Pre", "Post"])
        s_in = st.text_input("Services")
        if st.form_submit_button("VALIDER GSHEETS"):
            row = pd.DataFrame([{"Commune": c_in, "Province": p_in, "Paiement": y_in, "Services": s_in}])
            up = pd.concat([df[df['Commune'] != c_in], row], ignore_index=True)
            conn.update(data=up)
            st.rerun()

# --- 5. INTERFACE HTML ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ 
            --creos: #4169E1; --dark: #1e293b; --bg: #f8fafc;
            /* Couleurs sans accents dans les noms de variables */
            --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; 
            --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; 
        }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: var(--bg); }}
        #left {{ flex: 0 0 42%; padding: 20px; border-right: 1px solid #ddd; display: flex; flex-direction: column; }}
        #right {{ flex: 1; padding: 20px; background: white; display: flex; flex-direction: column; }}
        #map-container {{ flex: 1; background: white; border-radius: 12px; border: 1px solid #eee; margin-bottom: 10px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.5; cursor: pointer; }}
        .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
        #search {{ width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .prov-h {{ background: #f1f5f9; padding: 8px; font-weight: bold; font-size: 12px; color: #475569; margin-top: 5px; }}
        .item-r {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f8fafc; font-size: 13px; align-items: center; }}
        .badge {{ padding: 3px 6px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; margin-left: 2px; display: inline-flex; align-items: center; gap: 3px; }}
        #pop {{ position: fixed; background: white; border: 1px solid #ccc; padding: 15px; border-radius: 8px; display: none; z-index: 1000; width: 220px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>

<div id="pop">
    <b id="pop-t"></b><br>
    <div id="pop-f" style="font-size:12px; margin-top:10px"></div>
    <button onclick="saveToSidebar()" style="width:100%; margin-top:10px; background:var(--creos); color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">CONFIGURER</button>
</div>

<div id="left">
    <div id="map-container"><svg id="svg" viewBox="0 0 900 700"></svg></div>
    <div style="background:var(--dark); color:white; padding:15px; border-radius:10px; text-align:center;">
        <span id="stat" style="font-size:28px; font-weight:bold; color:#38bdf8;">0</span> UNITÉS
    </div>
</div>

<div id="right">
    <input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="filter()">
    <div id="list"></div>
</div>

<script>
    const rawData = {json_data};
    const fwb = {json.dumps(data_fwb)};
    let db = new Map();
    rawData.forEach(d => db.set(d.Commune, d));

    const sMeta = {{
        "Cantine Jour": {{ i: "fa-utensils", c: "#fb923c" }},
        "Cantine Semaine": {{ i: "fa-calendar-day", c: "#f59e0b" }},
        "Cantine Mois": {{ i: "fa-calendar-days", c: "#d97706" }},
        "Garderie": {{ i: "fa-clock", c: "#38bdf8" }},
        "Activités": {{ i: "fa-volleyball", c: "#4ade80" }}
    }};

    function init() {{
        const svg = document.getElementById('svg');
        const anchors = {{ "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], "Hainaut": [40, 200], "Liège": [580, 80], "Namur": [280, 320], "Luxembourg": [530, 420] }};

        Object.entries(fwb).forEach(([pName, list]) => {{
            // Nettoyage du nom de la province pour la couleur (liege au lieu de liège)
            const cleanP = pName.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
            list.forEach((name, i) => {{
                const x = anchors[pName][0] + (i % 8 * 24), y = anchors[pName][1] + (Math.floor(i / 8) * 22);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 4);
                r.setAttribute("class", "commune" + (db.has(name) ? " active" : ""));
                r.style.fill = `var(--c-${{cleanP}})`;
                r.onclick = (e) => showPop(name, pName, e);
                const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name;
                r.appendChild(t); svg.appendChild(r);
            }});
        }});
        updateUI();
    }}

    function showPop(name, prov, e) {{
        const d = db.get(name) || {{ Paiement: 'Pre', Services: '' }};
        document.getElementById('pop-t').innerText = name;
        document.getElementById('pop-f').innerHTML = `
            <input type="hidden" id="i-prov" value="${{prov}}">
            Pay: <select id="i-pay"><option value="Pre" ${{d.Paiement==='Pre'?'selected':''}}>Pre</option><option value="Post" ${{d.Paiement==='Post'?'selected':''}}>Post</option></select><br><br>
            ${{Object.keys(sMeta).map(s => `<label style="display:block"><input type="checkbox" class="i-srv" value="${{s}}" ${{d.Services.includes(s)?'checked':''}}> ${{s}}</label>`).join('')}}
        `;
        const p = document.getElementById('pop'); p.style.display='block'; p.style.left=e.pageX+'px'; p.style.top=e.pageY+'px';
    }}

    function saveToSidebar() {{
        const name = document.getElementById('pop-t').innerText;
        const prov = document.getElementById('i-prov').value;
        const pay = document.getElementById('i-pay').value;
        const srvs = Array.from(document.querySelectorAll('.i-srv:checked')).map(x=>x.value).join('|');

        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(i => {{
            const label = i.closest('.stTextInput')?.querySelector('label')?.innerText || "";
            if(label.includes("Commune")) i.value = name;
            if(label.includes("Province")) i.value = prov;
            if(label.includes("Services")) i.value = srvs;
            i.dispatchEvent(new Event('input', {{bubbles:true}}));
        }});
        document.getElementById('pop').style.display='none';
    }}

    function updateUI() {{
        const list = document.getElementById('list');
        list.innerHTML = ""; let n = 0;
        const order = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
        order.forEach(p => {{
            const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
            if(filtered.length > 0) {{
                const h = document.createElement('div'); h.className='prov-h'; h.innerText=p; list.appendChild(h);
                filtered.forEach(x => {{
                    n++;
                    const row = document.createElement('div'); row.className='item-r';
                    const b = x.Services.split('|').filter(s=>s).map(s => `<span class="badge" style="background:${{sMeta[s].c}}"><i class="fa-solid ${{sMeta[s].i}}"></i> ${{s}}</span>`).join('');
                    row.innerHTML = `<span><b>${{x.Commune}}</b> <small>(${{x.Paiement}})</small></span><div>${{b}}</div>`;
                    list.appendChild(row);
                }});
            }}
        }});
        document.getElementById('stat').innerText = n;
    }}

    function filter() {{
        const v = document.getElementById('search').value.toLowerCase();
        document.querySelectorAll('.item-r').forEach(r => {{
            r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none';
        }});
    }}
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=850)
