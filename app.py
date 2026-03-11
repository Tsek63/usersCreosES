import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- RÉFÉRENTIEL COULEURS ---
PROV_COLORS = {
    "Bruxelles": "#FFCC00", 
    "Brabant Wallon": "#FF5733", 
    "Hainaut": "#C70039", 
    "Liège": "#900C3F", 
    "Namur": "#581845", 
    "Luxembourg": "#2E86C1"
}

# --- DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- LISTE COMPLÈTE DES 281 COMMUNES ---
@st.cache_data
def get_full_list():
    return [
        # BRUXELLES (19)
        {"n": "Anderlecht", "p": "Bruxelles"}, {"n": "Auderghem", "p": "Bruxelles"}, {"n": "Berchem-Sainte-Agathe", "p": "Bruxelles"}, {"n": "Bruxelles", "p": "Bruxelles"}, {"n": "Etterbeek", "p": "Bruxelles"}, {"n": "Evere", "p": "Bruxelles"}, {"n": "Forest", "p": "Bruxelles"}, {"n": "Ganshoren", "p": "Bruxelles"}, {"n": "Ixelles", "p": "Bruxelles"}, {"n": "Jette", "p": "Bruxelles"}, {"n": "Koekelberg", "p": "Bruxelles"}, {"n": "Molenbeek-Saint-Jean", "p": "Bruxelles"}, {"n": "Saint-Gilles", "p": "Bruxelles"}, {"n": "Saint-Josse-ten-Noode", "p": "Bruxelles"}, {"n": "Schaerbeek", "p": "Bruxelles"}, {"n": "Uccle", "p": "Bruxelles"}, {"n": "Watermael-Boitsfort", "p": "Bruxelles"}, {"n": "Woluwe-Saint-Lambert", "p": "Bruxelles"}, {"n": "Woluwe-Saint-Pierre", "p": "Bruxelles"},
        # BRABANT WALLON (27)
        {"n": "Beauvechain", "p": "Brabant Wallon"}, {"n": "Braine-l'Alleud", "p": "Brabant Wallon"}, {"n": "Braine-le-Château", "p": "Brabant Wallon"}, {"n": "Chastre", "p": "Brabant Wallon"}, {"n": "Chaumont-Gistoux", "p": "Brabant Wallon"}, {"n": "Court-Saint-Étienne", "p": "Brabant Wallon"}, {"n": "Genappe", "p": "Brabant Wallon"}, {"n": "Grez-Doiceau", "p": "Brabant Wallon"}, {"n": "Hélécine", "p": "Brabant Wallon"}, {"n": "Incourt", "p": "Brabant Wallon"}, {"n": "Ittre", "p": "Brabant Wallon"}, {"n": "Jodoigne", "p": "Brabant Wallon"}, {"n": "La Hulpe", "p": "Brabant Wallon"}, {"n": "Lasne", "p": "Brabant Wallon"}, {"n": "Mont-Saint-Guibert", "p": "Brabant Wallon"}, {"n": "Nivelles", "p": "Brabant Wallon"}, {"n": "Orp-Jauche", "p": "Brabant Wallon"}, {"n": "Ottignies-Louvain-la-Neuve", "p": "Brabant Wallon"}, {"n": "Perwez", "p": "Brabant Wallon"}, {"n": "Ramillies", "p": "Brabant Wallon"}, {"n": "Rebecq", "p": "Brabant Wallon"}, {"n": "Rixensart", "p": "Brabant Wallon"}, {"n": "Tubize", "p": "Brabant Wallon"}, {"n": "Villers-la-Ville", "p": "Brabant Wallon"}, {"n": "Walhain", "p": "Brabant Wallon"}, {"n": "Waterloo", "p": "Brabant Wallon"}, {"n": "Wavre", "p": "Brabant Wallon"},
        # HAINAUT (69)
        {"n": "Aiseau-Presles", "p": "Hainaut"}, {"n": "Anderlues", "p": "Hainaut"}, {"n": "Antoing", "p": "Hainaut"}, {"n": "Ath", "p": "Hainaut"}, {"n": "Beaumont", "p": "Hainaut"}, {"n": "Belœil", "p": "Hainaut"}, {"n": "Bernissart", "p": "Hainaut"}, {"n": "Binche", "p": "Hainaut"}, {"n": "Boussu", "p": "Hainaut"}, {"n": "Braine-le-Comte", "p": "Hainaut"}, {"n": "Brugelette", "p": "Hainaut"}, {"n": "Brunehaut", "p": "Hainaut"}, {"n": "Celles", "p": "Hainaut"}, {"n": "Chapelle-lez-Herlaimont", "p": "Hainaut"}, {"n": "Charleroi", "p": "Hainaut"}, {"n": "Châtelet", "p": "Hainaut"}, {"n": "Chièvres", "p": "Hainaut"}, {"n": "Chimay", "p": "Hainaut"}, {"n": "Colfontaine", "p": "Hainaut"}, {"n": "Comines-Warneton", "p": "Hainaut"}, {"n": "Courcelles", "p": "Hainaut"}, {"n": "Dour", "p": "Hainaut"}, {"n": "Écaussinnes", "p": "Hainaut"}, {"n": "Ellezelles", "p": "Hainaut"}, {"n": "Enghien", "p": "Hainaut"}, {"n": "Erquelinnes", "p": "Hainaut"}, {"n": "Estaimpuis", "p": "Hainaut"}, {"n": "Estinnes", "p": "Hainaut"}, {"n": "Farciennes", "p": "Hainaut"}, {"n": "Fleurus", "p": "Hainaut"}, {"n": "Fontaine-l'Évêque", "p": "Hainaut"}, {"n": "Frameries", "p": "Hainaut"}, {"n": "Frasnes-lez-Anvaing", "p": "Hainaut"}, {"n": "Froidchapelle", "p": "Hainaut"}, {"n": "Gerpinnes", "p": "Hainaut"}, {"n": "Ham-sur-Heure-Nalinnes", "p": "Hainaut"}, {"n": "Hensies", "p": "Hainaut"}, {"n": "Honnelles", "p": "Hainaut"}, {"n": "Jurbise", "p": "Hainaut"}, {"n": "La Louvière", "p": "Hainaut"}, {"n": "Le Rœulx", "p": "Hainaut"}, {"n": "Lens", "p": "Hainaut"}, {"n": "Les Bons Villers", "p": "Hainaut"}, {"n": "Lessines", "p": "Hainaut"}, {"n": "Leuze-en-Hainaut", "p": "Hainaut"}, {"n": "Lobbes", "p": "Hainaut"}, {"n": "Manage", "p": "Hainaut"}, {"n": "Merbes-le-Château", "p": "Hainaut"}, {"n": "Momignies", "p": "Hainaut"}, {"n": "Mons", "p": "Hainaut"}, {"n": "Mont-de-l'Enclus", "p": "Hainaut"}, {"n": "Montigny-le-Tilleul", "p": "Hainaut"}, {"n": "Morlanwelz", "p": "Hainaut"}, {"n": "Mouscron", "p": "Hainaut"}, {"name": "Musson", "prov": "Hainaut"}, {"n": "Pecq", "p": "Hainaut"}, {"n": "Péruwelz", "p": "Hainaut"}, {"n": "Pont-à-Celles", "p": "Hainaut"}, {"n": "Quaregnon", "p": "Hainaut"}, {"n": "Quévy", "p": "Hainaut"}, {"n": "Quiévrain", "p": "Hainaut"}, {"n": "Rumes", "p": "Hainaut"}, {"n": "Saint-Ghislain", "p": "Hainaut"}, {"n": "Seneffe", "p": "Hainaut"}, {"n": "Silly", "p": "Hainaut"}, {"n": "Sivry-Rance", "p": "Hainaut"}, {"n": "Soignies", "p": "Hainaut"}, {"n": "Thuin", "p": "Hainaut"}, {"n": "Tournai", "p": "Hainaut"},
        # LIÈGE (84)
        {"n": "Amay", "p": "Liège"}, {"n": "Amblève", "p": "Liège"}, {"n": "Ans", "p": "Liège"}, {"n": "Anthisnes", "p": "Liège"}, {"n": "Aubel", "p": "Liège"}, {"n": "Awans", "p": "Liège"}, {"n": "Aywaille", "p": "Liège"}, {"n": "Baelen", "p": "Liège"}, {"n": "Bassenge", "p": "Liège"}, {"n": "Berloz", "p": "Liège"}, {"n": "Beyne-Heusay", "p": "Liège"}, {"n": "Blegny", "p": "Liège"}, {"n": "Braives", "p": "Liège"}, {"n": "Bullange", "p": "Liège"}, {"n": "Burdinne", "p": "Liège"}, {"n": "Burg-Reuland", "p": "Liège"}, {"n": "Bütgenbach", "p": "Liège"}, {"n": "Chaudfontaine", "p": "Liège"}, {"n": "Clavier", "p": "Liège"}, {"n": "Comblain-au-Pont", "p": "Liège"}, {"n": "Crisnée", "p": "Liège"}, {"n": "Dalhem", "p": "Liège"}, {"n": "Dison", "p": "Liège"}, {"n": "Donceel", "p": "Liège"}, {"n": "Engis", "p": "Liège"}, {"n": "Esneux", "p": "Liège"}, {"n": "Eupen", "p": "Liège"}, {"n": "Faimes", "p": "Liège"}, {"n": "Ferrières", "p": "Liège"}, {"n": "Fexhe-le-Haut-Clocher", "p": "Liège"}, {"n": "Flémalle", "p": "Liège"}, {"n": "Fléron", "p": "Liège"}, {"n": "Geer", "p": "Liège"}, {"n": "Grâce-Hollogne", "p": "Liège"}, {"n": "Hamoir", "p": "Liège"}, {"n": "Hannut", "p": "Liège"}, {"n": "Héron", "p": "Liège"}, {"n": "Herstal", "p": "Liège"}, {"n": "Herve", "p": "Liège"}, {"n": "Huy", "p": "Liège"}, {"n": "Jalhay", "p": "Liège"}, {"n": "Juprelle", "p": "Liège"}, {"n": "La Calamine", "p": "Liège"}, {"n": "Liège", "p": "Liège"}, {"n": "Lierneux", "p": "Liège"}, {"n": "Limbourg", "p": "Liège"}, {"n": "Lincent", "p": "Liège"}, {"n": "Lontzen", "p": "Liège"}, {"n": "Malmedy", "p": "Liège"}, {"n": "Marchin", "p": "Liège"}, {"n": "Modave", "p": "Liège"}, {"n": "Nandrin", "p": "Liège"}, {"n": "Neupré", "p": "Liège"}, {"n": "Olne", "p": "Liège"}, {"n": "Oreye", "p": "Liège"}, {"n": "Ouffet", "p": "Liège"}, {"n": "Oupeye", "p": "Liège"}, {"n": "Pepinster", "p": "Liège"}, {"n": "Plombières", "p": "Liège"}, {"n": "Raeren", "p": "Liège"}, {"n": "Remicourt", "p": "Liège"}, {"n": "Saint-Georges-sur-Meuse", "p": "Liège"}, {"n": "Saint-Nicolas", "p": "Liège"}, {"n": "Saint-Vith", "p": "Liège"}, {"n": "Seraing", "p": "Liège"}, {"n": "Soumagne", "p": "Liège"}, {"n": "Spa", "p": "Liège"}, {"n": "Sprimont", "p": "Liège"}, {"n": "Stavelot", "p": "Liège"}, {"n": "Stoumont", "p": "Liège"}, {"n": "Theux", "p": "Liège"}, {"n": "Thimister-Clermont", "p": "Liège"}, {"n": "Tinlot", "p": "Liège"}, {"n": "Trois-Ponts", "p": "Liège"}, {"n": "Trooz", "p": "Liège"}, {"n": "Verlaine", "p": "Liège"}, {"n": "Verviers", "p": "Liège"}, {"n": "Visé", "p": "Liège"}, {"n": "Waimes", "p": "Liège"}, {"n": "Wanze", "p": "Liège"}, {"n": "Waremme", "p": "Liège"}, {"n": "Wasseiges", "p": "Liège"}, {"n": "Welkenraedt", "p": "Liège"},
        # NAMUR (38)
        {"n": "Andenne", "p": "Namur"}, {"n": "Anhée", "p": "Namur"}, {"n": "Assesse", "p": "Namur"}, {"n": "Beauraing", "p": "Namur"}, {"n": "Bièvre", "p": "Namur"}, {"n": "Cerfontaine", "p": "Namur"}, {"n": "Ciney", "p": "Namur"}, {"n": "Couvin", "p": "Namur"}, {"n": "Dinant", "p": "Namur"}, {"n": "Doische", "p": "Namur"}, {"n": "Éghezée", "p": "Namur"}, {"n": "Fernelmont", "p": "Namur"}, {"n": "Floreffe", "p": "Namur"}, {"n": "Florennes", "p": "Namur"}, {"n": "Fosses-la-Ville", "p": "Namur"}, {"n": "Gedinne", "p": "Namur"}, {"n": "Gembloux", "p": "Namur"}, {"n": "Gesves", "p": "Namur"}, {"n": "Hamelois", "p": "Namur"}, {"n": "Hastière", "p": "Namur"}, {"n": "Havelange", "p": "Namur"}, {"n": "Houyet", "p": "Namur"}, {"n": "Jemeppe-sur-Sambre", "p": "Namur"}, {"n": "La Bruyère", "p": "Namur"}, {"n": "Mettet", "p": "Namur"}, {"n": "Namur", "p": "Namur"}, {"n": "Ohey", "p": "Namur"}, {"n": "Onhaye", "p": "Namur"}, {"n": "Philippeville", "p": "Namur"}, {"n": "Profondeville", "p": "Namur"}, {"n": "Rochefort", "p": "Namur"}, {"n": "Sambreville", "p": "Namur"}, {"n": "Sombreffe", "p": "Namur"}, {"n": "Somme-Leuze", "p": "Namur"}, {"n": "Viroinval", "p": "Namur"}, {"n": "Vresse-sur-Semois", "p": "Namur"}, {"n": "Walcourt", "p": "Namur"}, {"n": "Yvoir", "p": "Namur"},
        # LUXEMBOURG (44)
        {"n": "Arlon", "p": "Luxembourg"}, {"n": "Attert", "p": "Luxembourg"}, {"n": "Aubange", "p": "Luxembourg"}, {"n": "Bastogne", "p": "Luxembourg"}, {"n": "Bertogne", "p": "Luxembourg"}, {"n": "Bertrix", "p": "Luxembourg"}, {"n": "Bouillon", "p": "Luxembourg"}, {"n": "Chiny", "p": "Luxembourg"}, {"n": "Daverdisse", "p": "Luxembourg"}, {"n": "Durbuy", "p": "Luxembourg"}, {"n": "Érezée", "p": "Luxembourg"}, {"n": "Étalle", "p": "Luxembourg"}, {"n": "Fauvillers", "p": "Luxembourg"}, {"n": "Florenville", "p": "Luxembourg"}, {"n": "Gouvy", "p": "Luxembourg"}, {"n": "Habay", "p": "Luxembourg"}, {"n": "Herbeumont", "p": "Luxembourg"}, {"n": "Hotton", "p": "Luxembourg"}, {"n": "Houffalize", "p": "Luxembourg"}, {"n": "La Roche-en-Ardenne", "p": "Luxembourg"}, {"n": "Léglise", "p": "Luxembourg"}, {"n": "Libin", "p": "Luxembourg"}, {"n": "Libramont-Chevigny", "p": "Luxembourg"}, {"n": "Manhay", "p": "Luxembourg"}, {"n": "Marche-en-Famenne", "p": "Luxembourg"}, {"n": "Martelange", "p": "Luxembourg"}, {"n": "Meix-devant-Virton", "p": "Luxembourg"}, {"n": "Messancy", "p": "Luxembourg"}, {"n": "Musson", "p": "Luxembourg"}, {"n": "Nassogne", "p": "Luxembourg"}, {"n": "Neufchâteau", "p": "Luxembourg"}, {"n": "Paliseul", "p": "Luxembourg"}, {"n": "Rendeux", "p": "Luxembourg"}, {"n": "Rouvroy", "p": "Luxembourg"}, {"n": "Sainte-Ode", "p": "Luxembourg"}, {"n": "Saint-Hubert", "p": "Luxembourg"}, {"n": "Saint-Léger", "p": "Luxembourg"}, {"n": "Tellin", "p": "Luxembourg"}, {"n": "Tenneville", "p": "Luxembourg"}, {"n": "Tintigny", "p": "Luxembourg"}, {"n": "Vaux-sur-Sûre", "p": "Luxembourg"}, {"n": "Vielsalm", "p": "Luxembourg"}, {"n": "Virton", "p": "Luxembourg"}, {"n": "Wellin", "p": "Luxembourg"}
    ]

