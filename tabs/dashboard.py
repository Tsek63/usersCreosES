import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

def render(df_ecoles, df_config, data_fwb):
    # --- 1. CALCULS DES DONNÉES ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_non = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    tab1_rows = []
    if not df_active.empty:
        # On boucle sur les communes qui ont au moins une école active
        for comm in df_active['Commune'].unique():
            grp = df_active[df_active['Commune'] == comm]
            prov = grp['Province'].iloc[0] if not grp.empty else "Inconnu"
            
            nb_oui = len(grp)
            nb_non = len(df_non[df_non['Commune'] == comm])
            
            # Calcul "Sans réponse" (?) : Écoles dans Ecoles mais pas dans Config
            ecoles_fase = df_ecoles[df_ecoles['Commune'] == comm]['Fase école'].astype(str).tolist()
            config_fase = df_config[df_config['Commune'] == comm]['Fase école'].astype(str).tolist()
            nb_sans = len([e for e in ecoles_fase if e not in config_fase])
            
            tab1_rows.append({
                'Commune': comm, 
                'Province': prov, 
                'NbOui': nb_oui, 
                'NbNon': nb_non, 
                'NbSans': nb_sans
            })
    
    df_tab1 = pd.DataFrame(tab1_rows) if tab1_rows else pd.DataFrame(columns=['Commune', 'Province', 'NbOui', 'NbNon', 'NbSans'])

    # --- 2. STATS PANNEAU DE GAUCHE ---
    t_dash = len(df_tab1)
    p_dash = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    po_dash = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    services_dict = {
        "Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00", 
        "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"
    }
    s_html = ""
    for s_name, s_color in services_dict.items():
        count = int(df_active['Services'].str.contains(s_name, na=False).sum())
        s_html += f'''<div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>{s_name}</span><span style="font-weight:bold; background:{s_color}; padding:0 6px; border-radius:4px;">{count}</span>
                      </div>'''

    # --- 3. PRÉPARATION JSON ---
    json_recs = df_tab1.to_json(orient='records')
    map_ref_json = json.dumps(data_fwb)

    # --- 4. BLOC HTML / JS ---
    html_map = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: white; color: #334155; }}
        #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; background: #fff; }}
        #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
        #map-box {{ flex: 0 0 320px; background: #262730; border-radius: 8px; margin-bottom: 10px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; }}
        .active {{ stroke: #ffffff !important; stroke-width: 1.5px !important; opacity: 1 !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; font-size: 14px; box-sizing: border-box; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; font-size: 12px; }}
        .item-row {{ display: flex; flex-direction: column; padding: 12px 10px; border-bottom: 1px solid #f1f5f9; }}
        .counts-container {{ display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }}
        .cnt {{ padding: 3px 10px; border-radius: 4px; color: white; font-size: 10.5px; font-weight: bold; width: fit-content; }}
        .prov-header {{ background: #f8fafc; padding: 5px 10px; font-size: 10px; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-top: 10px; }}
    </style></head>
    <body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div style="text-align:center; margin-bottom:10px; border-bottom:1px solid #334155; padding-bottom:5px;">
                <div style="opacity:0.7; font-size:10px;">COMMUNES ACTIVES</div>
                <div style="font-size:32px; font-weight:bold;">{t_dash}</div>
            </div>
            <div style="display:flex; gap:15px;">
                <div style="flex:1;">
                    <div style="opacity:0.5; font-size:9px; text-align:center; margin-bottom:4px;">PAIEMENT</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
                        <span>Pré</span><span style="font-weight:bold; color:#ec4899;">{p_dash}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span>Post</span><span style="font-weight:bold; color:#38bdf8;">{po_dash}</span>
                    </div>
                </div>
                <div style="flex:1.5;">
                    <div style="opacity:0.5; font-size:9px; text-align:center; margin-bottom:4px;">SERVICES</div>
                    {s_html}
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
            const provColors = {{
                "bruxelles": "#ffeaa7", "brabant": "#81ecec", "hainaut": "#a29bfe",
                "liege": "#74b9ff", "namur": "#fab1a0", "luxembourg": "#FF43D0"
            }};

            Object.entries(mapRef).forEach(([provName, communes]) => {{
                if (!anchors[provName]) return; 
                const colorKey = provName.toLowerCase().split(' ')[0].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const color = provColors[colorKey] || "#555";
                communes.forEach((name, i) => {{
                    const x = anchors[provName][0] + (i % 8 * 23);
                    const y = anchors[provName][1] + (Math.floor(i / 8) * 21);
                    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    rect.setAttribute("x", x); rect.setAttribute("y", y);
                    rect.setAttribute("width", 20); rect.setAttribute("height", 18); rect.setAttribute("rx", 3);
                    rect.setAttribute("class", "commune" + (dbMap.has(name) ? " active" : ""));
                    rect.style.fill = color;
                    svg.appendChild(rect);
                }});
            }});
            renderList();
        }}

        function renderList() {{
            const listDiv = document.getElementById('list');
            listDiv.innerHTML = "";
            const provs = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            
            provs.forEach(p => {{
                const filtered = dbData.filter(d => d.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div');
                    h.className = 'prov-header'; h.innerText = p;
                    listDiv.appendChild(h);
                    
                    filtered.forEach(x => {{
                        const row = document.createElement('div');
                        row.className = 'item-row';
                        row.innerHTML = `
                            <span><strong style="color:#4169E1; font-size:14px;">${{x.Commune}}</strong></span>
                            <div class="counts-container">
                                <span class="cnt" style="background:#22c55e" title="Utilisent Creos">✓ ${{x.NbOui}} Écoles utilisant Creos Extrascolaire</span>
                                <span class="cnt" style="background:#ef4444" title="N'utilisent pas Creos">✗ ${{x.NbNon}} Écoles qui ne l'utilisent pas</span>
                                <span class="cnt" style="background:#94a3b8" title="Sans configuration">? ${{x.NbSans}} Écoles sans choix enregistré</span>
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
