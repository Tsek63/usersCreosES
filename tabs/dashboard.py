import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
from ui_components import audit_card

def render(df_ecoles, df_config, data_fwb, df_contacts):
    # --- 1. PRÉPARATION ---
    df_active = df_config[df_config['Extrascolaire'] == 'Oui'].copy()
    df_non = df_config[df_config['Extrascolaire'] == 'Non'].copy()
    
    def normalize_prov(p):
        p = str(p)
        if "Bruxelles" in p: return "Bruxelles"
        if "Brabant" in p: return "Brabant Wallon"
        return p

    tab1_rows = []
    for comm in df_active['Commune'].unique():
        grp = df_active[df_active['Commune'] == comm]
        prov = normalize_prov(grp['Province'].iloc[0] if not grp.empty else "Inconnu")
        nb_oui = len(grp)
        nb_non = len(df_non[df_non['Commune'] == comm])
        
        fase_fwb = df_ecoles[df_ecoles['Commune'] == comm]['Fase école'].astype(str).tolist()
        fase_cfg = df_config[df_config['Commune'] == comm]['Fase école'].astype(str).tolist()
        nb_sans = len([e for e in fase_fwb if e not in fase_cfg])
        
        tab1_rows.append({'Commune': comm, 'Province': prov, 'NbOui': nb_oui, 'NbNon': nb_non, 'NbSans': nb_sans})
    
    df_tab1 = pd.DataFrame(tab1_rows) if not tab1_rows == [] else pd.DataFrame(columns=['Province','Commune','NbOui','NbNon','NbSans'])

    # --- 2. STATS GAUCHE ---
    t_dash = len(df_tab1)
    p_dash = len(df_active[df_active['Paiement'] == 'Prépaiement'])
    po_dash = len(df_active[df_active['Paiement'] == 'Post-paiement'])
    s_dash = {
        "Cantine Jour": (int(df_active['Services'].str.contains("Cantine Jour", na=False).sum()), "#FFD700"),
        "Cantine Semaine": (int(df_active['Services'].str.contains("Cantine Semaine", na=False).sum()), "#FF8C00"),
        "Cantine Mois": (int(df_active['Services'].str.contains("Cantine Mois", na=False).sum()), "#FF0000"),
        "Garderie": (int(df_active['Services'].str.contains("Garderie", na=False).sum()), "#38bdf8"),
        "Activités": (int(df_active['Services'].str.contains("Activités", na=False).sum()), "#4ade80"),
    }

    # --- 3. CARTE & LISTE ---
    data_fwb_norm = {normalize_prov(k): v for k, v in data_fwb.items()}
    json_recs = df_tab1.to_json(orient='records')
    map_ref_json = json.dumps(data_fwb_norm)

    html_map = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --dark: #1e293b; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: white; }}
        #left {{ flex: 5; padding: 10px; display: flex; flex-direction: column; }}
        #right {{ flex: 7; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
        #map-box {{ flex: 0 0 300px; background: #262730; border-radius: 8px; margin-bottom: 8px; }}
        svg {{ width: 100%; height: 100%; }}
        .commune {{ stroke: rgba(255,255,255,0.1); stroke-width: 0.5; opacity: 0.3; cursor: help; }}
        .active {{ stroke: #ffffff !important; stroke-width: 1.5px !important; opacity: 1 !important; }}
        #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; font-size: 14px; outline: none; }}
        #list {{ flex: 1; overflow-y: auto; }}
        .stats-panel {{ background: var(--dark); color: white; padding: 15px; border-radius: 12px; }}
        .panel-header {{ text-align: center; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #f1f5f9; font-size: 11px; align-items: center; color: #334155; }}
        .commune-name {{ flex: 0 0 150px; font-weight: bold; color: #4169E1; font-size: 13px; }}
        .counts-container {{ display: flex; gap: 4px; flex-grow: 1; justify-content: flex-end; }}
        .cnt {{ padding: 2px 10px; border-radius: 4px; color: white; font-weight: bold; white-space: nowrap; font-size: 10px; }}
    </style></head>
    <body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div class="panel-header"><div style="font-size:12px; opacity:0.7;">COMMUNES ACTIVES</div><div style="font-size:42px; font-weight:bold;">{t_dash}</div></div>
            <div style="display:flex; gap:20px;">
                <div style="flex:1;">
                    <div style="font-size:11px; opacity:0.5; text-align:center; margin-bottom:8px;">PAIEMENT</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px;"><span>Prépaiement</span><span style="font-weight:bold; color:#ec4899;">{p_dash}</span></div>
                    <div style="display:flex; justify-content:space-between; font-size:13px;"><span>Post-paiement</span><span style="font-weight:bold; color:#38bdf8;">{po_dash}</span></div>
                </div>
                <div style="flex:1;">
                    <div style="font-size:11px; opacity:0.5; text-align:center; margin-bottom:8px;">SERVICES</div>
                    {"".join([f'<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px;"><span>{k}</span><span style="font-weight:bold; background:{v[1]}; padding:0 6px; border-radius:4px;">{v[0]}</span></div>' for k,v in s_dash.items()])}
                </div>
            </div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher..." onkeyup="doSearch()"><div id="list"></div></div>
    <script>
        const dbData = {json_recs}; const mapRef = {map_ref_json};
        const dbMap = new Map(); dbData.forEach(item => dbMap.set(item.Commune, item));
        function init() {{
            const svg = document.getElementById('svg');
            const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
            Object.entries(mapRef).forEach(([p, list]) => {{
                if (!anchors[p]) return;
                list.forEach((name, i) => {{
                    const x = anchors[p][0] + (i % 8 * 23); const y = anchors[p][1] + (Math.floor(i / 8) * 21);
                    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    rect.setAttribute("x", x); rect.setAttribute("y", y); rect.setAttribute("width", 20); rect.setAttribute("height", 18); rect.setAttribute("rx", 3);
                    rect.setAttribute("class", "commune" + (dbMap.has(name) ? " active" : ""));
                    rect.style.fill = "#ccc";
                    const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name; rect.appendChild(t);
                    svg.appendChild(rect);
                }});
            }});
            renderList();
        }}
        function renderList() {{
            const listDiv = document.getElementById('list'); listDiv.innerHTML = "";
            const provinces = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            provinces.forEach(p => {{
                const filtered = dbData.filter(d => d.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div'); h.style.background='#f8fafc'; h.style.padding='6px 10px'; h.style.fontSize='10px'; h.style.fontWeight='bold'; h.style.color='#94a3b8'; h.style.marginTop='10px'; h.innerText = p.toUpperCase(); listDiv.appendChild(h);
                    filtered.forEach(x => {{
                        const row = document.createElement('div'); row.className = 'item-row';
                        row.innerHTML = `<div class="commune-name">${{x.Commune}}</div><div class="counts-container">
                            <span class="cnt" style="background:#22c55e">✓ ${{x.NbOui}} École(s) utilisent</span>
                            <span class="cnt" style="background:#ef4444">✗ ${{x.NbNon}} Refus</span>
                            <span class="cnt" style="background:#94a3b8">? ${{x.NbSans}} Pas de choix</span>
                        </div>`;
                        listDiv.appendChild(row);
                    }});
                }}
            }});
        }}
        function doSearch() {{
            const val = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.item-row').forEach(row => {{ row.style.display = row.innerText.toLowerCase().includes(val) ? 'flex' : 'none'; }});
        }}
    </script></body></html>
    """
    components.html(html_map, height=750)

    # --- 4. AUDIT ---
    st.divider()
    st.subheader("🕵️ Audit de Qualité & Prospection")
    communes_actives = df_active['Commune'].unique()
    communes_avec_contacts = df_contacts['Commune'].unique()
    sans_contact = [c for c in communes_actives if c not in communes_avec_contacts]
    
    ecoles_fwb_total = set(df_ecoles['Fase école'].unique())
    ecoles_cfg_total = set(df_config['Fase école'].unique())
    en_attente = len(ecoles_fwb_total - ecoles_cfg_total)
    top_prov = df_active['Province'].value_counts().idxmax() if not df_active.empty else "N/A"

    aud1, aud2, aud3, aud4 = st.columns(4)
    with aud1: audit_card("Contacts manquants", f"{len(sans_contact)} commune(s)", "#ef4444" if sans_contact else "#22c55e", "⚠️")
    with aud2: audit_card("Écoles en attente", f"{en_attente} écoles", "#3b82f6", "🔔")
    with aud3: audit_card("Province Leader", top_prov, "#f59e0b", "🏆")
    with aud4: 
        taux = round((len(df_active) / len(df_ecoles)) * 100, 1) if not df_ecoles.empty else 0
        audit_card("Pénétration", f"{taux}%", "#8b5cf6", "📈")

    if sans_contact:
        with st.expander("🔎 Voir les communes actives sans contact"):
            st.write(", ".join(sorted(sans_contact)))
