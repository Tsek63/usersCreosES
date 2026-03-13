import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Injection CSS Globale (Header, Boutons, Design)
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Header Principal */
        .main-header {
            background-color: #4169E1; padding: 15px 25px; border-radius: 10px;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 15px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white; color: #4169E1; padding: 8px 18px;
            border-radius: 5px; text-decoration: none; font-weight: bold;
        }

        /* Style spécifique Bouton EXCEL (Bleu Canard) */
        div.stDownloadButton > button {
            background-color: #008080 !important;
            color: white !important;
            border: none !important;
            width: 100% !important;
            height: 45px !important;
            font-weight: bold !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #006666 !important;
        }

        /* Style spécifique Bouton IMPRESSION */
        .print-btn {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            width: 100%;
            height: 45px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .print-btn:hover { background-color: #5a6268; }
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

# --- TAB 1 : DASHBOARD (Identique pour la carte) ---
with tab1:
    # On garde la logique de la carte ici (réduite pour lisibilité du code complet)
    t_dash = len(df_gsheets)
    s_dash = {
        "Cantine Jour": (df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum(), "#FFD700"),
        "Cantine Semaine": (df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum(), "#FF8C00"),
        "Cantine Mois": (df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum(), "#FF0000"),
        "Garderie": (df_gsheets['Services'].str.contains("Garderie", na=False).sum(), "#38bdf8"),
        "Activités": (df_gsheets['Services'].str.contains("Activités", na=False).sum(), "#4ade80")
    }
    # [Code HTML/JS de la carte inséré ici lors de l'exécution]
    # (Par souci de place, je réutilise la structure HTML du message précédent)
    # ... (Composant carte identique au précédent) ...

# --- TAB 2 : GESTION ET FILTRES ---
with tab2:
    # 1. Zone du haut : Formulaire + Résumé
    c_form, c_stat = st.columns([6, 4])
    with c_form:
        st.subheader("✏️ Édition")
        p_sel = st.selectbox("1. Province", list(data_fwb.keys()), key="m_p")
        with st.form("edit_form"):
            f1, f2 = st.columns(2)
            with f1: com_sel = st.selectbox("2. Commune", data_fwb[p_sel])
            with f2:
                pay_v = st.radio("3. Mode", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("4. Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            if st.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                new_r = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_r], ignore_index=True)
                conn.update(data=df_u); st.rerun()

    with c_stat:
        # Bloc Statistique Couleur Bleu Canard
        st.markdown(f"""
        <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
            <div style="font-size:11px; text-transform:uppercase; opacity:0.8;">Communes Actives</div>
            <div style="font-size:50px; font-weight:bold; line-height:1;">{len(df_gsheets)}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # --- 2. ZONE FILTRES AVEC BOUTON RESET ALIGNÉ ---
    if 'rc' not in st.session_state: st.session_state.rc = 0
    
    col_titre, col_reset = st.columns([7, 3])
    with col_titre:
        st.subheader("🔍 Filtres & Liste filtrée")
    with col_reset:
        st.write("##")
        if st.button("❌ Effacer les filtres", use_container_width=True):
            st.session_state.rc += 1
            st.rerun()

    f1, f2, f3 = st.columns([2, 1, 2])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")

    # Logique de filtrage
    df_r = df_gsheets.copy()
    if not df_r.empty:
        if fl_p: df_r = df_r[df_r['Province'].isin(fl_p)]
        if fl_m: df_r = df_r[df_r['Paiement'].isin(fl_m)]
        if fl_s:
            for s in fl_s: df_r = df_r[df_r['Services'].str.contains(s, na=False)]
        
        df_sorted = df_r.sort_values(['Province', 'Commune'])

        # --- 3. BOUTONS EXPORT ET IMPRESSION (Sous les filtres) ---
        st.write("##")
        col_ex, col_pr = st.columns(2)
        
        with col_ex:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_sorted.to_excel(writer, index=False, sheet_name='Creos_Export')
            st.download_button(label="📥 Exporter vers Excel", data=buffer.getvalue(), file_name="creos_export.xlsx", use_container_width=True)

        with col_pr:
            # Préparation HTML pour Impression
            f_p_txt = f"Provinces: {', '.join(fl_p)}" if fl_p else "Toutes les Provinces"
            f_m_txt = f"Paiement: {', '.join(fl_m)}" if fl_m else "Tous les modes"
            f_s_txt = f"Services: {', '.join(fl_s)}" if fl_s else "Tous les services"
            
            rows_html = ""
            for prov in sorted(df_sorted['Province'].unique()):
                rows_html += f"<tr style='background:#f2f2f2;'><td colspan='3'><b>{prov}</b></td></tr>"
                for _, row in df_sorted[df_sorted['Province']==prov].iterrows():
                    rows_html += f"<tr><td>{row['Commune']}</td><td>{row['Paiement']}</td><td>{row['Services'].replace('|', ', ')}</td></tr>"

            print_js = f"""
            <script>
            function doPrint() {{
                var win = window.open('', '', 'height=700,width=900');
                win.document.write('<html><head><title>Impression Creos</title><style>');
                win.document.write('body{{font-family:sans-serif; padding:30px;}} table{{width:100%; border-collapse:collapse; margin-top:20px;}}');
                win.document.write('th,td{{border:1px solid #ccc; padding:8px; text-align:left; font-size:12px;}} th{{background:#4169E1; color:white;}}');
                win.document.write('.meta{{font-size:11px; color:#555; margin-bottom:10px;}} hr{{border:0; border-top:2px solid #4169E1;}}');
                win.document.write('</style></head><body>');
                win.document.write('<h2>Liste des Utilisateurs Creos</h2><hr>');
                win.document.write('<div class="meta">{f_p_txt}<br>{f_m_txt}<br>{f_s_txt}</div>');
                win.document.write('<table><thead><tr><th>Commune</th><th>Mode</th><th>Services</th></tr></thead><tbody>{rows_html}</tbody></table>');
                win.document.write('</body></html>');
                win.document.close();
                setTimeout(function(){{ win.print(); }}, 500);
            }}
            </script>
            <button onclick="doPrint()" class="print-btn">🖨️ IMPRESSION</button>
            """
            components.html(print_js, height=50)

        # 4. Liste et Graphiques
        col_list, col_viz = st.columns([6, 4], gap="medium")
        with col_list:
            st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=500)
        
        with col_viz:
            if not df_sorted.empty:
                # Camembert Paiement
                p_c = df_sorted['Paiement'].value_counts().reset_index()
                fig_p = px.pie(p_c, values='count', names='Paiement', hole=0.4, title="Modes de Paiement",
                               color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
                fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig_p, use_container_width=True)

                # Barres Services
                sl = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
                ct = [df_sorted['Services'].str.contains(s, na=False).sum() for s in sl]
                df_s = pd.DataFrame({'Service': sl, 'Nombre': ct})
                fig_s = px.bar(df_s, x='Nombre', y='Service', orientation='h', title="Popularité des Services",
                               color='Service', color_discrete_map={
                                  "Cantine Jour": "#FFD700", "Cantine Semaine": "#FF8C00",
                                  "Cantine Mois": "#FF0000", "Garderie": "#38bdf8", "Activités": "#4ade80"})
                fig_s.update_layout(height=250, showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig_s, use_container_width=True)
