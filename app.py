import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- COULEURS PASTEL (Comme votre image) ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1",      # Jaune
    "Brabant Wallon": "#A9F1EB", # Cyan
    "Hainaut": "#C8B6FF",       # Violet
    "Liège": "#9AE8FF",         # Bleu
    "Namur": "#FFCCB6",         # Corail
    "Luxembourg": "#FF85F3"      # Rose
}

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE COMPLÈTE DES 281 COMMUNES ---
@st.cache_data
def get_full_list():
    return [
        # BRUXELLES (19)
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Auderghem", "prov": "Bruxelles"}, {"name": "Berchem-Sainte-Agathe", "prov": "Bruxelles"}, {"name": "Bruxelles", "prov": "Bruxelles"}, {"name": "Etterbeek", "prov": "Bruxelles"}, {"name": "Evere", "prov": "Bruxelles"}, {"name": "Forest", "prov": "Bruxelles"}, {"name": "Ganshoren", "prov": "Bruxelles"}, {"name": "Ixelles", "prov": "Bruxelles"}, {"name": "Jette", "prov": "Bruxelles"}, {"name": "Koekelberg", "prov": "Bruxelles"}, {"name": "Molenbeek-Saint-Jean", "prov": "Bruxelles"}, {"name": "Saint-Gilles", "prov": "Bruxelles"}, {"name": "Saint-Josse-ten-Noode", "prov": "Bruxelles"}, {"name": "Schaerbeek", "prov": "Bruxelles"}, {"name": "Uccle", "prov": "Bruxelles"}, {"name": "Watermael-Boitsfort", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Lambert", "prov": "Bruxelles"}, {"name": "Woluwe-Saint-Pierre", "prov": "Bruxelles"},
        # BRABANT WALLON (27)
        {"name": "Beauvechain", "prov": "Brabant Wallon"}, {"name": "Braine-l'Alleud", "prov": "Brabant Wallon"}, {"name": "Braine-le-Château", "prov": "Brabant Wallon"}, {"name": "Chastre", "prov": "Brabant Wallon"}, {"name": "Chaumont-Gistoux", "prov": "Brabant Wallon"}, {"name": "Court-Saint-Étienne", "prov": "Brabant Wallon"}, {"name": "Genappe", "prov": "Brabant Wallon"}, {"name": "Grez-Doiceau", "prov": "Brabant Wallon"}, {"name": "Hélécine", "prov": "Brabant Wallon"}, {"name": "Incourt", "prov": "Brabant Wallon"}, {"name": "Ittre", "prov": "Brabant Wallon"}, {"name": "Jodoigne", "prov": "Brabant Wallon"}, {"name": "La Hulpe", "prov": "Brabant Wallon"}, {"name": "Lasne", "prov": "Brabant Wallon"}, {"name": "Mont-Saint-Guibert", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"}, {"name": "Orp-Jauche", "prov": "Brabant Wallon"}, {"name": "Ottignies-Louvain-la-Neuve", "prov": "Brabant Wallon"}, {"name": "Perwez", "prov": "Brabant Wallon"}, {"name": "Ramillies", "prov": "Brabant Wallon"}, {"name": "Rebecq", "prov": "Brabant Wallon"}, {"name": "Rixensart", "prov": "Brabant Wallon"}, {"name": "Tubize", "prov": "Brabant Wallon"}, {"name": "Villers-la-Ville", "prov": "Brabant Wallon"}, {"name": "Walhain", "prov": "Brabant Wallon"}, {"name": "Waterloo", "prov": "Brabant Wallon"}, {"name": "Wavre", "prov": "Brabant Wallon"},
        # HAINAUT (69)
        {"name": "Aiseau-Presles", "prov": "Hainaut"}, {"name": "Anderlues", "prov": "Hainaut"}, {"name": "Antoing", "prov": "Hainaut"}, {"name": "Ath", "prov": "Hainaut"}, {"name": "Beaumont", "prov": "Hainaut"}, {"name": "Belœil", "prov": "Hainaut"}, {"name": "Bernissart", "prov": "Hainaut"}, {"name": "Binche", "prov": "Hainaut"}, {"name": "Boussu", "prov": "Hainaut"}, {"name": "Braine-le-Comte", "prov": "Hainaut"}, {"name": "Brugelette", "prov": "Hainaut"}, {"name": "Brunehaut", "prov": "Hainaut"}, {"name": "Celles", "prov": "Hainaut"}, {"name": "Chapelle-lez-Herlaimont", "prov": "Hainaut"}, {"name": "Charleroi", "prov": "Hainaut"}, {"name": "Châtelet", "prov": "Hainaut"}, {"name": "Chièvres", "prov": "Hainaut"}, {"name": "Chimay", "prov": "Hainaut"}, {"name": "Colfontaine", "prov": "Hainaut"}, {"name": "Comines-Warneton", "prov": "Hainaut"}, {"name": "Courcelles", "prov": "Hainaut"}, {"name": "Dour", "prov": "Hainaut"}, {"name": "Écaussinnes", "prov": "Hainaut"}, {"name": "Ellezelles", "prov": "Hainaut"}, {"name": "Enghien", "prov": "Hainaut"}, {"name": "Erquelinnes", "prov": "Hainaut"}, {"name": "Estaimpuis", "prov": "Hainaut"}, {"name": "Estinnes", "prov": "Hainaut"}, {"name": "Farciennes", "prov": "Hainaut"}, {"name": "Fleurus", "prov": "Hainaut"}, {"name": "Fontaine-l'Évêque", "prov": "Hainaut"}, {"name": "Frameries", "prov": "Hainaut"}, {"name": "Frasnes-lez-Anvaing", "prov": "Hainaut"}, {"name": "Froidchapelle", "prov": "Hainaut"}, {"name": "Gerpinnes", "prov": "Hainaut"}, {"name": "Ham-sur-Heure-Nalinnes", "prov": "Hainaut"}, {"name": "Hensies", "prov": "Hainaut"}, {"name": "Honnelles", "prov": "Hainaut"}, {"name": "Jurbise", "prov": "Hainaut"}, {"name": "La Louvière", "prov": "Hainaut"}, {"name": "Le Rœulx", "prov": "Hainaut"}, {"name": "Lens", "prov": "Hainaut"}, {"name": "Les Bons Villers", "prov": "Hainaut"}, {"name": "Lessines", "prov": "Hainaut"}, {"name": "Leuze-en-Hainaut", "prov": "Hainaut"}, {"name": "Lobbes", "prov": "Hainaut"}, {"name": "Manage", "prov": "Hainaut"}, {"name": "Merbes-le-Château", "prov": "Hainaut"}, {"name": "Momignies", "prov": "Hainaut"}, {"name": "Mons", "prov": "Hainaut"}, {"name": "Mont-de-l'Enclus", "prov": "Hainaut"}, {"name": "Montigny-le-Tilleul", "prov": "Hainaut"}, {"name": "Morlanwelz", "prov": "Hainaut"}, {"name": "Mouscron", "prov": "Hainaut"}, {"name": "Pecq", "prov": "Hainaut"}, {"name": "Péruwelz", "prov": "Hainaut"}, {"name": "Pont-à-Celles", "prov": "Hainaut"}, {"name": "Quaregnon", "prov": "Hainaut"}, {"name": "Quévy", "prov": "Hainaut"}, {"name": "Quiévrain", "prov": "Hainaut"}, {"name": "Rumes", "prov": "Hainaut"}, {"name": "Saint-Ghislain", "prov": "Hainaut"}, {"name": "Seneffe", "prov": "Hainaut"}, {"name": "Silly", "prov": "Hainaut"}, {"name": "Sivry-Rance", "prov": "Hainaut"}, {"name": "Soignies", "prov": "Hainaut"}, {"name": "Thuin", "prov": "Hainaut"}, {"name": "Tournai", "prov": "Hainaut"},
        # LIÈGE (84)
        {"name": "Amay", "prov": "Liège"}, {"name": "Amblève", "prov": "Liège"}, {"name": "Ans", "prov": "Liège"}, {"name": "Anthisnes", "prov": "Liège"}, {"name": "Aubel", "prov": "Liège"}, {"name": "Awans", "prov": "Liège"}, {"name": "Aywaille", "prov": "Liège"}, {"name": "Baelen", "prov": "Liège"}, {"name": "Bassenge", "prov": "Liège"}, {"name": "Berloz", "prov": "Liège"}, {"name": "Beyne-Heusay", "prov": "Liège"}, {"name": "Blegny", "prov": "Liège"}, {"name": "Braives", "prov": "Liège"}, {"name": "Bullange", "prov": "Liège"}, {"name": "Burdinne", "prov": "Liège"}, {"name": "Burg-Reuland", "prov": "Liège"}, {"name": "Bütgenbach", "prov": "Liège"}, {"name": "Chaudfontaine", "prov": "Liège"}, {"name": "Clavier", "prov": "Liège"}, {"name": "Comblain-au-Pont", "prov": "Liège"}, {"name": "Crisnée", "prov": "Liège"}, {"name": "Dalhem", "prov": "Liège"}, {"name": "Dison", "prov": "Liège"}, {"name": "Donceel", "prov": "Liège"}, {"name": "Engis", "prov": "Liège"}, {"name": "Esneux", "prov": "Liège"}, {"name": "Eupen", "prov": "Liège"}, {"name": "Faimes", "prov": "Liège"}, {"name": "Ferrières", "prov": "Liège"}, {"name": "Fexhe-le-Haut-Clocher", "prov": "Liège"}, {"name": "Flémalle", "prov": "Liège"}, {"name": "Fléron", "prov": "Liège"}, {"name": "Geer", "prov": "Liège"}, {"name": "Grâce-Hollogne", "prov": "Liège"}, {"name": "Hamoir", "prov": "Liège"}, {"name": "Hannut", "prov": "Liège"}, {"name": "Héron", "prov": "Liège"}, {"name": "Herstal", "prov": "Liège"}, {"name": "Herve", "prov": "Liège"}, {"name": "Huy", "prov": "Liège"}, {"name": "Jalhay", "prov": "Liège"}, {"name": "Juprelle", "prov": "Liège"}, {"name": "La Calamine", "prov": "Liège"}, {"name": "Liège", "prov": "Liège"}, {"name": "Lierneux", "prov": "Liège"}, {"name": "Limbourg", "prov": "Liège"}, {"name": "Lincent", "prov": "Liège"}, {"name": "Lontzen", "prov": "Liège"}, {"name": "Malmedy", "prov": "Liège"}, {"name": "Marchin", "prov": "Liège"}, {"name": "Modave", "prov": "Liège"}, {"name": "Nandrin", "prov": "Liège"}, {"name": "Neupré", "prov": "Liège"}, {"name": "Olne", "prov": "Liège"}, {"name": "Oreye", "prov": "Liège"}, {"name": "Ouffet", "prov": "Liège"}, {"name": "Oupeye", "prov": "Liège"}, {"name": "Pepinster", "prov": "Liège"}, {"name": "Plombières", "prov": "Liège"}, {"name": "Raeren", "prov": "Liège"}, {"name": "Remicourt", "prov": "Liège"}, {"name": "Saint-Georges-sur-Meuse", "prov": "Liège"}, {"name": "Saint-Nicolas", "prov": "Liège"}, {"name": "Saint-Vith", "prov": "Liège"}, {"name": "Seraing", "prov": "Liège"}, {"name": "Soumagne", "prov": "Liège"}, {"name": "Spa", "prov": "Liège"}, {"name": "Sprimont", "prov": "Liège"}, {"name": "Stavelot", "prov": "Liège"}, {"name": "Stoumont", "prov": "Liège"}, {"name": "Theux", "prov": "Liège"}, {"name": "Thimister-Clermont", "prov": "Liège"}, {"name": "Tinlot", "prov": "Liège"}, {"name": "Trois-Ponts", "prov": "Liège"}, {"name": "Trooz", "prov": "Liège"}, {"name": "Verlaine", "prov": "Liège"}, {"name": "Verviers", "prov": "Liège"}, {"name": "Visé", "prov": "Liège"}, {"name": "Waimes", "prov": "Liège"}, {"name": "Wanze", "prov": "Liège"}, {"name": "Waremme", "prov": "Liège"}, {"name": "Wasseiges", "prov": "Liège"}, {"name": "Welkenraedt", "prov": "Liège"},
        # NAMUR (38)
        {"name": "Andenne", "prov": "Namur"}, {"name": "Anhée", "prov": "Namur"}, {"name": "Assesse", "prov": "Namur"}, {"name": "Beauraing", "prov": "Namur"}, {"name": "Bièvre", "prov": "Namur"}, {"name": "Cerfontaine", "prov": "Namur"}, {"name": "Ciney", "prov": "Namur"}, {"name": "Couvin", "prov": "Namur"}, {"name": "Dinant", "prov": "Namur"}, {"name": "Doische", "prov": "Namur"}, {"name": "Éghezée", "prov": "Namur"}, {"name": "Fernelmont", "prov": "Namur"}, {"name": "Floreffe", "prov": "Namur"}, {"name": "Florennes", "prov": "Namur"}, {"name": "Fosses-la-Ville", "prov": "Namur"}, {"name": "Gedinne", "prov": "Namur"}, {"name": "Gembloux", "prov": "Namur"}, {"name": "Gesves", "prov": "Namur"}, {"name": "Hamelois", "prov": "Namur"}, {"name": "Hastière", "prov": "Namur"}, {"name": "Havelange", "prov": "Namur"}, {"name": "Houyet", "prov": "Namur"}, {"name": "Jemeppe-sur-Sambre", "prov": "Namur"}, {"name": "La Bruyère", "prov": "Namur"}, {"name": "Mettet", "prov": "Namur"}, {"name": "Namur", "prov": "Namur"}, {"name": "Ohey", "prov": "Namur"}, {"name": "Onhaye", "prov": "Namur"}, {"name": "Philippeville", "prov": "Namur"}, {"name": "Profondeville", "prov": "Namur"}, {"name": "Rochefort", "prov": "Namur"}, {"name": "Sambreville", "prov": "Namur"}, {"name": "Sombreffe", "prov": "Namur"}, {"name": "Somme-Leuze", "prov": "Namur"}, {"name": "Viroinval", "prov": "Namur"}, {"name": "Vresse-sur-Semois", "prov": "Namur"}, {"name": "Walcourt", "prov": "Namur"}, {"name": "Yvoir", "prov": "Namur"},
        # LUXEMBOURG (44)
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Attert", "prov": "Luxembourg"}, {"name": "Aubange", "prov": "Luxembourg"}, {"name": "Bastogne", "prov": "Luxembourg"}, {"name": "Bertogne", "prov": "Luxembourg"}, {"name": "Bertrix", "prov": "Luxembourg"}, {"name": "Bouillon", "prov": "Luxembourg"}, {"name": "Chiny", "prov": "Luxembourg"}, {"name": "Daverdisse", "prov": "Luxembourg"}, {"name": "Durbuy", "prov": "Luxembourg"}, {"name": "Érezée", "prov": "Luxembourg"}, {"name": "Étalle", "prov": "Luxembourg"}, {"name": "Fauvillers", "prov": "Luxembourg"}, {"name": "Florenville", "prov": "Luxembourg"}, {"name": "Gouvy", "prov": "Luxembourg"}, {"name": "Habay", "prov": "Luxembourg"}, {"name": "Herbeumont", "prov": "Luxembourg"}, {"name": "Hotton", "prov": "Luxembourg"}, {"name": "Houffalize", "prov": "Luxembourg"}, {"name": "La Roche-en-Ardenne", "prov": "Luxembourg"}, {"name": "Léglise", "prov": "Luxembourg"}, {"name": "Libin", "prov": "Luxembourg"}, {"name": "Libramont-Chevigny", "prov": "Luxembourg"}, {"name": "Manhay", "prov": "Luxembourg"}, {"name": "Marche-en-Famenne", "prov": "Luxembourg"}, {"name": "Martelange", "prov": "Luxembourg"}, {"name": "Meix-devant-Virton", "prov": "Luxembourg"}, {"name": "Messancy", "prov": "Luxembourg"}, {"name": "Musson", "prov": "Luxembourg"}, {"name": "Nassogne", "prov": "Luxembourg"}, {"name": "Neufchâteau", "prov": "Luxembourg"}, {"name": "Paliseul", "prov": "Luxembourg"}, {"name": "Rendeux", "prov": "Luxembourg"}, {"name": "Rouvroy", "prov": "Luxembourg"}, {"name": "Sainte-Ode", "prov": "Luxembourg"}, {"name": "Saint-Hubert", "prov": "Luxembourg"}, {"name": "Saint-Léger", "prov": "Luxembourg"}, {"name": "Tellin", "prov": "Luxembourg"}, {"name": "Tenneville", "prov": "Luxembourg"}, {"name": "Tintigny", "prov": "Luxembourg"}, {"name": "Vaux-sur-Sûre", "prov": "Luxembourg"}, {"name": "Vielsalm", "prov": "Luxembourg"}, {"name": "Virton", "prov": "Luxembourg"}, {"name": "Wellin", "prov": "Luxembourg"}
    ]

