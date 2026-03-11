import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io
import json

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard", initial_sidebar_state="collapsed")

# Suppression de la sidebar car nous utilisons un layout plein écran custom
st.markdown("<style>#MainMenu, header, footer {visibility: hidden;} [data-testid='stSidebar'] {display:none;}</style>", unsafe_allow_html=True)

# --- RÉFÉRENTIEL COULEURS (Inspirées de votre image) ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1",      # Jaune clair top
    "Brabant Wallon": "#A9F1EB", # Cyan top
    "Liège": "#9AE8FF",         # Bleu clair right
    "Hainaut": "#C8B6FF",       # Violet left
    "Namur": "#FFCCB6",         # Corail center
    "Luxembourg": "#FF85F3"      # Magenta bottom-right
}

# --- CHARGEMENT DONNÉES GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE COMPLÈTE DES 281 COMMUNES (Nettoyée) ---
@st.cache_data
def get_full_list():
    # Note: Musson Hainaut a été retiré, Musson Luxembourg maintenu.
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Auderghem", "prov": "Bruxelles"}, {"name": "Berchem-Sainte-Agathe", "prov": "Bruxelles"}, {"name": "Bruxelles", "prov": "Bruxelles"}, {"name": "Etterbeek", "prov": "Bruxelles"}, {"name": "Evere", "prov": "Bruxelles"}, {"name": "Forest", "prov": "Bruxelles"}, {"name": "Ganshoren", "prov": "Bruxelles"}, {"name": "Ixelles", "prov": "Bruxelles"}, {"name": "Jette", "prov": "Bruxelles"}, {"name": "Koekelberg", "prov": "Bruxelles"}, {"name": "Molenbeek-Saint-Jean", "prov": "Bruxelles"}, {"name": "Saint-Gilles", "prov": "Bruxelles"}, {"name": "Saint-Josse-ten-Noode", "prov": "Bruxelles"}, {"name": "Schaerbeek", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"}, {"name": "Watermael-Boitsfort", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Lambert", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Pierre", "prov": "Bruxelles"},
        {"name": "Beauvechain", "prov": "Brabant Wallon"}, {"name": "Braine-l'Alleud", "prov": "Brabant Wallon"}, {"name": "Braine-le-Château", "prov": "Brabant Wallon"}, {"name": "Chastre", "prov": "Brabant Wallon"}, {"name": "Chaumont-Gistoux", "prov": "Brabant Wallon"}, {"name": "Court-Saint-Étienne", "prov": "Brabant Wallon"}, {"name": "Genappe", "prov": "Brabant Wallon"}, {"name": "Grez-Doiceau", "prov": "Brabant Wallon"}, {"name": "Hélécine", "prov": "Brabant Wallon"}, {"name": "Incourt", "prov": "Brabant Wallon"}, {"name": "Ittre", "prov": "Brabant Wallon"}, {"name": "Jodoigne", "prov": "Brabant Wallon"}, {"name": "La Hulpe", "prov": "Brabant Wallon"}, {"name": "Lasne", "prov": "Brabant Wallon"}, {"name": "Mont-Saint-Guibert", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"}, {"name": "Orp-Jauche", "prov": "Brabant Wallon"}, {"name": "Ottignies-Louvain-la-Neuve", "prov": "Brabant Wallon"}, {"name": "Perwez", "prov": "Brabant Wallon"}, {"name": "Ramillies", "prov": "Brabant Wallon"}, {"name": "Rebecq", "prov": "Brabant Wallon"}, {"name": "Rixensart", "prov": "Brabant Wallon"}, {"name": "Tubize", "prov": "Brabant Wallon"}, {"name": "Villers-la-Ville", "prov": "Brabant Wallon"}, {"name": "Walhain", "prov": "Brabant Wallon"}, {"name": "Waterloo", "prov": "Brabant Wallon"}, {"name": "Wavre", "prov": "Brabant Wallon"},
        {"name": "Aiseau-Presles", "prov": "Hainaut"}, {"name": "Anderlues", "prov": "Hainaut"}, {"name": "Antoing", "prov": "Hainaut"}, {"name": "Ath", "prov": "Hainaut"}, {"name": "Beaumont", "prov": "Hainaut"}, {"name": "Belœil", "prov": "Hainaut"}, {"name": "Bernissart", "prov": "Hainaut"}, {"name": "Binche", "prov": "Hainaut"}, {"name": "Boussu", "prov": "Hainaut"}, {"name": "Braine-le-Comte", "prov": "Hainaut"}, {"name": "Brugelette", "prov": "Hainaut"}, {"name": "Brunehaut", "prov": "Hainaut"}, {"name": "Celles", "prov": "Hainaut"}, {"name": "Chapelle-lez-Herlaimont", "prov": "Hainaut"}, {"name": "Charleroi", "prov": "Hainaut"}, {"name": "Châtelet", "prov": "Hainaut"}, {"name": "Chièvres", "prov": "Hainaut"}, {"name": "Chimay", "prov": "Hainaut"}, {"name": "Colfontaine", "prov": "Hainaut"}, {"name": "Comines-Warneton", "prov": "Hainaut"}, {"name": "Courcelles", "prov": "Hainaut"}, {"name": "Dour", "prov": "Hainaut"}, {"name": "Écaussinnes", "prov": "Hainaut"}, {"name": "Ellezelles", "prov": "Hainaut"}, {"name": "Enghien", "prov": "Hainaut"}, {"name": "Erquelinnes", "prov": "Hainaut"}, {"name": "Estaimpuis", "prov": "Hainaut"}, {"name": "Estinnes", "prov": "Hainaut"}, {"name": "Farciennes", "prov": "Hainaut"}, {"name": "Fleurus", "prov": "Hainaut"}, {"name": "Fontaine-l'Évêque", "prov": "Hainaut"}, {"name": "Frameries", "prov": "Hainaut"}, {"name": "Frasnes-lez-Anvaing", "prov": "Hainaut"}, {"name": "Froidchapelle", "prov": "Hainaut"}, {"name": "Gerpinnes", "prov": "Hainaut"}, {"name": "Ham-sur-Heure-Nalinnes", "prov": "Hainaut"}, {"name": "Hensies", "prov": "Hainaut"}, {"name": "Honnelles", "prov": "Hainaut"}, {"name": "Jurbise", "prov": "Hainaut"}, {"name": "La Louvière", "prov": "Hainaut"}, {"name": "Le Rœulx", "prov": "Hainaut"}, {"name": "Lens", "prov": "Hainaut"}, {"name": "Les Bons Villers", "prov": "Hainaut"}, {"name": "Lessines", "prov": "Hainaut"}, {"name": "Leuze-en-Hainaut", "prov": "Hainaut"}, {"name": "Lobbes", "prov": "Hainaut"}, {"name": "Manage", "prov": "Hainaut"}, {"name": "Merbes-le-Château", "prov": "Hainaut"}, {"name": "Momignies", "prov": "Hainaut"}, {"name": "Mons", "prov": "Hainaut"}, {"name": "Mont-de-l'Enclus", "prov": "Hainaut"}, {"name": "Montigny-le-Tilleul", "prov": "Hainaut"}, {"name": "Morlanwelz", "prov": "Hainaut"}, {"name": "Mouscron", "prov": "Hainaut"}, {"name": "Pecq", "prov": "Hainaut"}, {"name": "Péruwelz", "prov": "Hainaut"}, {"name": "Pont-à-Celles", "prov": "Hainaut"}, {"name": "Quaregnon", "prov": "Hainaut"}, {"name": "Quévy", "prov": "Hainaut"}, {"name": "Quiévrain", "prov": "Hainaut"}, {"name": "Rumes", "prov": "Hainaut"}, {"name": "Saint-Ghislain", "prov": "Hainaut"}, {"name": "Seneffe", "prov": "Hainaut"}, {"name": "Silly", "prov": "Hainaut"}, {"name": "Sivry-Rance", "prov": "Hainaut"}, {"name": "Soignies", "prov": "Hainaut"}, {"name": "Thuin", "prov": "Hainaut"}, {"name": "Tournai", "prov": "Hainaut"},
        {"name": "Amay", "prov": "Liège"}, {"name": "Amblève", "prov": "Liège"}, {"name": "Ans", "prov": "Liège"}, {"name": "Anthisnes", "prov": "Liège"}, {"name": "Aubel", "prov": "Liège"}, {"name": "Awans", "prov": "Liège"}, {"name": "Aywaille", "prov": "Liège"}, {"name": "Baelen", "prov": "Liège"}, {"name": "Bassenge", "prov": "Liège"}, {"name": "Berloz", "prov": "Liège"}, {"name": "Beyne-Heusay", "prov": "Liège"}, {"name": "Blegny", "prov": "Liège"}, {"name": "Braives", "prov": "Liège"}, {"name": "Bullange", "prov": "Liège"}, {"name": "Burdinne", "prov": "Liège"}, {"name": "Burg-Reuland", "prov": "Liège"}, {"name": "Bütgenbach", "prov": "Liège"}, {"name": "Chaudfontaine", "prov": "Liège"}, {"name": "Clavier", "prov": "Liège"}, {"name": "Comblain-au-Pont", "prov": "Liège"}, {"name": "Crisnée", "prov": "Liège"}, {"name": "Dalhem", "prov": "Liège"}, {"name": "Dison", "prov": "Liège"}, {"name": "Donceel", "prov": "Liège"}, {"name": "Engis", "prov": "Liège"}, {"name": "Esneux", "prov": "Liège"}, {"name": "Eupen", "prov": "Liège"}, {"name": "Faimes", "prov": "Liège"}, {"name": "Ferrières", "prov": "Liège"}, {"name": "Fexhe-le-Haut-Clocher", "prov": "Liège"}, {"name": "Flémalle", "prov": "Liège"}, {"name": "Fléron", "prov": "Liège"}, {"name": "Geer", "prov": "Liège"}, {"name": "Grâce-Hollogne", "prov": "Liège"}, {"name": "Hamoir", "prov": "Liège"}, {"name": "Hannut", "prov": "Liège"}, {"name": "Héron", "prov": "Liège"}, {"name": "Herstal", "prov": "Liège"}, {"name": "Herve", "prov": "Liège"}, {"name": "Huy", "prov": "Liège"}, {"name": "Jalhay", "prov": "Liège"}, {"name": "Juprelle", "prov": "Liège"}, {"name": "La Calamine", "prov": "Liège"}, {"name": "Liège", "prov": "Liège"}, {"name": "Lierneux", "prov": "Liège"}, {"name": "Limbourg", "prov": "Liège"}, {"name": "Lincent", "prov": "Liège"}, {"name": "Lontzen", "prov": "Liège"}, {"name": "Malmedy", "prov": "Liège"}, {"name": "Marchin", "prov": "Liège"}, {"name": "Modave", "prov": "Liège"}, {"name": "Nandrin", "prov": "Liège"}, {"name": "Neupré", "prov": "Liège"}, {"name": "Olne", "prov": "Liège"}, {"name": "Oreye", "prov": "Liège"}, {"name": "Ouffet", "prov": "Liège"}, {"name": "Oupeye", "prov": "Liège"}, {"name": "Pepinster", "prov": "Liège"}, {"name": "Plombières", "prov": "Liège"}, {"name": "Raeren", "prov": "Liège"}, {"name": "Remicourt", "prov": "Liège"}, {"name": "Saint-Georges-sur-Meuse", "prov": "Liège"}, {"name": "Saint-Nicolas", "prov": "Liège"}, {"name": "Saint-Vith", "prov": "Liège"}, {"name": "Seraing", "prov": "Liège"}, {"name": "Soumagne", "prov": "Liège"}, {"name": "Spa", "prov": "Liège"}, {"name": "Sprimont", "prov": "Liège"}, {"name": "Stavelot", "prov": "Liège"}, {"name": "Stoumont", "prov": "Liège"}, {"name": "Theux", "prov": "Liège"}, {"name": "Thimister-Clermont", "prov": "Liège"}, {"name": "Tinlot", "prov": "Liège"}, {"name": "Trois-Ponts", "prov": "Liège"}, {"name": "Trooz", "prov": "Liège"}, {"name": "Verlaine", "prov": "Liège"}, {"name": "Verviers", "prov": "Liège"}, {"name": "Visé", "prov": "Liège"}, {"name": "Waimes", "prov": "Liège"}, {"name": "Wanze", "prov": "Liège"}, {"name": "Waremme", "prov": "Liège"}, {"name": "Wasseiges", "prov": "Liège"}, {"name": "Welkenraedt", "prov": "Liège"},
        {"name": "Andenne", "prov": "Namur"}, {"name": "Anhée", "prov": "Namur"}, {"name": "Assesse", "prov": "Namur"}, {"name": "Beauraing", "prov": "Namur"}, {"name": "Bièvre", "prov": "Namur"}, {"name": "Cerfontaine", "prov": "Namur"}, {"name": "Ciney", "prov": "Namur"}, {"name": "Couvin", "prov": "Namur"}, {"name": "Dinant", "prov": "Namur"}, {"name": "Doische", "prov": "Namur"}, {"name": "Éghezée", "prov": "Namur"}, {"name": "Fernelmont", "prov": "Namur"}, {"name": "Floreffe", "prov": "Namur"}, {"name": "Florennes", "prov": "Namur"}, {"name": "Fosses-la-Ville", "prov": "Namur"}, {"name": "Gedinne", "prov": "Namur"}, {"name": "Gembloux", "prov": "Namur"}, {"name": "Gesves", "prov": "Namur"}, {"name": "Hamelois", "prov": "Namur"}, {"name": "Hastière", "prov": "Namur"}, {"name": "Havelange", "prov": "Namur"}, {"name": "Houyet", "prov": "Namur"}, {"name": "Jemeppe-sur-Sambre", "prov": "Namur"}, {"name": "La Bruyère", "prov": "Namur"}, {"name": "Mettet", "prov": "Namur"}, {"name": "Namur", "prov": "Namur"}, {"name": "Ohey", "prov": "Namur"}, {"name": "Onhaye", "prov": "Namur"}, {"name": "Philippeville", "prov": "Namur"}, {"name": "Profondeville", "prov": "Namur"}, {"name": "Rochefort", "prov": "Namur"}, {"name": "Sambreville", "prov": "Namur"}, {"name": "Sombreffe", "prov": "Namur"}, {"name": "Somme-Leuze", "prov": "Namur"}, {"name": "Viroinval", "prov": "Namur"}, {"name": "Vresse-sur-Semois", "prov": "Namur"}, {"name": "Walcourt", "prov": "Namur"}, {"name": "Yvoir", "prov": "Namur"},
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Attert", "prov": "Luxembourg"}, {"name": "Aubange", "prov": "Luxembourg"}, {"name": "Bastogne", "prov": "Luxembourg"}, {"name": "Bertogne", "prov": "Luxembourg"}, {"name": "Bertrix", "prov": "Luxembourg"}, {"name": "Bouillon", "prov": "Luxembourg"}, {"name": "Chiny", "prov": "Luxembourg"}, {"name": "Daverdisse", "prov": "Luxembourg"}, {"name": "Durbuy", "prov": "Luxembourg"}, {"name": "Érezée", "prov": "Luxembourg"}, {"name": "Étalle", "prov": "Luxembourg"}, {"name": "Fauvillers", "prov": "Luxembourg"}, {"name": "Florenville", "prov": "Luxembourg"}, {"name": "Gouvy", "prov": "Luxembourg"}, {"name": "Habay", "prov": "Luxembourg"}, {"name": "Herbeumont", "prov": "Luxembourg"}, {"name": "Hotton", "prov": "Luxembourg"}, {"name": "Houffalize", "prov": "Luxembourg"}, {"name": "La Roche-en-Ardenne", "prov": "Luxembourg"}, {"name": "Léglise", "prov": "Luxembourg"}, {"name": "Libin", "prov": "Luxembourg"}, {"name": "Libramont-Chevigny", "prov": "Luxembourg"}, {"name": "Manhay", "prov": "Luxembourg"}, {"name": "Marche-en-Famenne", "prov": "Luxembourg"}, {"name": "Martelange", "prov": "Luxembourg"}, {"name": "Meix-devant-Virton", "prov": "Luxembourg"}, {"name": "Messancy", "prov": "Luxembourg"}, {"name": "Musson", "prov": "Luxembourg"}, {"name": "Nassogne", "prov": "Luxembourg"}, {"name": "Neufchâteau", "prov": "Luxembourg"}, {"name": "Paliseul", "prov": "Luxembourg"}, {"name": "Rendeux", "prov": "Luxembourg"}, {"name": "Rouvroy", "prov": "Luxembourg"}, {"name": "Sainte-Ode", "prov": "Luxembourg"}, {"name": "Saint-Hubert", "prov": "Luxembourg"}, {"name": "Saint-Léger", "prov": "Luxembourg"}, {"name": "Tellin", "prov": "Luxembourg"}, {"name": "Tenneville", "prov": "Luxembourg"}, {"name": "Tintigny", "prov": "Luxembourg"}, {"name": "Vaux-sur-Sûre", "prov": "Luxembourg"}, {"name": "Vielsalm", "prov": "Luxembourg"}, {"name": "Virton", "prov": "Luxembourg"}, {"name": "Wellin", "prov": "Luxembourg"}
    ]

