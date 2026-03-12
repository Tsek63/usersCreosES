import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard v4")
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

# --- 3. DONNÉES GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")
df['Commune'] = df['Commune'].astype(str).str.strip()
df['Province'] = df['Province'].astype(str).str.strip()
json_records = df.to_json(orient='records')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Admin")
    with st.form("f_sync"):
        c_name = st.text_input("Commune")
        c_prov = st.text_input("Province")
        c_pay = st.selectbox("Paiement", ["Pre", "Post"])
        c_serv = st.text_input("Services (ex: Garderie|Activités)")
        if st.form_submit_button("SAUVEGARDER"):
            new_row = pd.DataFrame([{"Commune": c_name, "Province": c_prov, "Paiement": c_pay, "Services": c_serv}])
            df_up = pd.concat([df[df['Commune'] != c_name], new_row], ignore_index=True)
            conn.update(data=df_up)
            st.rerun()

# --- 5. INTERFACE ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ 
            --creos: #4169E1; --dark: #1e293b; --bg: #f1f5f9;
            --c-bxl: #ffeaa7; --c-bw: #81ecec; --c-hai: #a29bfe; 
            --c-lie: #74b9ff; --c-nam: #fab1a0; --c-lux: #FF43D0; 
        }}
        body {{ margin: 0; font-family: 'Segoe UI', sans-serif; display: flex; height: 100vh; background: var(--bg); overflow: hidden; }}
        #left {{ flex: 0 0 45%; padding: 15px; display: flex; flex-direction: column; }}
        #right {{ flex: 1; padding: 15px; display: flex; flex-direction: column; background: white; border-left: 2px solid #ddd; }}
        #map-container {{ flex: 1; background: white; border-radius: 12px; border: 1px solid #ccc; position: relative; overflow: hidden; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.5; cursor: pointer; }}
        .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .p-head {{ background: #eee; padding: 5px 10px; font-weight: bold; font-size: 12px; margin-top: 5px; }}
        .c-row {{ display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #eee; font-size: 13px; align-items: center; }}
        .badge {{ padding: 2px 5px; border-radius: 3px; color: white; font-size: 9px; margin-left: 2px; font-weight: bold; display: inline-flex; align-items: center; gap: 3px; }}
        #pop {{ position: fixed; background: white; border: 1px solid #999; padding: 15px; border-radius: 8px; display: none; z-index: 1000; width: 200px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>

<div id="pop">
    <b id="p-name"></b><br>
    <div id="p-form" style="font-size:12px; margin-top:10px;"></div>
    <button onclick="sendToSidebar()" style="width:100%; margin-top:10px; background:var(--creos); color:white; border:none; padding:5px; cursor:pointer;">CONFIGURER</button>
</div>

<div id="left">
    <div id="map-container">
        <svg id="svg" viewBox="0 0 950 700"></svg>
    </div>
    <div style="background:var(--dark); color:white; padding:10px; margin-top:10px; border-radius:8px; text-align:center;">
        <span id="total" style="font-size:24px; font-weight:bold; color:#38bdf8;">0</span> UNITÉS
    </div>
</div>

<div id="right">
    <input type="text" id="search" placeholder="🔍 Rechercher..." onkeyup="filterList()">
    <div id="list"></div>
</div>

<script>
    const dbRaw = {json_records};
    const fwb = {json.dumps(data_fwb)};
    let db = new Map();
    dbRaw.forEach(r => db.set(r.Commune, r));

    const meta = {{
        "Cantine Jour": {{ i: "fa-utensils", c: "#fb923c" }},
        "Cantine Semaine": {{ i: "fa-calendar-day", c: "#f59e0b" }},
        "Cantine Mois": {{ i: "fa-calendar-days", c: "#d97706" }},
        "Garderie": {{ i: "fa-clock", c: "#38bdf8" }},
        "Activités": {{ i: "fa-volleyball", c: "#4ade80" }}
    }};

    function init() {{
        const svg = document.getElementById('svg');
        // Ajustement des ancres pour que tout rentre
        const anchors = {{ 
            "Bruxelles": [350, 50], "Brabant Wallon": [350, 130], 
            "Hainaut": [50, 220], "Liège": [600, 100], 
            "Namur": [300, 350], "Luxembourg": [550, 450] 
        }};

        Object.entries(fwb).forEach(([prov, list]) => {{
            const cKey = prov.toLowerCase().includes('brabant') ? 'bw' : (prov.toLowerCase().includes('bruxelles') ? 'bxl' : prov.substring(0,3).toLowerCase());
            list.forEach((name, i) => {{
                const x = anchors[prov][0] + (i % 8 * 22), y = anchors[prov][1] + (Math.floor(i / 8) * 20);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 3);
                r.setAttribute("class", "commune" + (db.has(name) ? " active" : ""));
                r.style.fill = `var(--c-${{cKey}})`;
                r.onclick = (e) => {{
                    document.getElementById('p-name').innerText = name;
                    const d = db.get(name) || {{ Paiement:'Pre', Services:'' }};
                    document.getElementById('p-form').innerHTML = `
                        <input type="hidden" id="f-prov" value="${{prov}}">
                        Pay: <select id="f-pay"><option value="Pre" ${{d.Paiement==='Pre'?'selected':''}}>Pre</option><option value="Post" ${{d.Paiement==='Post'?'selected':''}}>Post</option></select><br><br>
                        ${{Object.keys(meta).map(s => `<label style="display:block"><input type="checkbox" class="f-srv" value="${{s}}" ${{d.Services.includes(s)?'checked':''}}> ${{s}}</label>`).join('')}}
                    `;
                    const pop = document.getElementById('pop');
                    pop.style.display='block'; pop.style.left=e.pageX+'px'; pop.style.top=e.pageY+'px';
                }};
                svg.appendChild(r);
            }});
        }});
        updateList();
    }}

    function sendToSidebar() {{
        const name = document.getElementById('p-name').innerText;
        const prov = document.getElementById('f-prov').value;
        const pay = document.getElementById('f-pay').value;
        const srvs = Array.from(document.querySelectorAll('.f-srv:checked')).map(x=>x.value).join('|');

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

    function updateList() {{
        const list = document.getElementById('list');
        list.innerHTML = ""; let n = 0;
        const provs = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
        
        provs.forEach(p => {{
            const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
            if(filtered.length > 0) {{
                const h = document.createElement('div'); h.className='p-head'; h.innerText=p; list.appendChild(h);
                filtered.forEach(x => {{
                    n++;
                    const row = document.createElement('div'); row.className='c-row';
                    const b = x.Services.split('|').filter(s=>s).map(s => `<span class="badge" style="background:${{meta[s].c}}"><i class="fa-solid ${{meta[s].i}}"></i> ${{s}}</span>`).join('');
                    row.innerHTML = `<span><b>${{x.Commune}}</b> <small>(${{x.Paiement}})</small></span><div>${{b}}</div>`;
                    list.appendChild(row);
                }});
            }}
        }});
        document.getElementById('total').innerText = n;
    }}

    function filterList() {{
        const v = document.getElementById('search').value.toLowerCase();
        document.querySelectorAll('.c-row').forEach(r => {{
            r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none';
        }});
    }}
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=850)
