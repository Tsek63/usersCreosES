import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

def render(df_ecoles, df_config, data_fwb):
    # --- 1. CALCULS DES DONNÉES (Logique strictement identique à votre original) ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_non = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    tab1_rows = []
    # On identifie toutes les communes qui ont une configuration (Oui ou Non)
    all_communes_in_config = df_config['Commune'].unique()
    
    for comm in all_communes_in_config:
        # On récupère la province depuis la config ou depuis la liste FWB
        row_config = df_config[df_config['Commune'] == comm]
        prov = row_config['Province'].iloc[0] if not row_config.empty else "Inconnu"
        
        nb_oui = len(df_config[(df_config['Commune'] == comm) & (df_config['Extrascolaire'] == 'Oui')])
        nb_non = len(df_config[(df_config['Commune'] == comm) & (df_config['Extrascolaire'] == 'Non')])
        
        # Calcul des "Sans réponse" (?) : écoles dans FWB mais absentes de Config pour cette commune
        fase_fwb = set(df_ecoles[df_ecoles['Commune'] == comm]['Fase école'].astype(str).unique())
        fase_cfg = set(df_config[df_config['Commune'] == comm]['Fase école'].astype(str).unique())
        nb_sans = len(fase_fwb - fase_cfg)
        
        # On n'ajoute à la liste que si au moins une école est 'Oui' (votre règle originale)
        if nb_oui > 0:
            tab1_rows.append({
                'Commune': comm, 
                'Province': prov, 
                'NbOui': nb_oui, 
                'NbNon': nb_non, 
                'NbSans': nb_sans
            })
    
    df_tab1 = pd.DataFrame(tab1_rows)

    # --- 2. CHIFFRES POUR LE PANNEAU DE GAUCHE ---
    t_dash = len(df_tab1) if not df_tab1.empty else 0
    p_dash = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    po_dash = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    
    # Calcul des compteurs de services
    services_labels = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    services_colors = ["#FFD700", "#FF8C00", "#FF0000", "#38bdf8", "#4ade80"]
    s_html = ""
    for label, color in zip(services_labels, services_colors):
        count = int(df_active['Services'].str.contains(label, na=False).sum())
        s_html += f'''<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; font-size:11px;">
                        <span>{label}</span><span style="font-weight:bold; background:{color}; padding:1px 7px; border-radius:4px; min-width:20px; text-align:center;">{count}</span>
                      </div>'''

    # --- 3. PRÉPARATION DU JSON POUR JAVASCRIPT ---
    # On transforme le DataFrame en liste de dictionnaires pour le JS
    json_data = df_tab1.to_dict(orient='records')
    json_recs = json.dumps(json_data)
    map_ref = json.dumps(data_fwb)

    # --- 4. LE BLOC HTML / JS ---
    # Note : Utilisation de replace pour éviter les conflits d'accolades Python/JS
    html_template = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; --blue: #4169E1; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: white; }}
        #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
        #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
        #map-box {{ flex: 0 0 300px; background: #262730; border-radius: 8px; margin-bottom: 8px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; }}
        .active {{ stroke: #ffffff !important; stroke-width: 1.8px !important; opacity: 1 !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; font-size: 14px; outline: none; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .stats-panel {{ background: var(--dark); color: white; padding: 12px; border-radius: 12px; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 12px; align-items: center; color: #334155; }}
        .cnt {{ padding: 2px 8px; border-radius: 4px; color: white; font-size: 11px; font-weight: bold; margin-left: 4px; }}
        .prov-header {{ background: #f8fafc; padding: 6px 10px; font-size: 11px; font-weight: bold; color: #64748b; text-transform: uppercase; margin-top: 10px; }}
    </style></head>
    <body>
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div style="text-align:center; border-bottom:1px solid #334155; padding-bottom:5px; margin-bottom:10px;">
                <div style="font-size:10px; opacity:0.7;">COMMUNES ACTIVES</div>
                <div style="font-size:36px; font-weight:bold;">{t_dash}</div>
            </div>
            <div style="display:flex; gap:15px;">
                <div style="flex:1;">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">PAIEMENT</div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span>Prépaiement</span><span style="font-weight:bold; background:#ec4899; padding:1px 7px; border-radius:4px;">{p_dash}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px;">
                        <span>Post-paiement</span><span style="font-weight:bold; background:#38bdf8; padding:1px 7px; border-radius:4px;">{po_dash}</span>
                    </div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:10px; opacity:0.5; text-align:center; margin-bottom:5px;">SERVICES</div>
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
        const mapRef = {map_ref};
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

            Object.entries(mapRef).forEach(([provName, communes]) => {{
                const colorKey = provName.toLowerCase().split(' ')[0].normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const color = colors[colorKey] || "#ccc";
                
                communes.forEach((name, i) => {{
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
                    h.className = 'prov-header';
                    h.innerText = p;
                    listDiv.appendChild(h);
                    
                    filtered.forEach(x => {{
                        const row = document.createElement('div');
                        row.className = 'item-row';
                        row.innerHTML = `<span><strong>${{x.Commune}}</strong></span>
                            <div>
                                <span class="cnt" style="background:#22c55e">✓ ${{x.NbOui}}</span>
                                <span class="cnt" style="background:#ef4444">✗ ${{x.NbNon}}</span>
                                <span class="cnt" style="background:#94a3b8">? ${{x.NbSans}}</span>
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

        window.onload = init;
    </script></body></html>
    """
    components.html(html_template, height=750)
