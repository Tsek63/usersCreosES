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

# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

# Nettoyage et Tri strict
df['Commune'] = df['Commune'].astype(str).str.strip()
df['Province'] = df['Province'].astype(str).str.strip()
order = {p: i for i, p in enumerate(data_fwb.keys())}
df['p_idx'] = df['Province'].map(order).fillna(99)
df = df.sort_values(['p_idx', 'Commune'])

# Conversion propre pour le JS
json_records = df.to_json(orient='records')

# --- 4. SIDEBAR (SAUVEGARDE MANUELLE SI LE PONT JS ECHOUE) ---
with st.sidebar:
    st.header("💾 Enregistrement")
    with st.form("form_save"):
        s_com = st.text_input("Commune (Nom exact)")
        s_prov = st.text_input("Province")
        s_pay = st.selectbox("Paiement", ["Pre", "Post"])
        s_serv = st.text_input("Services (ex: Garderie|Activités)")
        if st.form_submit_button("VALIDER GSHEETS"):
            new_row = pd.DataFrame([{"Commune": s_com, "Province": s_prov, "Paiement": s_pay, "Services": s_serv}])
            df_final = pd.concat([df[df['Commune'] != s_com], new_row], ignore_index=True)
            conn.update(data=df_final.drop(columns=['p_idx'], errors='ignore'))
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
            --creos: #4169E1; --dark: #1e293b; --bg: #f1f5f9;
            --c-bxl: #ffeaa7; --c-bw: #81ecec; --c-hai: #a29bfe; 
            --c-lie: #74b9ff; --c-nam: #fab1a0; --c-lux: #FF43D0; 
        }}
        body {{ margin: 0; font-family: 'Segoe UI', sans-serif; display: flex; height: 100vh; background: var(--bg); overflow: hidden; }}
        #left {{ flex: 0 0 38%; padding: 20px; display: flex; flex-direction: column; border-right: 2px solid #e2e8f0; }}
        #right {{ flex: 1; padding: 20px; display: flex; flex-direction: column; background: white; }}
        #map-box {{ height: 450px; background: white; border-radius: 12px; border: 1px solid #cbd5e1; margin-bottom: 15px; overflow: hidden; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: #fff; stroke-width: 0.5; cursor: pointer; }}
        .commune.active {{ stroke: #000 !important; stroke-width: 2px !important; }}
        #search {{ width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 15px; box-sizing: border-box; }}
        #list {{ flex: 1; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; }}
        .p-head {{ background: #f8fafc; padding: 10px; font-weight: bold; border-bottom: 1px solid #e2e8f0; color: #475569; text-transform: uppercase; font-size: 12px; }}
        .c-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
        .badge {{ padding: 3px 6px; border-radius: 4px; color: white; font-size: 10px; margin-left: 2px; display: inline-flex; align-items: center; gap: 3px; font-weight: bold; }}
        #popup {{ position: fixed; background: white; border: 1px solid #cbd5e1; padding: 15px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: none; z-index: 999; width: 250px; }}
        .btn {{ background: var(--creos); color: white; border: none; padding: 8px; width: 100%; border-radius: 5px; cursor: pointer; margin-top: 10px; font-weight: bold; }}
    </style>
</head>
<body>

<div id="popup">
    <h3 id="pop-name" style="margin:0 0 10px 0; color:var(--creos); font-size:16px;"></h3>
    <div id="pop-ui"></div>
    <button class="btn" onclick="copyToSidebar()">PRÉPARER SAUVEGARDE</button>
</div>

<div id="left">
    <div id="map-box"><svg id="svg"></svg></div>
    <div style="background: var(--dark); color: white; padding: 20px; border-radius: 12px; text-align: center;">
        <div id="total" style="font-size: 32px; font-weight: 900; color: #38bdf8;">0</div>
        <div style="font-size: 11px; letter-spacing: 1px;">UNITÉS ENREGISTRÉES</div>
    </div>
</div>

<div id="right">
    <input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()">
    <div id="list"></div>
</div>

<script>
    const raw = {json_records};
    const fwb = {json.dumps(data_fwb)};
    let db = new Map();
    raw.forEach(r => db.set(r.Commune, r));

    const sMeta = {{
        "Cantine Jour": {{ icon: "fa-utensils", c: "#fb923c" }},
        "Cantine Semaine": {{ icon: "fa-calendar-day", c: "#f59e0b" }},
        "Cantine Mois": {{ icon: "fa-calendar-days", c: "#d97706" }},
        "Garderie": {{ icon: "fa-clock", c: "#38bdf8" }},
        "Activités": {{ icon: "fa-volleyball", c: "#4ade80" }}
    }};

    function init() {{
        const svg = document.getElementById('svg');
        const anchors = {{ "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], "Hainaut": [40, 200], "Liège": [580, 80], "Namur": [280, 320], "Luxembourg": [530, 420] }};

        Object.entries(fwb).forEach(([prov, list]) => {{
            const cKey = prov.toLowerCase().includes('brabant') ? 'bw' : (prov.toLowerCase().includes('bruxelles') ? 'bxl' : prov.substring(0,3).toLowerCase());
            list.forEach((name, i) => {{
                const x = anchors[prov][0] + (i % 8 * 24), y = anchors[prov][1] + (Math.floor(i / 8) * 22);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 4);
                r.setAttribute("class", "commune" + (db.has(name) ? " active" : ""));
                r.style.fill = `var(--c-${{cKey}})`;
                r.onclick = (e) => showPop(name, prov, e);
                const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name;
                r.appendChild(t); svg.appendChild(r);
            }});
        }});
        render();
    }}

    function showPop(name, prov, e) {{
        const pop = document.getElementById('popup');
        const d = db.get(name) || {{ Paiement: 'Pre', Services: '' }};
        document.getElementById('pop-name').innerText = name;
        document.getElementById('pop-ui').innerHTML = `
            <input type="hidden" id="in-prov" value="${{prov}}">
            <div style="font-size:13px; margin-bottom:10px;">Paiement: 
                <select id="in-pay"><option value="Pre" ${{d.Paiement==='Pre'?'selected':''}}>Pre</option><option value="Post" ${{d.Paiement==='Post'?'selected':''}}>Post</option></select>
            </div>
            <div style="font-size:12px;">
                ${{Object.keys(sMeta).map(s => `<label style="display:block;"><input type="checkbox" class="in-srv" value="${{s}}" ${{d.Services.includes(s)?'checked':''}}> ${{s}}</label>`).join('')}}
            </div>
        `;
        pop.style.display = 'block'; pop.style.left = Math.min(e.pageX, window.innerWidth-270)+'px'; pop.style.top = Math.min(e.pageY, window.innerHeight-300)+'px';
    }}

    function copyToSidebar() {{
        const name = document.getElementById('pop-name').innerText;
        const prov = document.getElementById('in-prov').value;
        const pay = document.getElementById('in-pay').value;
        const srvs = Array.from(document.querySelectorAll('.in-srv:checked')).map(x => x.value).join('|');

        // On essaie d'envoyer aux inputs Streamlit
        const inputs = window.parent.document.querySelectorAll('input');
        if(inputs.length > 0) {{
            inputs.forEach(i => {{
                const label = i.closest('.stTextInput')?.querySelector('label')?.innerText || "";
                if(label.includes("Commune")) {{ i.value = name; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                if(label.includes("Province")) {{ i.value = prov; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                if(label.includes("Services")) {{ i.value = srvs; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }});
        }}
        document.getElementById('popup').style.display = 'none';
        alert("Données prêtes pour " + name + ". Cliquez sur VALIDER dans la colonne de gauche.");
    }}

    function render() {{
        const list = document.getElementById('list');
        list.innerHTML = ""; let n = 0;
        ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"].forEach(p => {{
            const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
            if(filtered.length > 0) {{
                const h = document.createElement('div'); h.className = 'p-head'; h.innerText = p; list.appendChild(h);
                filtered.forEach(x => {{
                    n++;
                    const row = document.createElement('div'); row.className = 'c-row';
                    const badges = x.Services.split('|').filter(s => s).map(s => `
                        <span class="badge" style="background:${{sMeta[s].c}}"><i class="fa-solid ${{sMeta[s].icon}}"></i> ${{s}}</span>
                    `).join('');
                    row.innerHTML = `<span><strong>${{x.Commune}}</strong> <small>${{x.Paiement}}</small></span><div>${{badges}}</div>`;
                    list.appendChild(row);
                }});
            }}
        }});
        document.getElementById('total').innerText = n;
    }}

    function doSearch() {{
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
