import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

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

# --- 4. FONCTION RAPPORT HTML ---
def get_print_html(df, filters_desc):
    icons_styles = {
        "Cantine Jour": "background:#fb923c; color:white;", "Cantine Semaine": "background:#f59e0b; color:white;",
        "Cantine Mois": "background:#d97706; color:white;", "Garderie": "background:#38bdf8; color:white;",
        "Activités": "background:#4ade80; color:white;"
    }
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; padding: 40px; color: #1e3a8a; }}
            .header {{ border-bottom: 3px solid #4169E1; margin-bottom: 20px; }}
            h1 {{ color: #4169E1; margin: 0; padding-bottom: 10px; }}
            .filters {{ background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #cbd5e1; font-size: 0.9em; }}
            .province-block {{ margin-top: 30px; page-break-inside: avoid; }}
            .province-title {{ background: #4169E1; color: white; padding: 10px 15px; border-radius: 5px; font-size: 1.1em; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #eff6ff; color: #1e3a8a; text-transform: uppercase; font-size: 0.75em; }}
            th, td {{ border: 1px solid #bfdbfe; padding: 10px; text-align: left; }}
            .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 4px; font-weight: bold; }}
            .pay-badge {{ color: #4169E1; font-weight: bold; border-bottom: 1px dotted #4169E1; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header"><h1>Utilisateurs de Creos Extrascolaire</h1><p>Rapport du {pd.Timestamp.now().strftime('%d/%m/%Y')}</p></div>
        <div class="filters"><strong>Filtres :</strong> {filters_desc}</div>
    """
    for p in sorted(df['Province'].unique()):
        html += f"<div class='province-block'><div class='province-title'>{p}</div><table><thead><tr><th>Commune</th><th>Paiement</th><th>Services actifs</th></tr></thead><tbody>"
        for _, row in df[df['Province'] == p].sort_values('Commune').iterrows():
            servs = row['Services'].split('|') if row['Services'] else []
            s_html = "".join([f'<span class="badge" style="{icons_styles.get(s, "background:#ccc;")}">{s}</span>' for s in servs if s])
            html += f"<tr><td><strong style='color:#1e40af;'>{row['Commune']}</strong></td><td><span class='pay-badge'>{row['Paiement']}</span></td><td>{s_html}</td></tr>"
        html += "</tbody></table></div>"
    return html + "</body></html>"

# --- 5. TABS ---
tab1, tab2 = st.tabs(["📊 Dashboard & Carte", "✏️ Gestion des Communes"])

# --- TAB 1 : DASHBOARD ---
with tab1:
    total_com_dash = len(df_gsheets)
    pre_count_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    post_count_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    services_list = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    s_stats_dash = {s: df_gsheets['Services'].str.contains(s, na=False).sum() for s in services_list}
    
    json_records = df_gsheets.to_json(orient='records')
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{ --creos: #4169E1; --dark: #1e293b; --bg: #ffffff; --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
            body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; background: var(--bg); }}
            #left {{ flex: 4; padding: 10px; display: flex; flex-direction: column; }}
            #right {{ flex: 6; padding: 10px; display: flex; flex-direction: column; background: white; border-left: 1px solid #eee; }}
            #map-box {{ flex: 0 0 400px; background: white; border-radius: 8px; border: 1px solid #eee; margin-bottom: 10px; }}
            svg {{ width: 100%; height: 100%; }}
            .commune {{ stroke: #fff; stroke-width: 0.5; }}
            .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
            #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; }}
            #list {{ flex: 1; overflow-y: auto; }}
            .stats-panel {{ background: var(--dark); color: white; padding: 15px; border-radius: 10px; overflow-y: auto; }}
            .stats-title {{ font-size: 11px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }}
            .main-count {{ font-size: 32px; font-weight: bold; color: #38bdf8; margin-bottom: 15px; border-bottom: 1px solid #334155; padding-bottom: 5px; }}
            .sub-stat {{ display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; padding: 2px 0; }}
            .serv-stat {{ display: inline-block; font-size: 10px; padding: 3px 8px; border-radius: 4px; margin: 2px; background: #334155; }}
            .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 13px; align-items: center; }}
            .badge {{ padding: 2px 6px; border-radius: 4px; color: white; font-size: 9px; font-weight: bold; margin-left: 2px; display: inline-flex; align-items: center; gap: 3px; }}
            .prov-label {{ background: #f8fafc; padding: 6px 10px; font-weight: bold; font-size: 11px; color: #64748b; text-transform: uppercase; }}
        </style>
    </head>
    <body onload="init()">
    <div id="left">
        <div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div class="stats-panel">
            <div class="stats-title">Total des communes actives</div>
            <div class="main-count">{total_com_dash}</div>
            <div style="margin-bottom: 15px;">
                <div class="sub-stat"><span>Prépaiement</span> <b style="color:#fb923c">{pre_count_dash}</b></div>
                <div class="sub-stat"><span>Post-paiement</span> <b style="color:#38bdf8">{post_count_dash}</b></div>
            </div>
            <div class="stats-title" style="margin-top:10px">Par Service</div>
            <div style="margin-top:5px;">
                <div class="serv-stat">Cantine Jour: {s_stats_dash['Cantine Jour']}</div>
                <div class="serv-stat">Cantine Sem.: {s_stats_dash['Cantine Semaine']}</div>
                <div class="serv-stat">Cantine Mois: {s_stats_dash['Cantine Mois']}</div>
                <div class="serv-stat">Garderie: {s_stats_dash['Garderie']}</div>
                <div class="serv-stat">Activités: {s_stats_dash['Activités']}</div>
            </div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher une commune..." onkeyup="doSearch()"><div id="list"></div></div>
    <script>
        const dbData = {json_records};
        const mapRef = {json.dumps(data_fwb)};
        let db = new Map(); dbData.forEach(r => db.set(r.Commune, r));
        const icons = {{ "Cantine Jour": {{ i: "fa-utensils", c: "#fb923c" }}, "Cantine Semaine": {{ i: "fa-calendar-day", c: "#f59e0b" }}, "Cantine Mois": {{ i: "fa-calendar-days", c: "#d97706" }}, "Garderie": {{ i: "fa-clock", c: "#38bdf8" }}, "Activités": {{ i: "fa-volleyball", c: "#4ade80" }} }};
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
                    const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = name;
                    r.appendChild(t); svg.appendChild(r);
                }});
            }});
            render();
        }}
        function render() {{
            const listDiv = document.getElementById('list'); listDiv.innerHTML = "";
            const provs = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            provs.forEach(p => {{
                const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div'); h.className = 'prov-label'; h.innerText = p; listDiv.appendChild(h);
                    filtered.forEach(x => {{ const row = document.createElement('div'); row.className = 'item-row';
                        const badges = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{icons[s]?.c || '#ccc'}}"><i class="fa-solid ${{icons[s]?.i || 'fa-tag'}}"></i> ${{s}}</span>`).join('');
                        row.innerHTML = `<span><b>${{x.Commune}}</b> <small>(${{x.Paiement}})</small></span><div>${{badges}}</div>`;
                        listDiv.appendChild(row);
                    }});
                }}
            }});
        }}
        function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => {{ r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'; }}); }}
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=750)

# --- TAB 2 : GESTION ---
with tab2:
    st.header("✏️ Gestion des données")
    
    # 60/40 Split
    col_left, col_right = st.columns([6, 4])

    with col_left:
        prov_selected = st.selectbox("1. Province", list(data_fwb.keys()), key="mgr_prov")
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1: 
                comm_selected = st.selectbox("2. Commune", data_fwb[prov_selected])
            with c2:
                pay_val = st.radio("3. Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_val = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            
            b1, b2 = st.columns(2)
            with b1:
                if st.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                    new_row = pd.DataFrame([{"Commune": comm_selected, "Province": prov_selected, "Paiement": pay_val, "Services": "|".join(serv_val)}])
                    df_final = pd.concat([df_gsheets[df_gsheets['Commune'] != comm_selected], new_row], ignore_index=True)
                    conn.update(data=df_final); st.rerun()
            with b2:
                if st.form_submit_button("🗑️ SUPPRIMER", use_container_width=True):
                    df_final = df_gsheets[df_gsheets['Commune'] != comm_selected]
                    conn.update(data=df_final); st.rerun()

with col_right:
        # Calcul des stats
        t_com = len(df_gsheets)
        t_pre = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
        t_post = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
        p_val = (t_pre / t_com * 100) if t_com > 0 else 0

        s_info = {
            "Cantine Jour": {"color": "#fb923c", "icon": "fa-utensils"},
            "Cantine Semaine": {"color": "#f59e0b", "icon": "fa-calendar-day"},
            "Cantine Mois": {"color": "#d97706", "icon": "fa-calendar-days"},
            "Garderie": {"color": "#38bdf8", "icon": "fa-clock"},
            "Activités": {"color": "#4ade80", "icon": "fa-volleyball"}
        }

        # --- CORRECTION ICI : Construction propre sans retours à la ligne parasites ---
        b_html = ""
        for s, info in s_info.items():
            count = df_gsheets['Services'].str.contains(s, na=False).sum()
            b_html += f'<div style="background:{info["color"]};padding:6px 12px;border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;color:white;font-weight:bold;font-size:13px;">'
            b_html += f'<span><i class="fa-solid {info["icon"]}"></i> &nbsp; {s}</span>'
            b_html += f'<span style="background:rgba(0,0,0,0.2);padding:2px 8px;border-radius:5px;">{count}</span></div>'

        # On assemble le tout dans une seule string finale
        final_ui = f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <div style="background-color: #008080; padding: 20px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1); font-family: sans-serif;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8;">Total Communes Actives</div>
                    <div style="font-size: 48px; font-weight: bold; line-height: 1;">{t_com}</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 12px; font-weight: bold;">
                    <span style="color: #fb923c;">PRÉ: {t_pre}</span>
                    <span style="color: #38bdf8;">POST: {t_post}</span>
                </div>
                <div style="width: 100%; background-color: rgba(255,255,255,0.2); height: 8px; border-radius: 10px; margin-bottom: 25px; overflow: hidden; display: flex;">
                    <div style="width: {p_val}%; background-color: #fb923c; height: 100%;"></div>
                    <div style="width: {100 - p_val}%; background-color: #38bdf8; height: 100%;"></div>
                </div>
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">Répartition par Service</div>
                {b_html}
            </div>
        """
        st.markdown(final_ui, unsafe_allow_html=True)

    # --- RESTE DU CODE (FILTRES ET TABLEAU) ---
    st.divider()
    st.subheader("🔍 Filtres & Impression")
    if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 2, 1])
    with f_col1: f_prov = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"f_prov_{st.session_state.reset_counter}")
    with f_col2: f_pay = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"f_pay_{st.session_state.reset_counter}")
    with f_col3: f_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"f_serv_{st.session_state.reset_counter}")
    with f_col4:
        st.write("")
        if st.button("❌ Effacer filtres", use_container_width=True): st.session_state.reset_counter += 1; st.rerun()

    df_display = df_gsheets.copy()
    f_list = []
    if f_prov: df_display = df_display[df_display['Province'].isin(f_prov)]; f_list.append(f"Provinces: {', '.join(f_prov)}")
    if f_pay: df_display = df_display[df_display['Paiement'].isin(f_pay)]; f_list.append(f"Paiement: {', '.join(f_pay)}")
    if f_serv:
        for s in f_serv: df_display = df_display[df_display['Services'].str.contains(s, na=False, regex=False)]
        f_list.append(f"Services: {', '.join(f_serv)}")
    
    if not df_display.empty:
        df_display = df_display.sort_values(by=['Province', 'Commune'])
        html_report = get_print_html(df_display, " | ".join(f_list) if f_list else "Tous les utilisateurs")
        st.download_button("🖨️ GÉNÉRER LE RAPPORT D'IMPRESSION COLORÉ", data=html_report, file_name="rapport_creos.html", mime="text/html", use_container_width=True)

    st.dataframe(df_display, use_container_width=True, hide_index=True)
