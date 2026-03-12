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

# Nettoyage et Tri Python avant d'envoyer au JS
df_gsheets['Commune'] = df_gsheets['Commune'].astype(str).str.strip()
df_gsheets['Province'] = df_gsheets['Province'].astype(str).str.strip()
# Définir l'ordre des provinces pour le tri
ord_p = {p: i for i, p in enumerate(data_fwb.keys())}
df_gsheets['ord'] = df_gsheets['Province'].map(ord_p).fillna(99)
df_gsheets = df_gsheets.sort_values(['ord', 'Commune'])

json_data = df_gsheets.to_json(orient='records')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("💾 SAUVEGARDE")
    st.info("Cliquez sur une commune ou remplissez manuellement :")
    with st.form("main_form"):
        # Les labels doivent être très précis pour le JS
        f_commune = st.text_input("NOM_COMMUNE")
        f_province = st.text_input("NOM_PROVINCE")
        f_paiement = st.selectbox("MODE_PAIEMENT", ["Pre", "Post"])
        f_services = st.text_input("LISTE_SERVICES")
        btn = st.form_submit_button("VALIDER VERS GSHEETS")

if btn and f_commune:
    new_data = pd.DataFrame([{"Commune": f_commune, "Province": f_province, "Paiement": f_paiement, "Services": f_services}])
    # On retire l'ancienne version si elle existe
    df_clean = df_gsheets[df_gsheets['Commune'] != f_commune].drop(columns=['ord'], errors='ignore')
    updated_df = pd.concat([df_clean, new_data], ignore_index=True)
    conn.update(data=updated_df)
    st.success(f"Enregistré : {f_commune}")
    st.rerun()

