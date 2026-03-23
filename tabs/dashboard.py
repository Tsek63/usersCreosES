import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

def render(df_ecoles, df_config, data_fwb):
    # --- 1. PRÉPARATION ET NORMALISATION DES DONNÉES ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_non = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    # Traduction pour Bruxelles (pour que la carte trouve les coordonnées)
    def normalize_prov(p):
        p = str(p)
        if "Bruxelles" in p: return "Bruxelles"
        if "Brabant" in p: return "Brabant Wallon"
        return p

    tab1_rows = []
    # On identifie les communes actives
    for comm in df_active['Commune'].unique():
        grp = df_active[df_active['Commune'] == comm]
        prov_raw = grp['Province'].iloc[0] if not grp.empty else "Inconnu"
        prov = normalize_prov(prov_raw)
        
        nb_oui = len(grp)
        nb_non = len(df_non[df_non['Commune'] == comm])
        
        # Calcul des écoles sans réponse (?)
        fase_fwb = df_ecoles[df_ecoles['Commune'] == comm]['Fase école'].astype(str).tolist()
        fase_cfg = df_config[df_config['Commune'] == comm]['Fase école'].astype(str).tolist()
        nb_sans = len([e for e in fase_fwb if e not in fase_cfg])
        
        tab1_rows.append({
            'Commune': comm, 
            'Province': prov, 
            'NbOui': nb_oui, 
            'NbNon': nb_non, 
            'NbSans': nb_sans
        })
    
    df_tab1 = pd.DataFrame(tab1_rows)

    # --- 2. STATS PANNEAU DE GAUCHE ---
    t_dash = len(df_tab1)
    p_dash = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    po_dash = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    s_dash = {
        "Cantine Jour":    (int(df_active['Services'].str.contains("Cantine Jour",    na=False).sum()), "#FFD700"),
        "Cantine Semaine": (int(df_active['Services'].str.contains("Cantine Semaine", na=False).sum()), "#FF8C00"),
        "Cantine Mois":    (int(df_active['Services'].str.contains("Cantine Mois",    na=False).sum()), "#FF0000"),
        "Garderie":        (int(df_active['Services'].str.contains("Garderie",        na=False).sum()), "#38bdf8"),
        "Activités":       (int(df_active['Services'].str.contains("Activités",       na=False).sum()), "#4ade80"),
    }

    # --- 3. PRÉPARATION DU JSON ---
    # On normalise aussi les clés du dictionnaire de référence FWB pour Bruxelles
    data_fwb_norm = {normalize_prov(k): v for k, v in data_fwb.items()}
    
    json_recs = df_tab1.to_json(orient='records')
    map_ref_json = json.dumps(data_fwb_norm)

    # --- 4. BLOC HTML / JS ---
    html_map = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: white; }}
        #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
        #right {{ flex: 8; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
        #map-box {{ flex: 0 0 300px; background: #262730; border-radius: 8px; margin-bottom: 8px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; cursor: help; }}
        .active {{ stroke: #ffffff !important; stroke-width: 1.8px !important; opacity: 1 !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #f1f5f9; font-size: 11px; align-items: center; color: #334155; }}
        .commune-name {{ flex: 0 0 150px; font-weight: bold; color: #4169E1; }}
        .counts-container {{ display: flex; gap: 4px; flex-grow: 1; justify-content: flex-end; }}
        .cnt {{ padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold; white-space: nowrap; font-size: 10px; }}
    </style></head>
    <body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div style="text-align:center; border-bottom:1px solid #334155; padding-bottom:5px; margin-bottom:10px;">
                <div style="font-size:10px; opacity:0.7;">COMMUNES ACTIVES</div><div style="font-size:36px; font-weight:bold;">{t_dash}</div>
            </div>
            <div style="display:flex; gap:15px;">
                <div style="flex:1;">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">PAIEMENT</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;"><span>Pré</span><span style="font-weight:bold; color:#ec4899;">{p_dash}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span>Post</span><span style="font-weight:bold; color:#38bdf8;">{po_dash}</span></div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">SERVICES</div>
                    {"".join([f'<div style="display:flex; justify-content:space-between; font-size:10px; margin-bottom:2px;"><span>{k}</span><span style="font-weight:bold; background:{v[1]}; padding:0 6px; border-radius:4px;">{v[0]}</span></div>' for k,v in s_dash.items()])}
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
        const dbMap = new Map();
        dbData.forEach(item => dbMap.set(item.Commune, item));

        function init() {{
            const svg = document.getElementById('svg');
            const anchors = {{
                "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180],
                "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400]
            }};
            const colors = {{
                "bruxelles": "#ffeaa7", "brabant": "#81ecec", "hainaut": "#a29bfe",
                "liege": "#74b9ff", "namur": "#fab1a0", "luxembourg": "#FF43D0"
            }};

            Object.entries(mapRef).forEach(([provName, list]) => {{
                if (!anchors[provName]) return;
                const colorKey = provName.toLowerCase().split(' ')[0].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const color = colors[colorKey] || "#ccc";
                
                list.forEach((name, i) => {{
                    const x = anchors[provName][0] + (i % 8 * 23);
                    const y = anchors[provName][1] + (Math.floor(i / 8) * 21);
                    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    rect.setAttribute("x", x); rect.setAttribute("y", y);
                    rect.setAttribute("width", 20); rect.setAttribute("height", 18); rect.setAttribute("rx", 3);
                    rect.setAttribute("class", "commune" + (dbMap.has(name) ? " active" : ""));
                    rect.style.fill = color;
                    
                    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
                    title.textContent = name;
                    rect.appendChild(title);
                    
                    svg.appendChild(rect);
                }});
            }});
            renderList();
        }}

        function renderList() {{
            const listDiv = document.getElementById('list');
            listDiv.innerHTML = "";
            const provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            
            provinces.forEach(p => {{
                const filtered = dbData.filter(d => d.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div');
                    h.style.background='#f8fafc'; h.style.padding='6px 10px'; h.style.fontSize='10px'; h.style.fontWeight='bold'; h.style.color='#94a3b8'; h.style.marginTop='10px';
                    h.innerText = p.toUpperCase();
                    listDiv.appendChild(h);
                    
                    filtered.forEach(x => {{
                        const row = document.createElement('div');
                        row.className = 'item-row';
                        row.innerHTML = `
                            <div class="commune-name">${{x.Commune}}</div>
                            <div class="counts-container">
                                <span class="cnt" style="background:#22c55e">✓ ${{x.NbOui}} Écoles avec Creos</span>
                                <span class="cnt" style="background:#ef4444">✗ ${{x.NbNon}} Inactives</span>
                                <span class="cnt" style="background:#94a3b8">? ${{x.NbSans}} Sans choix</span>
                            </div>`;
                        listDiv.appendChild(row);
                    }});
                }}
            }});
        }}

        function doSearch() {{
            const val = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.item-row').forEach(row => {{
                row.style.display = row.innerText.toLowerCase().includes(val) ? 'flex' : 'none';
            }});
        }}
    </script></body></html>
    """
    components.html(html_map, height=750)
