import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Manager")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

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

# --- 4. FONCTION IMPRESSION ---
def get_print_html(df, filters_desc):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            h1 {{ color: #4169E1; border-bottom: 2px solid #4169E1; }}
            .filter-info {{ background: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; }}
            .province-title {{ background: #1e293b; color: white; padding: 8px; margin-top: 20px; border-radius: 3px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f8fafc; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>Rapport Creos - Liste des Communes</h1>
        <div class="filter-info"><strong>Filtres appliqués :</strong> {filters_desc}</div>
    """
    
    provinces = df['Province'].unique()
    for p in sorted(provinces):
        html += f"<h3 class='province-title'>{p}</h3>"
        html += "<table><tr><th>Commune</th><th>Paiement</th><th>Services</th></tr>"
        sub_df = df[df['Province'] == p].sort_values('Commune')
        for _, row in sub_df.iterrows():
            html += f"<tr><td>{row['Commune']}</td><td>{row['Paiement']}</td><td>{row['Services']}</td></tr>"
        html += "</table>"
    
    html += "</body></html>"
    return html

# --- 5. NAVIGATION ---
tab1, tab2 = st.tabs(["📊 Dashboard & Carte", "✏️ Gestion des Communes"])

# --- TAB 1 (Vue Carte/Liste) ---
with tab1:
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
            #map-box {{ flex: 0 0 450px; background: white; border-radius: 8px; border: 1px solid #eee; margin-bottom: 10px; }}
            svg {{ width: 100%; height: 100%; }}
            .commune {{ stroke: #fff; stroke-width: 0.5; }}
            .active {{ stroke: #000 !important; stroke-width: 1.5px !important; }}
            #search {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; }}
            #list {{ flex: 1; overflow-y: auto; border: 1px solid #f9f9f9; }}
            .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 13px; align-items: center; }}
            .badge {{ padding: 2px 6px; border-radius: 4px; color: white; font-size: 9px; font-weight: bold; margin-left: 2px; display: inline-flex; align-items: center; gap: 3px; }}
            .prov-label {{ background: #f8fafc; padding: 6px 10px; font-weight: bold; font-size: 11px; color: #64748b; text-transform: uppercase; }}
        </style>
    </head>
    <body onload="init()">
    <div id="left"><div id="map-box"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div style="background:var(--dark); color:white; padding:15px; border-radius:10px; text-align:center;">
            <div id="total" style="font-size:28px; font-weight:bold; color:#38bdf8;">0</div>
            <div style="font-size:10px; letter-spacing:1px">UNITÉS ENREGISTRÉES</div>
        </div>
    </div>
    <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher..." onkeyup="doSearch()"><div id="list"></div></div>
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
            const listDiv = document.getElementById('list'); listDiv.innerHTML = ""; let count = 0;
            const provs = ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"];
            provs.forEach(p => {{
                const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                if(filtered.length > 0) {{
                    const h = document.createElement('div'); h.className = 'prov-label'; h.innerText = p; listDiv.appendChild(h);
                    filtered.forEach(x => {{ count++; const row = document.createElement('div'); row.className = 'item-row';
                        const badges = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{icons[s]?.c || '#ccc'}}"><i class="fa-solid ${{icons[s]?.i || 'fa-tag'}}"></i> ${{s}}</span>`).join('');
                        row.innerHTML = `<span><b>${{x.Commune}}</b> <small>(${{x.Paiement}})</small></span><div>${{badges}}</div>`;
                        listDiv.appendChild(row);
                    }});
                }}
            }});
            document.getElementById('total').innerText = count;
        }}
        function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => {{ r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'; }}); }}
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=750)

# --- TAB 2 (Gestion & Impression) ---
with tab2:
    st.header("✏️ Gestion & Filtres")
    
    # --- FORMULAIRE ---
    prov_selected = st.selectbox("1. Province", list(data_fwb.keys()), key="mgr_prov")
    with st.form("edit_form"):
        col1, col2 = st.columns(2)
        with col1: comm_selected = st.selectbox("2. Commune", data_fwb[prov_selected])
        with col2:
            pay_val = st.radio("3. Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
            serv_val = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
        
        c_save, c_del = st.columns(2)
        if c_save.form_submit_button("💾 ENREGISTRER", use_container_width=True):
            new_row = pd.DataFrame([{"Commune": comm_selected, "Province": prov_selected, "Paiement": pay_val, "Services": "|".join(serv_val)}])
            df_final = pd.concat([df_gsheets[df_gsheets['Commune'] != comm_selected], new_row], ignore_index=True)
            conn.update(data=df_final); st.rerun()
        if c_del.form_submit_button("🗑️ SUPPRIMER", use_container_width=True):
            df_final = df_gsheets[df_gsheets['Commune'] != comm_selected]
            conn.update(data=df_final); st.rerun()

    st.divider()

    # --- FILTRES ---
    if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 2, 1])
    
    with f_col1: f_prov = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"f_prov_{st.session_state.reset_counter}")
    with f_col2: f_pay = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"f_pay_{st.session_state.reset_counter}")
    with f_col3: f_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"f_serv_{st.session_state.reset_counter}")
    with f_col4:
        st.write("")
        if st.button("❌ Effacer filtres", use_container_width=True):
            st.session_state.reset_counter += 1; st.rerun()

    # --- LOGIQUE FILTRE ---
    df_display = df_gsheets.copy()
    f_list = []
    if f_prov: df_display = df_display[df_display['Province'].isin(f_prov)]; f_list.append(f"Provinces: {', '.join(f_prov)}")
    if f_pay: df_display = df_display[df_display['Paiement'].isin(f_pay)]; f_list.append(f"Paiement: {', '.join(f_pay)}")
    if f_serv:
        for s in f_serv: df_display = df_display[df_display['Services'].str.contains(s, na=False, regex=False)]
        f_list.append(f"Services: {', '.join(f_serv)}")
    
    filters_desc = " | ".join(f_list) if f_list else "Aucun filtre (Liste complète)"

# Remplacer la section "--- BOUTON IMPRIMER ---" par celle-ci :

    # --- BOUTON IMPRIMER (Version Fiable) ---
    if not df_display.empty:
        df_display = df_display.sort_values(by=['Province', 'Commune'])
        print_html = get_print_html(df_display, filters_desc)
        
        st.write("")
        # Utilisation d'un bouton de téléchargement (Download Button)
        # C'est la méthode la plus stable sur tous les navigateurs
        st.download_button(
            label="🖨️ PRÉPARER LE RAPPORT D'IMPRESSION",
            data=print_html,
            file_name="rapport_creos.html",
            mime="text/html",
            use_container_width=True,
            help="Cliquez pour télécharger le fichier, puis ouvrez-le pour imprimer."
        )
        st.info("💡 Une fois le fichier 'rapport_creos.html' téléchargé, ouvrez-le : il s'imprimera automatiquement.")
    
    st.write("")
    st.dataframe(df_display, use_container_width=True, hide_index=True)