# --- 5. HTML / JS ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ 
            --creos: #4169E1; --dark: #1e293b; --bg: #f8fafc;
            --color-bxl: #ffeaa7; --color-bw: #81ecec; --color-hai: #a29bfe; 
            --color-lie: #74b9ff; --color-nam: #fab1a0; --color-lux: #FF43D0; 
        }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; background: var(--bg); overflow: hidden; }}
        #left {{ flex: 0 0 40%; padding: 20px; border-right: 1px solid #ddd; display: flex; flex-direction: column; }}
        #right {{ flex: 1; padding: 20px; overflow-y: auto; background: white; }}
        #map {{ height: 450px; background: white; border-radius: 10px; border: 1px solid #eee; margin-bottom: 15px; position: relative; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: white; stroke-width: 0.5; cursor: pointer; }}
        .selected {{ stroke: black !important; stroke-width: 2px !important; }}
        .header-p {{ background: #f1f5f9; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 10px; border-radius: 5px; }}
        .row-c {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 15px; border-bottom: 1px solid #f8fafc; font-size: 13px; }}
        .badge {{ padding: 3px 7px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; margin-left: 3px; display: inline-flex; align-items: center; gap: 3px; }}
        #pop {{ position: fixed; background: white; border: 1px solid #ccc; padding: 15px; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); display: none; z-index: 100; width: 220px; }}
    </style>
</head>
<body>

<div id="pop">
    <h4 id="pop-title" style="margin-top:0"></h4>
    <div id="pop-content"></div>
    <button onclick="transfer()" style="width:100%; background:var(--creos); color:white; border:none; padding:8px; border-radius:5px; margin-top:10px; cursor:pointer">PREPARER SAUVEGARDE</button>
</div>

<div id="left">
    <div id="map"><svg id="svg-map" viewBox="0 0 850 650"></svg></div>
    <div style="background:var(--dark); color:white; padding:15px; border-radius:10px; text-align:center">
        <div id="stat" style="font-size:30px; font-weight:bold; color:#38bdf8">0</div>
        <div style="font-size:12px">COMMUNES ENREGISTRÉES</div>
    </div>
</div>

<div id="right">
    <div id="list-content"></div>
</div>

<script>
    const gsheetsData = {json_data};
    const fwb = {json.dumps(data_fwb)};
    let db = new Map();
    gsheetsData.forEach(d => db.set(d.Commune, d));

    const icons = {{
        "Cantine Jour": {{ icon: "fa-utensils", color: "#fb923c" }},
        "Cantine Semaine": {{ icon: "fa-calendar-day", color: "#f59e0b" }},
        "Cantine Mois": {{ icon: "fa-calendar-days", color: "#d97706" }},
        "Garderie": {{ icon: "fa-clock", color: "#38bdf8" }},
        "Activités": {{ icon: "fa-volleyball", color: "#4ade80" }}
    }};

    function initMap() {{
        const svg = document.getElementById('svg-map');
        const anchors = {{ "Bruxelles": [330, 40], "Brabant Wallon": [330, 110], "Hainaut": [40, 200], "Liège": [580, 80], "Namur": [280, 320], "Luxembourg": [530, 420] }};

        Object.entries(fwb).forEach(([prov, communes]) => {{
            const colorKey = prov.toLowerCase().includes('brabant') ? 'bw' : (prov.toLowerCase().includes('bruxelles') ? 'bxl' : prov.substring(0,3).toLowerCase());
            communes.forEach((name, i) => {{
                const x = anchors[prov][0] + (i % 8 * 24), y = anchors[prov][1] + (Math.floor(i / 8) * 22);
                const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 21); r.setAttribute("height", 19); r.setAttribute("rx", 4);
                r.setAttribute("class", "commune" + (db.has(name) ? " selected" : ""));
                r.style.fill = `var(--color-${{colorKey}})`;
                r.onclick = (e) => showPop(name, e, prov);
                const t = document.createElementNS("http://www.w3.org/2000/svg", "title");
                t.textContent = name;
                r.appendChild(t); svg.appendChild(r);
            }});
        }});
        renderList();
    }}

    function showPop(name, e, prov) {{
        const pop = document.getElementById('pop');
        const d = db.get(name) || {{ Paiement: 'Pre', Services: '' }};
        const sList = d.Services.split('|');
        document.getElementById('pop-title').innerText = name;
        document.getElementById('pop-content').innerHTML = `
            <input type="hidden" id="p-prov" value="${{prov}}">
            <div style="font-size:12px">Paiement: 
                <select id="p-pay"><option value="Pre" ${{d.Paiement==='Pre'?'selected':''}}>Pre</option><option value="Post" ${{d.Paiement==='Post'?'selected':''}}>Post</option></select>
            </div>
            <div style="font-size:11px; margin-top:10px">
                ${{Object.keys(icons).map(s => `<label style="display:block"><input type="checkbox" class="p-serv" value="${{s}}" ${{sList.includes(s)?'checked':''}}> ${{s}}</label>`).join('')}}
            </div>
        `;
        pop.style.display = 'block'; pop.style.left = e.pageX + 'px'; pop.style.top = e.pageY + 'px';
    }}

    function transfer() {{
        const name = document.getElementById('pop-title').innerText;
        const prov = document.getElementById('p-prov').value;
        const pay = document.getElementById('p-pay').value;
        const servs = Array.from(document.querySelectorAll('.p-serv:checked')).map(x => x.value).join('|');

        // PONT VERS STREAMLIT (Correction ciblée)
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(i => {{
            const label = i.parentElement.parentElement.querySelector('label');
            if(label) {{
                if(label.innerText.includes("NOM_COMMUNE")) {{ i.value = name; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                if(label.innerText.includes("NOM_PROVINCE")) {{ i.value = prov; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                if(label.innerText.includes("LISTE_SERVICES")) {{ i.value = servs; i.dispatchEvent(new Event('input', {{bubbles:true}})); }}
            }}
        }});
        document.getElementById('pop').style.display = 'none';
        alert("Prêt pour " + name + " ! Cliquez sur VALIDER à gauche.");
    }}

    function renderList() {{
        const cont = document.getElementById('list-content');
        cont.innerHTML = "";
        let count = 0;
        const provs = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
        
        provs.forEach(p => {{
            const items = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
            if(items.length > 0) {{
                const h = document.createElement('div'); h.className = "header-p"; h.innerText = p; cont.appendChild(h);
                items.forEach(it => {{
                    count++;
                    const row = document.createElement('div'); row.className = "row-c";
                    const srvs = it.Services.split('|').filter(x => x).map(s => `
                        <span class="badge" style="background:${{icons[s].color}}"><i class="fa-solid ${{icons[s].icon}}"></i> ${{s}}</span>
                    `).join('');
                    row.innerHTML = `<span><strong>${{it.Commune}}</strong> <small>${{it.Paiement}}</small></span><div>${{srvs}}</div>`;
                    cont.appendChild(row);
                }});
            }}
        }});
        document.getElementById('stat').innerText = count;
    }}
    initMap();
</script>
</body>
</html>
"""

components.html(html_code, height=800)