all_communes = get_full_list()

# --- INITIALISATION SESSION STATE ---
if 'selected_commune_data' not in st.session_state:
    st.session_state.selected_commune_data = None

# --- GENERATION DU HTML POUR LA MOSAÏQUE (CSS Custom) ---
def generate_mosaic_html(communes_list, db_dataframe):
    # Dictionnaire pour regrouper les communes par province
    provinces_groups = {}
    for c in communes_list:
        if c['prov'] not in provinces_groups:
            provinces_groups[c['prov']] = []
        provinces_groups[c['prov']].append(c['name'])

    # Construction du CSS dynamique pour positionner les mosaïques
    # Inspiré par image_0.png
    css = """
    <style>
        .map-container {
            position: relative;
            width: 1000px;
            height: 700px;
            margin: 0 auto;
            border: 1px solid #eee;
            background-color: white;
            border-radius: 8px;
        }
        .province-group {
            position: absolute;
            display: grid;
            gap: 2px;
        }
        .tile {
            width: 15px;
            height: 15px;
            border-radius: 3px;
            cursor: pointer;
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.1s, border-color 0.1s;
        }
        .tile:hover {
            transform: scale(1.3);
            border-color: black !important;
            z-index: 10;
        }
        /* Positionnements spécifiques (adaptés de l'image) */
        #prov-Bruxelles { top: 30px; left: 45%; grid-template-columns: repeat(7, 1fr); }
        #prov-BW { top: 120px; left: 45%; grid-template-columns: repeat(7, 1fr); }
        #prov-Hainaut { top: 250px; left: 50px; grid-template-columns: repeat(7, 1fr); }
        #prov-Liege { top: 100px; right: 50px; grid-template-columns: repeat(7, 1fr); }
        #prov-Namur { top: 400px; left: 350px; grid-template-columns: repeat(7, 1fr); }
        #prov-Luxembourg { bottom: 30px; right: 100px; grid-template-columns: repeat(7, 1fr); }
    </style>
    """

    html = '<div class="map-container">'
    
    # Génération des tuiles
    for prov, com_names in provinces_groups.items():
        prov_id = f"prov-{prov.replace(' ', '')}"
        html += f'<div class="province-group" id="{prov_id}">'
        for com_name in com_names:
            # Sécurité : la clé pour le JavaScript
            safe_id = f"{com_name.replace(' ', '_')}"
            
            # Couleur pleine de la province (comme demandé)
            color = PROV_COLORS.get(prov, "#EEE")
            
            # Capture du clic via JavaScript : on envoie les données à un input caché Streamlit
            click_js = f"window.parent.postMessage({{type: 'streamlit:set_widget_value', id: 'com_selection_input', value: {{'name': '{com_name}', 'prov': '{prov}'}}}}, '*');"
            
            html += f'<div class="tile" style="background-color: {color};" onclick="{click_js}" title="{com_name} ({prov})"></div>'
        html += '</div>'
    
    html += '</div>'
    
    # Ajout d'un input caché que le JavaScript peut manipuler
    st.components.v1.html(css + html, height=710)

