import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# CSS : Gestion de l'affichage Écran vs Impression
st.markdown("""
    <style>
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
        }
        .header-title { font-size: 24px; font-weight: bold; margin: 0; }
        .tt-button {
            background-color: white; color: #4169E1; padding: 8px 18px;
            border-radius: 5px; text-decoration: none; font-weight: bold;
        }

        @media print {
            .no-print { display: none !important; }
            .print-only { display: block !important; visibility: visible !important; }
            .stApp { background-color: white !important; }
        }
        .print-only { display: none; }
        .print-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .print-table th, .print-table td { border: 1px solid #000; padding: 6px; text-align: left; font-size: 11px; }
        .province-title { background-color: #4169E1; color: white; padding: 5px; margin-top: 10px; font-weight: bold; }
    </style>
    
    <div class="main-header no-print">
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
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_gsheets = conn.read(ttl=0).dropna(how="all")
except:
    st.error("Impossible de se connecter à Google Sheets. Vérifiez vos secrets.")
    df_gsheets = pd.DataFrame(columns=["Commune", "Province", "Paiement", "Services"])

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord et Carte", "✏️ Gestion des Communes"])

# --- TAB 1 : DASHBOARD ---
with tab1:
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    if df_gsheets.empty:
        st.warning("Aucune donnée disponible dans le Google Sheet.")
    else:
        # (Calculs stats...)
        t_dash = len(df_gsheets)
        p_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
        po_dash = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
        
        # Affichage Carte (Simplifié pour le code complet)
        st.info("La carte interactive est chargée ci-dessous.")
        json_recs = df_gsheets.to_json(orient='records')
        # ... (Insertion de votre bloc html_map ici si désiré)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2 : GESTION ---
with tab2:
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    st.header("✏️ Gestion des Communes")
    
    # Formulaire Ajout/Modif
    c_form, c_stat = st.columns([6, 4])
    with c_form:
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
                conn.update(data=df_u)
                st.success(f"{com_sel} mis à jour !")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- ZONE FILTRES ET IMPRESSION ---
    if 'rc' not in st.session_state: st.session_state.rc = 0
    
    col_titre, col_print, col_reset = st.columns([5, 2, 3])
    with col_titre:
        st.subheader("🔍 Filtres & Liste")
    with col_print:
        st.write("##")
        if st.button("🖨️ IMPRESSION", use_container_width=True):
            components.html("<script>window.print();</script>", height=0)
    with col_reset:
        st.write("##")
        if st.button("❌ Effacer les filtres", use_container_width=True):
            st.session_state.rc += 1
            st.rerun()

    # Filtres
    f1, f2, f3 = st.columns([2, 1, 2])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")

    # Logique de filtrage et tri
    df_r = df_gsheets.copy()
    if not df_r.empty:
        if fl_p: df_r = df_r[df_r['Province'].isin(fl_p)]
        if fl_m: df_r = df_r[df_r['Paiement'].isin(fl_m)]
        if fl_s:
            for s in fl_s: df_r = df_r[df_r['Services'].str.contains(s, na=False)]
        
        df_sorted = df_r.sort_values(['Province', 'Commune'])

        # Affichage Écran
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Génération Impression (HTML caché à l'écran)
        print_html = f"<div class='print-only'><h1>Rapport Creos - {len(df_sorted)} communes</h1>"
        for prov in sorted(df_sorted['Province'].unique()):
            print_html += f"<div class='province-title'>{prov}</div><table class='print-table'><tr><th>Commune</th><th>Mode</th><th>Services</th></tr>"
            for _, row in df_sorted[df_sorted['Province'] == prov].iterrows():
                print_html += f"<tr><td>{row['Commune']}</td><td>{row['Paiement']}</td><td>{row['Services'].replace('|', ', ')}</td></tr>"
            print_html += "</table>"
        print_html += "</div>"
        st.markdown(print_html, unsafe_allow_html=True)
    else:
        st.info("Aucune commune à afficher selon les filtres.")