all_communes = get_full_list()

# --- CSS UNIQUE ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 18px !important; width: 18px !important; min-width: 18px !important;
        padding: 0px !important; margin: 1px !important; border: none !important; border-radius: 2px;
    }
    .prov-title { font-weight: bold; font-size: 12px; margin-top: 10px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- LAYOUT 40/60 ---
col_map, col_form = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte")
    
    # Création des blocs de provinces
    def render_province(p_name):
        st.markdown(f"<div class='prov-title'>{p_name}</div>", unsafe_allow_html=True)
        coms = [c for c in all_communes if c['prov'] == p_name]
        cols = st.columns(10) # 10 carrés par ligne
        for i, com in enumerate(coms):
            with cols[i % 10]:
                btn_id = f"btn_{com['name']}_{p_name}".replace(" ", "_")
                if st.button(" ", key=btn_id, help=f"{com['name']} ({p_name})"):
                    st.session_state.active_com = com['name']
                    st.session_state.active_prov = p_name
                st.markdown(f"<style>button[key='{btn_id}'] {{ background-color: {PROV_COLORS[p_name]} !important; }}</style>", unsafe_allow_html=True)

    # Ordre géographique approximatif
    render_province("Bruxelles")
    render_province("Brabant Wallon")
    render_province("Hainaut")
    render_province("Namur")
    render_province("Liège")
    render_province("Luxembourg")

with col_form:
    st.subheader("📝 Encodage")
    
    target = st.session_state.get('active_com')
    t_prov = st.session_state.get('active_prov')

    if target:
        existing = df_db[df_db['Commune'] == target]
        with st.container(border=True):
            st.title(f"📍 {target}")
            st.caption(f"Province : {t_prov}")
            
            with st.form("main_form"):
                c1, c2 = st.columns(2)
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []
                
                with c1:
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if d_pay=="Pre" else 1)
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)
                
                if st.form_submit_button("SAUVEGARDER", use_container_width=True):
                    new_row = pd.DataFrame([[target, t_prov, new_pay, "|".join(new_serv)]], columns=["Commune", "Province", "Paiement", "Services"])
                    up_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=up_df)
                    st.success("Enregistré !")
                    st.rerun()
    else:
        st.info("Cliquez sur un carré de couleur pour modifier une commune.")

    st.divider()
    # Barre de recherche de secours
    search = st.text_input("🔍 Recherche par nom")
    if search:
        res = [c for c in all_communes if search.lower() in c['name'].lower()]
        for r in res[:3]:
            if st.button(f"Sélectionner {r['name']}"):
                st.session_state.active_com = r['name']
                st.session_state.active_prov = r['prov']
                st.rerun()