# --- LAYOUT PRINCIPAL (Custom) ---
col_map, col_details = st.columns([0.7, 0.3])

with col_map:
    # --- BARRE DE RECHERCHE ---
    search_query = st.text_input("🔍 Recherche rapide...", placeholder="Ex: Oreye").strip().lower()

    # --- AFFICHAGE DE LA MOSAÏQUE GÉOGRAPHIQUE ---
    st.subheader("🗺️ Carte Interactive (Cliquez sur une tuile)")
    
    # On filtre la liste si recherche
    filtered_communes = all_communes
    if search_query:
        filtered_communes = [c for c in all_communes if search_query in c['name'].lower()]

    generate_mosaic_html(filtered_communes, df_db)

    # --- LÉGENDE ---
    with st.expander("🔑 Légende des provinces", expanded=False):
        cols_leg = st.columns(3)
        for i, (p, c) in enumerate(PROV_COLORS.items()):
            cols_leg[i % 3].markdown(f"<span style='color:{c}; font-size:20px;'>■</span> {p}", unsafe_allow_html=True)

# --- CAPTURE DE LA SÉLECTION VIA JAVASCRIPT ---
# C'est ici que l'input caché est défini et lu par Streamlit
selection_data = st.components.v1.html("""
<script>
    // Ecouter les messages envoyés par la mosaïque HTML
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit:set_widget_value' && event.data.id === 'com_selection_input') {
            // Pas besoin d'action ici, Streamlit le capture automatiquement via l'id
        }
    });
</script>
<input type="hidden" id="com_selection_input" style="display:none;">
""", height=0)

