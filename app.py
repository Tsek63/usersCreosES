import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import base64
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        .main-header {
            background-color: #4169E1;
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white; color: #4169E1; padding: 8px 18px;
            border-radius: 5px; text-decoration: none; font-weight: bold;
        }
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES DE RÉFÉRENCE ---
data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- FONCTION GÉNÉRATION HTML IMPRESSION ---
def generate_print_html(df_print, fl_p, fl_m, fl_s):
    date_str = pd.Timestamp.now().strftime("%d/%m/%Y à %H:%M")
    filter_parts = []
    if fl_p: filter_parts.append(f"Province(s) : {', '.join(fl_p)}")
    if fl_m: filter_parts.append(f"Paiement : {', '.join(fl_m)}")
    if fl_s: filter_parts.append(f"Services : {', '.join(fl_s)}")
    filter_text = " &nbsp;|&nbsp; ".join(filter_parts) if filter_parts else "Aucun filtre appliqué — Liste complète par province"
    province_colors = {
        "Bruxelles": "#ffeaa7", "Brabant Wallon": "#81ecec", "Hainaut": "#a29bfe",
        "Liège": "#74b9ff", "Namur": "#fab1a0", "Luxembourg": "#FF43D0",
    }
    rows_html = ""
    total = len(df_print)
    province_order = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"]
    for province in province_order:
        prov_df = df_print[df_print['Province'] == province].sort_values('Commune')
        if not prov_df.empty:
            bg_color = province_colors.get(province, "#e8f0fe")
            count = len(prov_df)
            rows_html += f"""
            <tr class="province-header">
                <td colspan="3" style="background-color:{bg_color}; border-left:4px solid #4169E1;">
                    📍 {province}
                    <span style="margin-left:10px; font-weight:normal; font-size:11px; opacity:0.7;">
                        ({count} commune{"s" if count > 1 else ""})
                    </span>
                </td>
            </tr>"""
            service_colors = {
                "Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00",
                "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"
            }
            for i, (_, row) in enumerate(prov_df.iterrows()):
                services_raw = row.get('Services', '') or ''
                services_list = [s.strip() for s in services_raw.split('|') if s.strip()]
                if services_list:
                    services_display = ' '.join([
                        f'<span style="background:{service_colors.get(s,"#ccc")};color:white;padding:2px 7px;'
                        f'border-radius:4px;font-size:10px;font-weight:bold;display:inline-block;margin:1px;'
                        f'-webkit-print-color-adjust:exact;print-color-adjust:exact;">{s}</span>'
                        for s in services_list
                    ])
                else:
                    services_display = '—'
                paiement = row.get('Paiement', '—') or '—'
                paiement_color = "#ec4899" if paiement == "Prépaiement" else "#38bdf8"
                row_bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
                rows_html += f"""
                <tr style="background-color:{row_bg};">
                    <td style="font-weight:600; color:#4169E1;">{row['Commune']}</td>
                    <td>
                        <span style="background:{paiement_color}; color:white; padding:2px 8px;
                                     border-radius:4px; font-size:11px; font-weight:bold;">
                            {paiement}
                        </span>
                    </td>
                    <td style="font-size:11px; color:#475569;">{services_display}</td>
                </tr>"""
    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Creos Extrascolaire — Impression</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; font-size: 12px; color: #333; padding: 20px; }}
    .header {{ background-color: #4169E1; color: white; padding: 14px 20px; border-radius: 8px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }}
    .header h1 {{ font-size: 18px; margin: 0; }}
    .header .date {{ font-size: 11px; opacity: 0.85; }}
    .filters {{ background: #f0f7ff; border-left: 4px solid #4169E1; padding: 8px 14px; margin-bottom: 12px; border-radius: 0 6px 6px 0; font-size: 11px; color: #334155; }}
    .filters strong {{ color: #4169E1; }}
    .summary {{ background: #008080; color: white; display: inline-block; padding: 6px 14px; border-radius: 6px; margin-bottom: 14px; font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 11.5px; }}
    thead th {{ background-color: #4169E1; color: white; padding: 8px 10px; text-align: left; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    tr.province-header td {{ padding: 7px 10px; font-weight: bold; font-size: 12px; color: #1e293b; border-top: 2px solid #4169E1; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    tr:not(.province-header) td {{ padding: 6px 10px; border-bottom: 1px solid #e2e8f0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .footer {{ margin-top: 20px; text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
    @page {{ margin: 0; size: A4; }}
    @media print {{ body {{ margin: 10mm 12mm; padding: 0; }} .no-print {{ display: none !important; }} thead {{ display: table-header-group; }} tr {{ page-break-inside: avoid; }} }}
</style></head><body>
<div class="header"><h1>🏫 Creos Extrascolaire — Liste des Communes</h1><span class="date">Imprimé le {date_str}</span></div>
<div class="filters"><strong>Filtres appliqués :</strong>&nbsp; {filter_text}</div>
<div class="summary">📍 Total : <strong>{total}</strong> commune{"s" if total > 1 else ""}</div>
<table><thead><tr><th style="width:35%">Commune</th><th style="width:22%">Mode de Paiement</th><th style="width:43%">Services</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<div class="footer">Creos Extrascolaire &mdash; Document généré automatiquement le {date_str}</div>
</body></html>"""
    return html


# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 4. TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes", "🏫 Écoles par Commune"])

# --- TAB 1 : DASHBOARD & CARTE ---
with tab1:
    t_dash = len(df_gsheets)
    p_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    po_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    s_dash = {
        "Cantine Jour": (df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum(), "#FFD700"),
        "Cantine Semaine": (df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum(), "#FF8C00"),
        "Cantine Mois": (df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum(), "#FF0000"),
        "Garderie": (df_gsheets['Services'].str.contains("Garderie", na=False).sum(), "#38bdf8"),
        "Activités": (df_gsheets['Services'].str.contains("Activités", na=False).sum(), "#4ade80")
    }
    json_recs = df_gsheets.to_json(orient='records')
    
    html_map = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
            :root {{ --dark: #1e293b; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
            body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; }}
            #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
            #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
            #map-box {{ flex: 0 0 300px; background: #262730; border-radius: 8px; margin-bottom: 8px; }}
            svg {{ width: 100%; height: 100%; }}
            .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; }}
            .active {{ stroke: #ffffff !important; stroke-width: 1.8px !important; opacity: 1 !important; }}
            #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; }}
            #list {{ flex: 1; overflow-y: auto; }}
            .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; }}
            .panel-header {{ text-align: center; border-bottom: 1px solid #334155; padding-bottom: 5px; margin-bottom: 10px; }}
            .main-count {{ font-size: 40px; font-weight: bold; }}
            .cols-container {{ display: flex; gap: 15px; }}
            .col-half {{ flex: 1; }}
            .v-item {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 11px; }}
            .v-val {{ font-weight: bold; padding: 1px 7px; border-radius: 4px; min-width: 20px; text-align: center; }}
            .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 12px; align-items: center; }}
            .badge-container {{ display: flex; flex-wrap: wrap; gap: 4px; justify-content: flex-end; }}
            .badge {{ padding: 2px 6px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; display: inline-flex; align-items: center; gap: 4px; }}
        </style></head><body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div class="panel-header"><div style="font-size:11px; opacity:0.7;">TOTAL COMMUNES ACTIVES</div><div class="main-count">{t_dash}</div></div>
            <div class="cols-container">
                <div class="col-half">
                    <div style="font-size:10px; opacity:0.5; text-align:center;">PAIEMENT</div>
                    <div class="v-item"><span>Prépaiement</span><span class="v-val" style="background:#ec4899">{p_dash}</span></div>
                    <div class="v-item"><span>Post-paiement</span><span class="v-val" style="background:#38bdf8">{po_dash}</span></div>
                </div>
                <div class="col-half">
                    <div style="font-size:10px; opacity:0.5; text-align:center;">SERVICES</div>
                    { "".join([f'<div class="v-item"><span>{k}</span><span class="v-val" style="background:{v[1]}">{v[0]}</span></div>' for k,v in s_dash.items()]) }
                </div>
            </div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()"><div id="list"></div></div>
    <script>
        const dbData = {json_recs}; const mapRef = {json.dumps(data_fwb)}; let db = new Map(); dbData.forEach(r => db.set(r.Commune, r));
        const icons = {{ "Cantine Jour": {{ i: "fa-utensils", c: "#FFD700" }}, "Cantine Semaine": {{ i: "fa-calendar-day", c: "#FF8C00" }}, "Cantine Mois": {{ i: "fa-calendar-days", c: "#FF0000" }}, "Garderie": {{ i: "fa-clock", c: "#38bdf8" }}, "Activités": {{ i: "fa-volleyball", c: "#4ade80" }} }};
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
                    filtered.forEach(x => {{ const row = document.createElement('div'); row.className = 'item-row';
                        const badges = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{icons[s]?.c || '#ccc'}}"><i class="fa-solid ${{icons[s]?.i || 'fa-tag'}}"></i> ${{s}}</span>`).join('');
                        row.innerHTML = `<span><strong style="color:#4169E1;">${{x.Commune}}</strong></span><div class="badge-container">${{badges}}</div>`; listDiv.appendChild(row);
                    }});
                }}
            }});
        }}
        function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => {{ r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'; }}); }}
    </script></body></html>"""
    components.html(html_map, height=750)

# --- TAB 2 : GESTION ---
with tab2:
    st.header("✏️ Gestion des Communes")
    nt = len(df_gsheets)
    p_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    po_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    
    c_form, c_stat = st.columns([6, 4])
    with c_form:
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()), key="m_p")
        with st.form("edit_form"):
            f1, f2 = st.columns(2)
            with f1: com_sel = st.selectbox("2. Commune", data_fwb[p_sel])
            with f2:
                pay_v = st.radio("3. Mode", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                    new_r = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                    df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_r], ignore_index=True)
                    conn.update(data=df_u); st.rerun()
            with sc2:
                if st.form_submit_button("🗑️ SUPPRIMER", use_container_width=True):
                    df_u = df_gsheets[df_gsheets['Commune'] != com_sel]
                    conn.update(data=df_u); st.rerun()

    with c_stat:
        st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<div style="background-color:#008080; padding:25px; border-radius:15px; color:white; text-align:center;">
<div style="font-size:12px; text-transform:uppercase; opacity:0.8; margin-bottom:5px;">Total des communes actives</div>
<div style="font-size:60px; font-weight:bold; margin-bottom:15px; line-height:1;">{nt}</div>
<div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); border-bottom:1px solid rgba(255,255,255,0.2); padding:15px 0; margin-bottom:15px;">
<div style="text-align:center;"><span style="display:block; font-size:18px; font-weight:bold; color:#ec4899;">{p_stat}</span><span style="font-size:11px; opacity:0.9;">Prépaiement</span></div>
<div style="text-align:center;"><span style="display:block; font-size:18px; font-weight:bold; color:#38bdf8;">{po_stat}</span><span style="font-size:11px; opacity:0.9;">Post-paiement</span></div>
</div>
<div style="text-align:left; font-size:11px; display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
<div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:6px; border-left:4px solid #FFD700;"><i class="fa-solid fa-utensils"></i> Cantine Jour : <b>{df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum()}</b></div>
<div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:6px; border-left:4px solid #FF8C00;"><i class="fa-solid fa-calendar-day"></i> Cantine Semaine : <b>{df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum()}</b></div>
<div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:6px; border-left:4px solid #FF0000;"><i class="fa-solid fa-calendar-days"></i> Cantine Mois : <b>{df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum()}</b></div>
<div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:6px; border-left:4px solid #38bdf8;"><i class="fa-solid fa-clock"></i> Garderie : <b>{df_gsheets['Services'].str.contains("Garderie", na=False).sum()}</b></div>
<div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:6px; border-left:4px solid #4ade80; grid-column: span 2;"><i class="fa-solid fa-volleyball"></i> Activités Extrascolaires : <b>{df_gsheets['Services'].str.contains("Activités", na=False).sum()}</b></div>
</div></div>
""", unsafe_allow_html=True)

    st.divider()

    if 'rc' not in st.session_state: st.session_state.rc = 0
    col_titre, col_reset = st.columns([7, 3])
    with col_titre: st.subheader("🔍 Filtres & Liste filtrée")
    with col_reset:
        st.write("##")
        if st.button("❌ Effacer les filtres", use_container_width=True):
            st.session_state.rc += 1; st.rerun()

    f1, f2, f3 = st.columns([2, 1, 2])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")

    df_r = df_gsheets.copy()
    if not df_r.empty:
        if fl_p: df_r = df_r[df_r['Province'].isin(fl_p)]
        if fl_m: df_r = df_r[df_r['Paiement'].isin(fl_m)]
        if fl_s:
            for s in fl_s: df_r = df_r[df_r['Services'].str.contains(s, na=False)]
        df_sorted = df_r.sort_values(['Province', 'Commune'])

        st.markdown("""
            <style>
                div.stDownloadButton > button { background-color: #008080 !important; color: white !important; border: none !important; width: 100% !important; }
                div.stDownloadButton > button:hover { background-color: #006666 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        col_excel, col_print = st.columns(2)
        with col_excel:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_sorted.to_excel(writer, index=False, sheet_name='Communes_Filtrees')
            st.download_button(label="📥 Exporter vers Excel", data=buffer.getvalue(), file_name="creos_export.xlsx", mime="application/vnd.ms-excel", use_container_width=True)

        with col_print:
            print_html = generate_print_html(df_sorted, fl_p, fl_m, fl_s)
            b64_print = base64.b64encode(print_html.encode('utf-8')).decode('ascii')
            components.html(f"""
            <style>* {{ box-sizing: border-box; margin: 0; padding: 0; }} body {{ margin: 0; padding: 0; }}
            button {{ background-color: #008080; color: white; border: none; padding: 0 16px; border-radius: 5px; cursor: pointer; width: 100%; height: 38px; font-size: 14px; font-weight: bold; font-family: sans-serif; display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 2px; }}
            button:hover {{ background-color: #006666; }}</style>
            <button onclick="openPrint()">🖨️ IMPRESSION</button>
            <script>
            function b64ToUtf8(str) {{ return decodeURIComponent(atob(str).split('').map(function(c) {{ return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2); }}).join('')); }}
            function openPrint() {{ var htmlContent = b64ToUtf8('{b64_print}'); var w = window.open('', '_blank'); w.document.open(); w.document.write(htmlContent); w.document.close(); setTimeout(function() {{ w.focus(); w.print(); }}, 600); }}
            </script>""", height=50)

        col_list, col_viz = st.columns([6, 4], gap="medium")
        with col_list:
            st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=520)
        with col_viz:
            if not df_sorted.empty:
                p_c = df_sorted['Paiement'].value_counts().reset_index()
                fig_p = px.pie(p_c, values='count', names='Paiement', hole=0.4, title="Modes de Paiement (Sélection)",
                               color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
                fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=40,b=0), legend=dict(orientation="h", y=-0.1))
                st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
                sl = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
                ct = [df_sorted['Services'].str.contains(s, na=False).sum() for s in sl]
                df_s = pd.DataFrame({'Service': sl, 'Nombre': ct})
                fig_s = px.bar(df_s, x='Nombre', y='Service', orientation='h', title="Popularité des Services (Sélection)",
                               color='Service', color_discrete_map={"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"})
                fig_s.update_layout(height=250, showlegend=False, margin=dict(l=0,r=0,t=40,b=0), xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})


# ============================================================
# --- TAB 3 : ÉCOLES PAR COMMUNE ---
# ============================================================
with tab3:

    # --- Chargement des données écoles depuis la feuille "Ecoles" du même GSheets ---
    try:
        df_ecoles = conn.read(worksheet="Ecoles", ttl=0).dropna(how="all")
        # Nettoyage des types
        for col in ['Fase PO', 'Fase école', 'Code postal']:
            df_ecoles[col] = df_ecoles[col].astype(str).str.replace(r'\.0$', '', regex=True)
    except Exception as e:
        st.error(
            f"⚠️ Impossible de charger la feuille **Ecoles**. "
            f"Assurez-vous d'avoir créé une feuille nommée **'Ecoles'** dans votre Google Sheets "
            f"et d'y avoir collé les données du fichier Excel fourni.\n\nErreur : `{e}`"
        )
        st.stop()

    # --- Communes actives dans Creos ---
    active_communes = set(df_gsheets['Commune'].tolist())
    all_po = sorted(df_ecoles['Nom PO'].dropna().unique().tolist())

    # --- Bandeau de stats global ---
    total_ecoles_global = len(df_ecoles)
    total_po_global = df_ecoles['Nom PO'].nunique()
    total_active_with_schools = len([c for c in active_communes if c in df_ecoles['Nom PO'].values])

    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <div style="display:flex; gap:12px; margin-bottom:16px;">
        <div style="flex:1; background:#4169E1; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8; letter-spacing:1px;">Total Écoles</div>
            <div style="font-size:38px; font-weight:bold; line-height:1.1;">{total_ecoles_global}</div>
        </div>
        <div style="flex:1; background:#008080; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8; letter-spacing:1px;">PO / Communes</div>
            <div style="font-size:38px; font-weight:bold; line-height:1.1;">{total_po_global}</div>
        </div>
        <div style="flex:1; background:#1e293b; color:white; padding:14px 18px; border-radius:10px; text-align:center;">
            <div style="font-size:10px; text-transform:uppercase; opacity:0.8; letter-spacing:1px;">Actives avec écoles</div>
            <div style="font-size:38px; font-weight:bold; line-height:1.1; color:#4ade80;">{total_active_with_schools}</div>
        </div>
        <div style="flex:3; background:#f8fafc; border:1px solid #e2e8f0; padding:14px 18px; border-radius:10px; display:flex; align-items:center;">
            <div>
                <div style="font-size:13px; color:#334155; font-weight:600; margin-bottom:4px;">
                    <i class="fa-solid fa-circle-info" style="color:#4169E1;"></i>
                    &nbsp;Comment utiliser cet onglet
                </div>
                <div style="font-size:11px; color:#64748b; line-height:1.6;">
                    Sélectionnez une <b>province</b> puis une <b>commune</b> pour afficher ses écoles.<br>
                    <span style="color:#4ade80; font-weight:bold;">✓ Vert</span> = commune active dans Creos &nbsp;|&nbsp;
                    <span style="color:#ef4444; font-weight:bold;">○ Gris</span> = commune non encore active
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Session state pour reset des filtres ---
    if 't3_rc' not in st.session_state:
        st.session_state.t3_rc = 0

    # --- Sélecteurs Province / Commune / Recherche + Bouton reset ---
    col_p3, col_c3, col_s3, col_btn3 = st.columns([2, 3, 3, 1.5])

    with col_p3:
        prov_tab3 = st.selectbox(
            "🗺️ Province",
            ["Toutes les provinces"] + list(data_fwb.keys()),
            key=f"t3_prov_{st.session_state.t3_rc}"
        )

    # Filtrer les communes disponibles selon la province choisie
    if prov_tab3 == "Toutes les provinces":
        communes_dispo = [""] + all_po
    else:
        communes_prov = data_fwb.get(prov_tab3, [])
        communes_dispo = [""] + sorted([c for c in communes_prov if c in df_ecoles['Nom PO'].values])

    with col_c3:
        commune_tab3 = st.selectbox(
            "🏘️ Commune",
            communes_dispo,
            key=f"t3_comm_{st.session_state.t3_rc}",
            format_func=lambda x: ("— Sélectionnez une commune" if x == "" else f"{'✅' if x in active_communes else '⚪'} {x}")
        )

    with col_s3:
        search_ecole = st.text_input(
            "🔍 Rechercher",
            key=f"t3_search_{st.session_state.t3_rc}",
            placeholder="Nom d'école, directeur, fase..."
        )

    with col_btn3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Effacer les filtres", key="t3_reset", use_container_width=True):
            st.session_state.t3_rc += 1
            st.rerun()

    if not commune_tab3 and not search_ecole:
        st.stop()

    if not commune_tab3 and search_ecole:
        # Recherche globale sur toutes les écoles si aucune commune sélectionnée
        df_search = df_ecoles[
            df_ecoles['Ecole'].astype(str).str.contains(search_ecole, case=False, na=False) |
            df_ecoles['Fase école'].astype(str).str.contains(search_ecole, case=False, na=False) |
            df_ecoles['Directeur/rice'].astype(str).str.contains(search_ecole, case=False, na=False)
        ]
        if df_search.empty:
            st.warning("Aucun résultat trouvé.")
        else:
            st.markdown(f"**{len(df_search)} résultat(s)** pour *\"{search_ecole}\"* sur toutes les communes")
            for _, row in df_search.iterrows():
                email_link = f'<a href="mailto:{row["Email"]}" style="color:#4169E1;">{row["Email"]}</a>' if pd.notna(row.get("Email")) and str(row.get("Email","")).strip() else "—"
                tel_link = f'<a href="tel:{row["Téléphone"]}" style="color:#4169E1;">{row["Téléphone"]}</a>' if pd.notna(row.get("Téléphone")) and str(row.get("Téléphone","")).strip() else "—"
                st.markdown(
                    f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #4169E1; border-radius:8px; padding:10px 16px; margin-bottom:8px;">'
                    f'<div style="font-weight:700; color:#1e293b; font-size:14px;">{row.get("Ecole","—")}</div>'
                    f'<div style="font-size:11px; color:#64748b; margin-top:2px;">PO : {row.get("Nom PO","—")} &nbsp;|&nbsp; Fase école : {row.get("Fase école","—")} &nbsp;|&nbsp; Dir. : {row.get("Directeur/rice","—")}</div>'
                    f'<div style="font-size:11px; color:#64748b; margin-top:2px;">{email_link} &nbsp;|&nbsp; {tel_link} &nbsp;|&nbsp; {row.get("Adresse","—")}, {row.get("Code postal","—")} {row.get("Localité","—")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        st.stop()

    # --- Données de la commune sélectionnée ---
    df_comm = df_ecoles[df_ecoles['Nom PO'] == commune_tab3].copy()
    fase_po = df_comm['Fase PO'].iloc[0] if not df_comm.empty else '—'
    is_active = commune_tab3 in active_communes

    # Infos Creos si commune active
    paiement_badge_html = ""
    services_badges_html = ""
    if is_active and not df_gsheets[df_gsheets['Commune'] == commune_tab3].empty:
        gsheet_row = df_gsheets[df_gsheets['Commune'] == commune_tab3].iloc[0]
        paiement_info = gsheet_row.get('Paiement', '—')
        services_info = gsheet_row.get('Services', '') or ''
        pc = "#ec4899" if paiement_info == "Prépaiement" else "#38bdf8"
        paiement_badge_html = f'<span style="background:{pc}; color:white; padding:4px 12px; border-radius:6px; font-size:11px; font-weight:bold;">{paiement_info}</span>'
        service_colors = {"Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"}
        for s in services_info.split("|"):
            s = s.strip()
            if s:
                sc = service_colors.get(s, "#999")
                services_badges_html += f'<span style="background:{sc}; color:white; padding:4px 10px; border-radius:6px; font-size:10px; font-weight:bold; margin-left:4px;">{s}</span>'

    active_color = "#4ade80" if is_active else "#64748b"
    active_text = "&#10003; Active dans Creos" if is_active else "&#9675; Non active dans Creos"
    active_txt_color = "#1e293b" if is_active else "white"

    active_badge_html = f'<span style="background:{active_color}; color:{active_txt_color}; padding:5px 14px; border-radius:20px; font-size:11px; font-weight:bold;">{active_text}</span>'
    all_badges_html = services_badges_html + paiement_badge_html + active_badge_html

    st.markdown(f'<div style="background:#1e293b; color:white; padding:13px 20px; border-radius:10px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;"><div style="display:flex; align-items:center; gap:16px;"><span style="font-size:20px; font-weight:bold;">&#127963; {commune_tab3}</span><span style="opacity:0.55; font-size:12px;">Fase PO : <b style="opacity:1;">{fase_po}</b></span><span style="opacity:0.55; font-size:12px;"><b style="opacity:1; color:#f8fafc;">{len(df_comm)}</b> &#233;cole(s)</span></div><div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">{all_badges_html}</div></div>', unsafe_allow_html=True)

    # --- Filtrage par recherche ---
    if search_ecole:
        mask = (
            df_comm['Ecole'].str.contains(search_ecole, case=False, na=False) |
            df_comm['Directeur.rice'].str.contains(search_ecole, case=False, na=False) |
            df_comm['Fase école'].astype(str).str.contains(search_ecole, case=False, na=False)
        )
        df_display = df_comm[mask]
    else:
        df_display = df_comm

    if df_display.empty:
        st.warning("Aucune école trouvée pour cette recherche.")
    else:
        st.markdown(
            f"<div style='font-size:12px; color:#64748b; margin-bottom:10px;'>"
            f"<b style='color:#334155;'>{len(df_display)}</b> école(s) affichée(s)</div>",
            unsafe_allow_html=True
        )

        # --- Affichage en cartes (2 par ligne) ---
        for i in range(0, len(df_display), 2):
            cols = st.columns(2, gap="medium")
            for j in range(2):
                idx = i + j
                if idx >= len(df_display):
                    break
                school = df_display.iloc[idx]
                with cols[j]:
                    email = school.get('Email', None)
                    phone = school.get('Téléphone', None)
                    bte_val = school.get('Bte', None)
                    bte = f" bte {bte_val}" if pd.notna(bte_val) and str(bte_val).strip() not in ['nan', ''] else ""
                    num = school.get('N°', '')
                    rue = school.get('Rue', '')
                    cp = school.get('Code postal', '')
                    loc = school.get('Localité', '')
                    adresse = f"{rue} {num}{bte}, {cp} {loc}".strip()

                    email_html = (
                        f'<a href="mailto:{email}" style="color:#4169E1; text-decoration:none;">{email}</a>'
                        if pd.notna(email) and str(email).strip() not in ['nan', '']
                        else '<span style="color:#94a3b8;">—</span>'
                    )
                    phone_html = (
                        f'<a href="tel:{phone}" style="color:#334155; text-decoration:none;">{phone}</a>'
                        if pd.notna(phone) and str(phone).strip() not in ['nan', '']
                        else '<span style="color:#94a3b8;">—</span>'
                    )

                    st.markdown(f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:10px; padding:16px;
                                margin-bottom:12px; border-left:5px solid #4169E1;
                                box-shadow: 0 2px 6px rgba(65,105,225,0.08);">
                        <div style="font-size:14px; font-weight:bold; color:#4169E1; margin-bottom:3px; line-height:1.3;">
                            🏫 {school['Ecole']}
                        </div>
                        <div style="font-size:10px; color:#94a3b8; margin-bottom:10px; letter-spacing:0.5px;">
                            N° FASE ÉCOLE : <b style="color:#475569; font-size:11px;">{school['Fase école']}</b>
                        </div>
                        <div style="border-top:1px solid #f1f5f9; padding-top:10px; font-size:12px; color:#334155; line-height:2;">
                            <div><i class="fa-solid fa-user" style="color:#4169E1; width:16px;"></i>&nbsp; <b>{school['Directeur.rice']}</b></div>
                            <div><i class="fa-solid fa-envelope" style="color:#4169E1; width:16px;"></i>&nbsp; {email_html}</div>
                            <div><i class="fa-solid fa-phone" style="color:#4169E1; width:16px;"></i>&nbsp; {phone_html}</div>
                            <div style="font-size:11px; color:#64748b; margin-top:4px;">
                                <i class="fa-solid fa-location-dot" style="color:#94a3b8; width:16px;"></i>&nbsp; {adresse}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()

        # --- Export Excel des écoles de la commune ---
        col_exp1, col_exp2, col_exp3 = st.columns([3, 2, 3])
        with col_exp2:
            buffer_e = io.BytesIO()
            export_df = df_display.drop(columns=['Rue', 'N°', 'Bte', 'Adresse'], errors='ignore')
            with pd.ExcelWriter(buffer_e, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name=f'Ecoles')
            st.download_button(
                label="📥 Exporter les écoles",
                data=buffer_e.getvalue(),
                file_name=f"ecoles_{commune_tab3.lower().replace(' ', '_').replace('/', '-')}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True,
                key="dl_ecoles"
            )


# --- FOOTER ---
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #1e293b;
        color: rgba(255,255,255,0.45); text-align: center; font-size: 11px;
        padding: 5px 0; letter-spacing: 1px; z-index: 9999;">
        © AJH 2026 — Creos Extrascolaire
    </div>
""", unsafe_allow_html=True)
