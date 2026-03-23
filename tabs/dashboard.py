import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

def render(df_ecoles, df_config, data_fwb):
    # --- 1. CALCULS EXACTS (Identiques à votre original) ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_non = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    tab1_rows = []
    # On parcourt les communes qui ont au moins une école active
    for comm in df_active['Commune'].unique():
        grp = df_active[df_active['Commune'] == comm]
        prov = grp['Province'].iloc[0]
        nb_oui = len(grp)
        nb_non = len(df_non[df_non['Commune'] == comm])
        
        # Calcul des écoles "Sans configuration" (présentes dans Ecoles mais pas dans Config)
        fase_ecoles_comm = df_ecoles[df_ecoles['Commune'] == comm]['Fase école'].astype(str).tolist()
        fase_config_comm = df_config[df_config['Commune'] == comm]['Fase école'].astype(str).tolist()
        nb_sans = len([e for e in fase_ecoles_comm if e not in fase_config_comm])
        
        tab1_rows.append({
            'Commune': comm, 'Province': prov, 'NbEcoles': nb_oui,
            'NbOui': nb_oui, 'NbNon': nb_non, 'NbSans': nb_sans
        })
    
    df_tab1 = pd.DataFrame(tab1_rows) if tab1_rows else pd.DataFrame(columns=['Commune', 'Province', 'NbEcoles', 'NbOui', 'NbNon', 'NbSans'])

    # --- 2. VARIABLES POUR LE DASHBOARD ---
    t_dash = df_tab1['Commune'].nunique() if not df_tab1.empty else 0
    p_dash = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    po_dash = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    s_dash = {
        "Cantine Jour":    (int(df_active['Services'].str.contains("Cantine Jour",    na=False).sum()), "#FFD700"),
        "Cantine Semaine": (int(df_active['Services'].str.contains("Cantine Semaine", na=False).sum()), "#FF8C00"),
        "Cantine Mois":    (int(df_active['Services'].str.contains("Cantine Mois",    na=False).sum()), "#FF0000"),
        "Garderie":        (int(df_active['Services'].str.contains("Garderie",        na=False).sum()), "#38bdf8"),
        "Activités":       (int(df_active['Services'].str.contains("Activités",       na=False).sum()), "#4ade80"),
    }

    # --- 3. INJECTION HTML / JS (Structure Gauche/Droite) ---
    json_recs = df_tab1.to_json(orient='records')
    map_ref_json = json.dumps(data_fwb)

    html_map = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background-color: white; }}
        #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
        #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
        #map-box {{ flex: 0 0 300px; background: #262730; border-radius: 8px; margin-bottom: 8px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; }}
        .active {{ stroke: #ffffff !important; stroke-width: 1.8px !important; opacity: 1 !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; font-size: 14px; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; }}
        .panel-header {{ text-align: center; border-bottom: 1px solid #334155; padding-bottom: 5px; margin-bottom: 10px; }}
        .main-count {{ font-size: 40px; font-weight: bold; }}
        .cols-container {{ display: flex; gap: 15px; }}
        .col-half {{ flex: 1; }}
        .v-item {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 11px; }}
        .v-val {{ font-weight: bold; padding: 1px 7px; border-radius: 4px; min-width: 20px; text-align: center; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 12px; align-items: center; color: #334155; }}
        .cnt {{ padding: 2px 8px; border-radius: 4px; color: white; font-size: 11px; font-weight: bold; margin-left: 4px; }}
    </style></head>
    <body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div class="panel-header"><div style="font-size:11px; opacity:0.7;">COMMUNES ACTIVES</div><div class="main-count">{t_dash}</div></div>
            <div class="cols-container">
                <div class="col-half">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">PAIEMENT</div>
                    <div class="v-item"><span>Prépaiement</span><span class="v-val" style="background:#ec4899">{p_dash}</span></div>
                    <div class="v-item"><span>Post-paiement</span><span class="v-val" style="background:#38bdf8">{po_dash}</span></div>
                </div>
                <div class="col-half">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">SERVICES</div>
                    { "".join([f'<div class="v-item"><span>{k}</span><span class="v-val" style="background:{v[1]}">{v[0]}</span></div>' for k,v in s_dash.items()]) }
                </div>
            </div>
        </div>
    </div>
    <div id="right">
        <input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()">
        <div id="list"></div>
    </div>
    <script>
        const dbData = {json_recs};
        const mapRef = {map_ref_json};
        let db = new Map();
        dbData.forEach(r => db.set(r.Commune, r));

        function init() {{
            const svg = document.getElementById('svg');
            const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
            Object.entries(mapRef).forEach(([pName, list]) => {{
                const cleanP = pName.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
                list.forEach((name, i) => {{
                    const x = anchors[pName][0] + (i % 8 * 23), y = anchors[pName][1] + (Math.floor(i / 8) * 21);
                    const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 3);
                    r.setAttribute("class", "commune" + (db.has(name) ? " active" : ""));
                    r.style.fill = `var(--c-${{cleanP}})`;
                    const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name; r.appendChild(t); svg.appendChild(r);
                }});
            }});
            render();
        }}

        function render() {{
            const listDiv = document.getElementById('list');
            listDiv.innerHTML = "";
            const provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            provinces.forEach(p => {{
                const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div');
                    h.style.background='#f8fafc'; h.style.padding='6px 10px'; h.style.fontSize='11px'; h.style.fontWeight='bold'; h.style.color='#64748b';
                    h.innerText = p.toUpperCase();
                    listDiv.appendChild(h);
                    filtered.forEach(x => {{
                        const row = document.createElement('div');
                        row.className = 'item-row';
                        row.innerHTML = `<span><strong>${{x.Commune}}</strong></span>
                            <div>
                                <span class="cnt" style="background:#22c55e" title="Actives">✓ ${{x.NbOui}}</span>
                                <span class="cnt" style="background:#ef4444" title="Non">✗ ${{x.NbNon}}</span>
                                <span class="cnt" style="background:#94a3b8" title="Inconnu">? ${{x.NbSans}}</span>
                            </div>`;
                        listDiv.appendChild(row);
                    }});
                }}
            }});
        }}

        function doSearch() {{
            const v = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.item-row').forEach(r => {{
                r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none';
            }});
        }}
    </script></body></html>
    """
    components.html(html_map, height=750)
