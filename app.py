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
        div.stDownloadButton > button:last-child {
            background-color: #2e7d32;
            color: white;
            border: none;
        }
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- 3. LOGIQUE DASHBOARD ---
nt = len(df_gsheets)
npr = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
npo = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
s_defs = [("Cantine Jour", "#ec4899", "fa-utensils"), ("Cantine Semaine", "#db2777", "fa-calendar-day"), ("Cantine Mois", "#be185d", "fa-calendar-days"), ("Garderie", "#38bdf8", "fa-clock"), ("Activités", "#4ade80", "fa-volleyball")]

b_html = ""
for n, c, i in s_defs:
    cnt = df_gsheets['Services'].str.contains(n, na=False).sum()
    b_html += f'<div style="background:{c};padding:8px 12px;border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;color:white;font-weight:bold;font-size:14px;"><span><i class="fa-solid {i}"></i> &nbsp; {n}</span><span style="background:rgba(0,0,0,0.2);padding:2px 8px;border-radius:5px;">{cnt}</span></div>'

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord & Carte", "✏️ Gestion des Communes"])

# --- TAB 1 : TABLEAU DE BORD ---
with tab1:
    # On injecte le bloc corrigé ici dans la partie gauche du dashboard
    json_recs = df_gsheets.to_json(orient='records')
    
    html_dashboard = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
            :root {{ --creos: #4169E1; --dark: #008080; --bg: #ffffff; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
            body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: #fff; }}
            #left {{ flex: 4.5; padding: 10px; display: flex; flex-direction: column; }}
            #right {{ flex: 5.5; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
            #map-box {{ flex: 0 0 350px; background: white; border-radius: 8px; border: 1px solid #eee; margin-bottom: 15px; }}
            svg {{ width: 100%; height: 100%; }}
            .commune {{ stroke: #fff; stroke-width: 0.5; }}
            .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
            .stats-container {{ background: var(--dark); color: white; padding: 20px; border-radius: 15px; flex: 1; overflow-y: auto; }}
            .grid-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }}
            .pay-box {{ padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 8px; }}
            .badge-v {{ padding: 8px 12px; border-radius: 8px; margin-bottom: 5px; display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; }}
        </style></head><body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-container">
            <div style="text-align:center;">
                <div style="font-size:12px;text-transform:uppercase;opacity:0.8;">Total des communes actives</div>
                <div style="font-size:50px;font-weight:bold;">{nt}</div>
            </div>
            <div class="grid-stats">
                <div style="border-right: 1px solid rgba(255,255,255,0.2); padding-right:10px;">
                    <div style="font-size:10px;opacity:0.7;margin-bottom:10px;text-transform:uppercase;">Paiement</div>
                    <div class="pay-box" style="background:#ec4899;"><small>PRÉPAIEMENT</small><br><b style="font-size:20px;">{npr}</b></div>
                    <div class="pay-box" style="background:#38bdf8;"><small>POST-PAIEMENT</small><br><b style="font-size:20px;">{npo}</b></div>
                </div>
                <div>
                    <div style="font-size:10px;opacity:0.7;margin-bottom:10px;text-transform:uppercase;">Services</div>
                    {b_html}
                </div>
            </div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;margin-bottom:10px;" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()"><div id="list"></div></div>
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
                    const h = document.createElement('div'); h.style.background='#f8fafc'; h.style.padding='6px'; h.style.fontSize='11px'; h.innerText = p; listDiv.appendChild(h);
                    filtered.forEach(x => {{ const row = document.createElement('div'); row.style="display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #f1f5f9;align-items:center;";
                        const badges = (x.Services || "").split('|').filter(s => s).map(s => `<span style="padding:2px 6px;border-radius:4px;color:white;font-size:9px;margin-left:3px;background:${{icons[s]?.c || '#ccc'}}">${{s}}</span>`).join('');
                        row.innerHTML = `<span style="font-size:13px;"><b>${{x.Commune}}</b></span><div>${{badges}}</div>`; listDiv.appendChild(row);
                    }});
                }}
            }});
        }}
        function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('#list > div').forEach(r => {{ if(r.innerText) r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'; }}); }}
    </script></body></html>"""
    components.html(html_dashboard, height=750)

# --- TAB 2 : GESTION ---
with tab2:
    st.header("✏️ Gestion des données")
    c1, c2 = st.columns([6, 4])
    with c1:
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()))
        with st.form("edit_form"):
            f1, f2 = st.columns(2)
            with f1: com_sel = st.selectbox("2. Commune", data_fwb[p_sel])
            with f2:
                pay_v = st.radio("3. Mode", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            if st.form_submit_button("💾 ENREGISTRER / MODIFIER"):
                new_r = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                conn.update(data=pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_r], ignore_index=True)); st.rerun()

    with c2:
        # Petit rappel rapide pour la gestion
        st.markdown(f"""
            <div style="background:#f1f5f9; padding:20px; border-radius:15px; border:1px solid #cbd5e1;">
                <h4 style="margin:0; color:#1e3a8a;">Statistiques rapides</h4>
                <hr>
                <p>Communes actives : <b>{nt}</b></p>
                <p>Prépaiement : <span style="color:#ec4899;font-weight:bold;">{npr}</span></p>
                <p>Post-paiement : <span style="color:#38bdf8;font-weight:bold;">{npo}</span></p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    # --- FILTRES ET EXPORTS ---
    df_res = df_gsheets.copy()
    st.subheader("🔍 Liste & Exports")
    st.dataframe(df_res.sort_values(['Province', 'Commune']), use_container_width=True, hide_index=True)
    
    # Boutons d'export
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        df_res.to_excel(wr, index=False)
    
    col_ex1, col_ex2 = st.columns(2)
    with col_ex2:
        st.download_button("📊 EXPORTER VERS EXCEL", data=buf.getvalue(), file_name="creos_export.xlsx", use_container_width=True)