# Hack Streamlit : on force la lecture de l'input caché après son rendu
# st.session_state.com_selection_input est alimenté par le JS
if 'com_selection_input' in st.session_state and st.session_state.com_selection_input:
    st.session_state.selected_commune_data = st.session_state.com_selection_input

with col_details:
    st.header("📋 Fiche d'Encodage")
    st.divider()

    target_data = st.session_state.selected_commune_data
    
    if target_data:
        com_name = target_data['name']
        com_prov = target_data['prov']
        
        existing = df_db[df_db['Commune'] == com_name]
        
        with st.container(border=True):
            st.title(f"📍 {com_name}")
            st.caption(f"Province : {com_prov}")
            
            with st.form("edit_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                
                # Valeurs par défaut si déjà encodé
                curr_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                curr_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_pay = st.radio("Système de Paiement", ["Pre", "Post"], index=0 if curr_pay == "Pre" else 1, horizontal=True)
                
                with c2:
                    new_serv = st.multiselect("Services Activés", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=curr_serv)

                st.divider()
                
                if st.form_submit_button("✅ ENREGISTRER L'ENCODAGE", use_container_width=True):
                    # Mise à jour de la Google Sheet
                    new_row = pd.DataFrame([[com_name, com_prov, new_pay, "|".join(new_serv)]], 
                                         columns=["Commune", "Province", "Paiement", "Services"])
                    
                    df_final = pd.concat([df_db[df_db['Commune'] != com_name], new_row], ignore_index=True)
                    conn.update(data=df_final)
                    
                    st.success(f"Synchronisation réussie pour {com_name} !")
                    st.session_state.selected_commune_data = None # On ferme la fiche
                    st.rerun()
    else:
        st.info("Sélectionnez une commune sur la carte à gauche pour l'éditer.")

    # --- STATS GLOBALES EN BAS DE FORMULAIRE ---
    st.divider()
    st.subheader("📊 Avancement Global")
    total_traitées = len(df_db)
    col1, col2 = st.columns(2)
    col1.metric("Communes", f"{total_traitées} / 281")
    col2.progress(total_traitées / 281)
