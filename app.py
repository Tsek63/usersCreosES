import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Couleurs de référence pour la cohérence visuelle
COLORS = {
    "Cantine Jour": "#fb923c",
    "Cantine Semaine": "#f59e0b",
    "Cantine Mois": "#d97706",
    "Garderie": "#38bdf8",
    "Activités": "#4ade80",
    "Prépaiement": "#fb923c",
    "Post-paiement": "#38bdf8",
    "Bleu-Creos": "#4169E1"
}

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
        /* Style pour le bloc statistique */
        .stats-container {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
        }}
        .stat-badge {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
        }}
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" class="tt-button">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. CONNEXION & DONNÉES ---
# (Reprise de votre dictionnaire data_fwb existant ici...)
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

# --- 3. RAPPORT HTML (Version Améliorée) ---
def get_print_html(df, filters_desc):
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; padding: 40px; color: #1e3a8a; }}
            h1 {{ color: {COLORS['Bleu-Creos']}; border-bottom: 2px solid {COLORS['Bleu-Creos']}; padding-bottom: 10px; }}
            .filters {{ background: #f1f5f9; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 0.9em; }}
            .province-title {{ background: {COLORS['Bleu-Creos']}; color: white; padding: 8px 15px; border-radius: 5px; margin-top: 25px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #bfdbfe; padding: 10px; text-align: left; }}
            th {{ background: #eff6ff; font-size: 0.8em; }}
            .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: white; margin-right: 4px; font-weight: bold; }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>Utilisateurs de Creos Extrascolaire</h1>
        <div class="filters"><strong>Filtres :</strong> {filters_desc}</div>
    """
    for p in sorted(df['Province'].unique()):
        html += f"<h3 class='province-title'>{p}</h3><table><thead><tr><th>Commune</th><th>Paiement</th><th>Services</th></tr></thead><tbody>"
        for _, row in df[df['Province'] == p].sort_values('Commune').iterrows():
            servs = row['Services'].split('|') if row['Services'] else []
            s_html = "".join([f'<span class="badge" style="background:{COLORS.get(s, "#ccc")};">{s}</span>' for s in servs if s])
            html += f"<tr><td><strong>{row['Commune']}</strong></td><td>{row['Paiement']}</td><td>{s_html}</td></tr>"
        html += "</tbody></table>"
    return html + "</body></html>"

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Dashboard & Carte", "✏️ Gestion des Communes"])

with tab1:
    # (Composant Carte identique au précédent)
    json_records = df_gsheets.to_json(orient='records')
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --c-bruxelles: #ffeaa7; --c-brabant: #81ecec; --c-hainaut: #a29bfe; --c-liege: #74b9ff; --c-namur: #fab1a0; --c-luxembourg: #FF43D0; }}
        body {{ margin: 0; font-family: sans-serif; display: flex; height: 100vh; overflow: hidden; }}
        #left {{ flex: 4; padding: 10px; }} #right {{ flex: 6; padding: 10px; overflow-y: auto; border-left: 1px solid #eee; }}
        svg {{ width: 100%; height: 400px; border: 1px solid #eee; border-radius: 8px; }}
        .item-row {{ display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 13px; align-items: center; }}
        .badge {{ padding: 2px 6px; border-radius: 4px; color: white; font-size: 9px; font-weight: bold; margin-left: 2px; }}
        .prov-label {{ background: #f8fafc; padding: 6px 10px; font-weight: bold; font-size: 11px; color: #64748b; text-transform: uppercase; }}
    </style></head>
    <body onload="init()">
        <div id="left"><svg id="svg" viewBox="0 0 900 650"></svg></div>
        <div id="right"><input type="text" id="search" placeholder="🔍 Rechercher..." style="width:100%; padding:10px; margin-bottom:10px;" onkeyup="doSearch()"><div id="list"></div></div>
        <script>
            const dbData = {json_records}; const mapRef = {json.dumps(data_fwb)};
            let db = new Map(); dbData.forEach(r => db.set(r.Commune, r));
            const icons = {{ "Cantine Jour": "#fb923c", "Cantine Semaine": "#f59e0b", "Cantine Mois": "#d97706", "Garderie": "#38bdf8", "Activités": "#4ade80" }};
            function init() {{
                const svg = document.getElementById('svg');
                const anchors = {{ "Bruxelles": [330, 30], "Brabant Wallon": [330, 100], "Hainaut": [40, 180], "Liège": [560, 60], "Namur": [280, 300], "Luxembourg": [530, 400] }};
                Object.entries(mapRef).forEach(([p, list]) => {{
                    const cleanP = p.toLowerCase().split(' ')[0];
                    list.forEach((n, i) => {{
                        const x = anchors[p][0] + (i % 8 * 23), y = anchors[p][1] + (Math.floor(i / 8) * 21);
                        const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                        r.setAttribute("x", x); r.setAttribute("y", y); r.setAttribute("width", 20); r.setAttribute("height", 18); r.setAttribute("rx", 3);
                        r.style.fill = db.has(n) ? `var(--c-${{cleanP}})` : "#eee";
                        r.style.stroke = db.has(n) ? "#333" : "#ddd";
                        const t = document.createElementNS("http://www.w3.org/2000/svg", "title"); t.textContent = n;
                        r.appendChild(t); svg.appendChild(r);
                    }});
                }});
                render();
            }}
            function render() {{
                const listDiv = document.getElementById('list');
                ["Bruxelles", "Brabant Wallon", "Hainaut", "Liège", "Namur", "Luxembourg"].forEach(p => {{
                    const filtered = Array.from(db.values()).filter(x => x.Province === p).sort((a,b) => a.Commune.localeCompare(b.Commune));
                    if(filtered.length > 0) {{
                        const h = document.createElement('div'); h.className = 'prov-label'; h.innerText = p; listDiv.appendChild(h);
                        filtered.forEach(x => {{ const row = document.createElement('div'); row.className = 'item-row';
                            const b = (x.Services || "").split('|').filter(s => s).map(s => `<span class="badge" style="background:${{icons[s]}}">${{s}}</span>`).join('');
                            row.innerHTML = `<span><b>${{x.Commune}}</b></span><div>${{b}}</div>`;
                            listDiv.appendChild(row);
                        }});
                    }}
                }});
            }}
            function doSearch() {{ const v = document.getElementById('search').value.toLowerCase(); document.querySelectorAll('.item-row').forEach(r => r.style.display = r.innerText.toLowerCase().includes(v) ? 'flex' : 'none'); }}
        </script>
    </body></html>
    """
    components.html(html_code, height=600)

with tab2:
    # --- LOGIQUE STATS ---
    total_com = len(df_gsheets)
    pre_count = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    post_count = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    serv_counts = {s: df_gsheets['Services'].str.contains(s, na=False).sum() for s in ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]}

    col_form, col_stats = st.columns([1.5, 1])

    with col_form:
        st.subheader("✏️ Gestion des données")
        prov_selected = st.selectbox("1. Province", list(data_fwb.keys()))
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1: comm_selected = st.selectbox("2. Commune", data_fwb[prov_selected])
            with c2: 
                pay_val = st.radio("3. Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_val = st.multiselect("4. Services", list(serv_counts.keys()))
            
            save_c, del_c = st.columns(2)
            if save_c.form_submit_button("💾 ENREGISTRER", use_container_width=True):
                new_row = pd.DataFrame([{"Commune": comm_selected, "Province": prov_selected, "Paiement": pay_val, "Services": "|".join(serv_val)}])
                df_final = pd.concat([df_gsheets[df_gsheets['Commune'] != comm_selected], new_row], ignore_index=True)
                conn.update(data=df_final); st.rerun()
            if del_c.form_submit_button("🗑️ SUPPRIMER", use_container_width=True):
                df_final = df_gsheets[df_gsheets['Commune'] != comm_selected]
                conn.update(data=df_final); st.rerun()

    with col_stats:
        st.markdown(f"""
            <div class="stats-container">
                <div style="font-size: 0.8em; color: #64748b; text-transform: uppercase;">Total des communes actives</div>
                <div style="font-size: 2.5em; font-weight: bold; color: {COLORS['Bleu-Creos']}; margin-bottom: 20px;">{total_com}</div>
                
                <div style="display: flex; gap: 40px;">
                    <div>
                        <div style="font-size: 0.7em; font-weight: bold; margin-bottom: 10px;">MODE DE PAIEMENT</div>
                        <div style="font-size: 0.9em; margin-bottom: 5px;"><span class="stat-badge" style="background:{COLORS['Prépaiement']}"></span>Prépaiement : <b>{pre_count}</b></div>
                        <div style="font-size: 0.9em;"><span class="stat-badge" style="background:{COLORS['Post-paiement']}"></span>Post-paiement : <b>{post_count}</b></div>
                    </div>
                    <div>
                        <div style="font-size: 0.7em; font-weight: bold; margin-bottom: 10px;">SERVICES ACTIFS</div>
                        {"".join([f'<div style="font-size: 0.9em; margin-bottom: 3px;"><span class="stat-badge" style="background:{COLORS[s]}"></span>{s} : <b>{count}</b></div>' for s, count in serv_counts.items()])}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # --- FILTRES & TABLEAU ---
    st.subheader("🔍 Liste & Impression")
    if 'reset_counter' not in st.session_state: st.session_state.reset_counter = 0
    f1, f2, f3, f4 = st.columns([2, 1, 2, 1])
    with f1: f_prov = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p{st.session_state.reset_counter}")
    with f2: f_pay = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"y{st.session_state.reset_counter}")
    with f3: f_serv = st.multiselect("Services", list(serv_counts.keys()), key=f"s{st.session_state.reset_counter}")
    with f4: 
        st.write("")
        if st.button("❌ Reset", use_container_width=True): st.session_state.reset_counter += 1; st.rerun()

    df_display = df_gsheets.copy()
    f_txt = []
    if f_prov: df_display = df_display[df_display['Province'].isin(f_prov)]; f_txt.append(f"Provinces: {', '.join(f_prov)}")
    if f_pay: df_display = df_display[df_display['Paiement'].isin(f_pay)]; f_txt.append(f"Paiement: {', '.join(f_pay)}")
    if f_serv:
        for s in f_serv: df_display = df_display[df_display['Services'].str.contains(s, na=False)]
        f_txt.append(f"Services: {', '.join(f_serv)}")

    if not df_display.empty:
        df_display = df_display.sort_values(by=['Province', 'Commune'])
        st.download_button("🖨️ GÉNÉRER LE RAPPORT D'IMPRESSION COLORÉ", data=get_print_html(df_display, " | ".join(f_txt) if f_txt else "Toutes les communes"), file_name="rapport_creos.html", mime="text/html", use_container_width=True)

    st.dataframe(df_display, use_container_width=True, hide_index=True)
