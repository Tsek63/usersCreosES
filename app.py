import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

st.markdown("""
    <style>
        /* Correction du padding supérieur */
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

# --- 3. CONNEXION GSHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes"])

# --- TAB 1 : DASHBOARD & CARTE ---
with tab1:
    t_dash = len(df_gsheets)
    p_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    po_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    s_dash = {
        "Cantine Jour": (df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum(), "#ec4899"),
        "Cantine Semaine": (df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum(), "#db2777"),
        "Cantine Mois": (df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum(), "#be185d"),
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
    
    # 1. ZONE DU HAUT : FORMULAIRE ET CHIFFRE TOTAL
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
        nt = len(df_gsheets)
        st.markdown(f"""
            <div style="background-color:#008080;padding:40px;border-radius:15px;color:white;text-align:center;">
                <div style="font-size:14px;text-transform:uppercase;opacity:0.8;">Total des communes actives</div>
                <div style="font-size:64px;font-weight:bold;">{nt}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 2. ZONE FILTRES
    st.subheader("🔍 Filtres & Liste")
    if 'rc' not in st.session_state: st.session_state.rc = 0
    f1, f2, f3, f4 = st.columns([2, 1, 2, 1])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")
    with f4: 
        if st.button("❌ Reset", use_container_width=True): st.session_state.rc += 1; st.rerun()

    # 3. ZONE DU BAS : LISTE À GAUCHE | GRAPHES À DROITE
    df_r = df_gsheets.copy()
    if not df_r.empty:
        if fl_p: df_r = df_r[df_r['Province'].isin(fl_p)]
        if fl_m: df_r = df_r[df_r['Paiement'].isin(fl_m)]
        if fl_s:
            for s in fl_s: df_r = df_r[df_r['Services'].str.contains(s, na=False)]
        
        df_sorted = df_r.sort_values(['Province', 'Commune'])
        col_list, col_viz = st.columns([6, 4], gap="medium")

        with col_list:
            st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=520)
        
        with col_viz:
            if not df_sorted.empty:
                # Graphique Paiement
                p_c = df_sorted['Paiement'].value_counts().reset_index()
                fig_p = px.pie(p_c, values='count', names='Paiement', hole=0.4, title="Modes de Paiement",
                               color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
                fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=40,b=0), legend=dict(orientation="h", y=-0.1))
                st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})

                # Graphique Services
                sl = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
                ct = [df_sorted['Services'].str.contains(s, na=False).sum() for s in sl]
                df_s = pd.DataFrame({'Service': sl, 'Nombre': ct})
                fig_s = px.bar(df_s, x='Nombre', y='Service', orientation='h', title="Popularité des Services",
                               color='Service', color_discrete_map={
                                  "Cantine Jour": "#ec4899", "Cantine Semaine": "#db2777",
                                  "Cantine Mois": "#be185d", "Garderie": "#38bdf8", "Activités": "#4ade80"})
                fig_s.update_layout(height=250, showlegend=False, margin=dict(l=0,r=0,t=40,b=0), xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