all_communes = get_full_list()

# --- INTERFACE ---
col_sidebar, col_main = st.columns([0.35, 0.65])

with col_sidebar:
    st.title("🗺️ État")
    
    # Légende épurée
    cols_leg = st.columns(3)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        cols_leg[i % 3].markdown(f"<span style='color:{c}; font-size:18px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.divider()
    search = st.text_input("🔍 Rechercher...", "").strip().lower()

    # CSS CARRÉS PLEINS 25px
    st.markdown("""
        <style>
        div.stButton > button {
            height: 25px !important; width: 25px !important; min-width: 25px !important;
            border-radius: 2px; padding: 0 !important; margin: 1px !important;
            border: none !important; color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    display_list = [c for c in all_communes if search in c['n'].lower()]
    grid_cols = st.columns(10)
    
    for i, com in enumerate(display_list):
        tile_color = PROV_COLORS.get(com['p'], "#EEE")
        with grid_cols[i % 10]:
            if st.button(" ", key=f"t_{com['n']}", help=f"{com['n']} ({com['p']})"):
                st.session_state.active_com = com['n']
                st.session_state.active_prov = com['p']
                st.rerun()
            st.markdown(f"<style>button[key='t_{com['n']}'] {{ background-color: {tile_color} !important; }}</style>", unsafe_allow_html=True)

with col_main:
    st.header("📊 Stats & Exports")
    s1, s2, s3 = st.columns(3)
    s1.metric("Communes traitées", f"{len(df_db)} / 281")
    
    if not df_db.empty:
        # EXPORTS
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df_db.to_excel(writer, index=False)
        st.download_button("📥 Excel", buf.getvalue(), "export.xlsx")
        st.download_button("📥 CSV (pour PDF)", df_db.to_csv(index=False).encode('utf-8'), "export.csv")
        
        serv_series = df_db['Services'].str.split('|').explode()
        s2.metric("Total Services", len(serv_series[serv_series != ""]))
        s3.metric("Dernier :", df_db['Commune'].iloc[-1] if not df_db.empty else "-")

    st.divider()

    target = st.session_state.get('active_com')
    t_prov = st.session_state.get('active_prov', "Inconnue")

    if target:
        existing = df_db[df_db['Commune'] == target]
        with st.container(border=True):
            st.subheader(f"📍 {target} ({t_prov})")
            with st.form("f_val"):
                c1, c2 = st.columns(2)
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []
                with c1:
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if d_pay=="Pre" else 1, horizontal=True)
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)
                
                if st.form_submit_button("✅ ENREGISTRER"):
                    new_row = pd.DataFrame([[target, t_prov, new_pay, "|".join(new_serv)]], columns=["Commune", "Province", "Paiement", "Services"])
                    up_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=up_df)
                    st.rerun()
    else:
        st.info("Sélectionnez un carré à gauche.")

    if not df_db.empty:
        st.bar_chart(df_db['Province'].value_counts())
