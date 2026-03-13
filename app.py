import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Palette de couleurs fixe
COLORS = {
    "Cantine Jour": "#fb923c",
    "Cantine Semaine": "#f59e0b",
    "Cantine Mois": "#d97706",
    "Garderie": "#38bdf8",
    "Activités": "#4ade80",
    "Prépaiement": "#fb923c",
    "Post-paiement": "#38bdf8",
    "Bleu-Creos": "#4169E1",
    "Bleu-Canard": "#008080"
}

# Styles CSS globaux (Header et Blocs)
st.markdown(f"""
    <style>
        #MainMenu, footer, header {{visibility: hidden;}}
        .main-header {{
            background-color: {COLORS['Bleu-Creos']};
            padding: 15px 25px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            color: white;
        }}
        .header-title {{ font-size: 24px; font-weight: bold; margin: 0; }}
        .tt-button {{
            background-color: white;
            color: {COLORS['Bleu-Creos']};
            padding: 8px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
        }}
        /* Bloc Statistique Bleu Canard */
        .stats-duck-blue {{
            background-color: {COLORS['Bleu-Canard']};
            color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-badge {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES & CONNEXION ---
data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

# --- 3. ONGLETS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord", "✏️ Gestion des Communes"])

# --- TAB 1 : TABLEAU DE BORD (Restauré) ---
with tab1:
    json_records = df_gsheets.to_json(orient='records')
    html_map = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            :root {{ --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
            body {{ margin: 0; font-family: sans-serif; background: white; color: #1e293b; display: flex; height: 100vh; overflow: hidden; }}
            #left {{ flex: 4; padding: 10px; }} #right {{ flex: 6; padding: 10px; overflow-y: auto; border-left: 1px solid #f1f5f9; }}
            svg {{ width: 100%; height: 500px; border: 1px solid #eee; border-radius: 8px; background: #fafafa; }}
            .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
            .badge {{ padding: 2px 6px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; margin-left: 3px; }}
            .prov-header {{ background: #f8fafc; padding: 6px; font-weight: bold; font-size: 11px; color: #64748b; text-transform: uppercase; }}
        </style>
    </head>
    <body onload="init()">
        <div id="left"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div id="right"><input type="text" id="s" placeholder="🔍 Rechercher une commune..." style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:5px;" onkeyup="search()"><div id="list"></div></div>
        <script>
            const dbData = {json_records}; const mapRef = {json.dumps(data_fwb)};
            let db = new Map(); dbData.forEach(r => db.set(r.Commune, r));
            const servCols = {{ "Cantine Jour": "#fb923c", "Cantine Semaine": "#f59e0b", "Cantine Mois": "#d97706", "Garderie": "#38bdf8", "Activités": "#4ade80" }};
            function init() {{
                const svg = document.getElementById('svg');
                const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
                Object.entries(mapRef).forEach(([p, list]) => {{
                    const cP = p.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
                    list.forEach((n, i) => {{
                        const x = anchors[p][0] + (i % 8 * 23), y = anchors[p][1] + (Math.floor(i / 8) * 21);
                        const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                        r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 3);
                        r.style.fill = db.has(n) ? `var(--c-${{cP}})` : "#eee";
                        r.style.stroke = db.has(n) ? "#334155" : "#ddd";
                        const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = n;
                        r.appendChild(t); svg.appendChild(r);
                    }});
                }});
                render();
            }}
            function render() {{
                const l = document.getElementById('list'); l.innerHTML = "";
                ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"].forEach(p => {{
                    const res = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                    if(res.length) {{
                        const h = document.createElement('div'); h.className = 'prov-header'; h.innerText = p; l.appendChild(h);
                        res.forEach(x => {{ const row = document.createElement('div'); row.className = 'item-row';
                            const b = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{servCols[s]}}">${{s}}</span>`).join('');
                            row.innerHTML = `<span><b>${{x.Commune}}</b></span><div>${{b}}</div>`; l.appendChild(row);
                        }});
                    }}
                }});
            }}
            function search() {{ const v = document.getElementById('s').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'); }}
        </script>
    </body></html>
    """
    components.html(html_map, height=600)

# --- TAB 2 : GESTION DES COMMUNES ---
with tab2:
    # Calcul des Stats
    total_com = len(df_gsheets)
    pre_count = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    post_count = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    services_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    s_counts = {s: df_gsheets['Services'].str.contains(s, na=False).sum() for s in services_list}

    col_form, col_stats = st.columns([1.5, 1])

    with col_form:
        st.subheader("✏️ Gestion des données")
        prov_sel = st.selectbox("1. Province", list(data_fwb.keys()))
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1: comm_sel = st.selectbox("2. Commune", data_fwb[prov_sel])
            with c2: 
                pay_v = st.radio("3. Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("4. Services", services_list)
            
            save_c, del_c = st.columns(2)
            if save_c.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                new_row = pd.DataFrame([{"Commune": comm_sel, "Province": prov_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_final = pd.concat([df_gsheets[df_gsheets['Commune'] != comm_sel], new_row], ignore_index=True)
                conn.update(data=df_final); st.rerun()
            if del_c.form_submit_button("🗑️ SUPPRIMER", use_container_width=True):
                df_final = df_gsheets[df_gsheets['Commune'] != comm_sel]
                conn.update(data=df_final); st.rerun()

    with col_stats:
        # Bloc Statistique en Bleu Canard
        serv_rows_html = "".join([f'<div style="font-size: 0.9em; margin-bottom: 4px;"><span class="stat-badge" style="background:{COLORS[s]}"></span>{s} : <b>{count}</b></div>' for s, count in s_counts.items()])
        
        st.markdown(f"""
            <div class="stats-duck-blue">
                <div style="font-size: 0.8em; opacity: 0.9; text-transform: uppercase; letter-spacing:1px; margin-bottom: 5px;">Total des communes actives</div>
                <div style="font-size: 3em; font-weight: bold; margin-bottom: 20px; line-height: 1;">{total_com}</div>
                
                <div style="display: flex; gap: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">PAIEMENT</div>
                        <div style="font-size: 0.95em; margin-bottom: 8px;"><span class="stat-badge" style="background:{COLORS['Prépaiement']}"></span>Pré : <b>{pre_count}</b></div>
                        <div style="font-size: 0.95em;"><span class="stat-badge" style="background:{COLORS['Post-paiement']}"></span>Post : <b>{post_count}</b></div>
                    </div>
                    <div style="flex: 1.2;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">SERVICES</div>
                        {serv_rows_html}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # --- FILTRES & IMPRESSION ---
    st.subheader("🔍 Liste détaillée")
    df_d = df_gsheets.copy()
    if not df_d.empty:
        df_d = df_d.sort_values(by=['Province', 'Commune'])
        st.dataframe(df_d, use_container_width=True, hide_index=True)
