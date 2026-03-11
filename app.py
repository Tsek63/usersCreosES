import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- CSS COMPLET (Fond bleu, Couleurs, Boutons) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #f0f8ff; }
    
    /* Carte : Carrés colorés */
    .stButton > button {
        border: none !important;
        height: 20px !important;
        width: 20px !important;
        min-width: 20px !important;
        padding: 0 !important;
        margin: 1px !important;
        border-radius: 4px !important;
    }

    /* Badges de la liste */
    .badge { padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; color: white; margin-right: 5px; display: inline-block; }
    .bg-pre { background-color: #4A90E2; }
    .bg-post { background-color: #2ECC71; }
    .bg-service { background-color: #F39C12; }
    
    /* Headers de province */
    .prov-header { 
        color: #1f4e79; font-weight: bold; font-size: 16px; 
        border-bottom: 2px solid #4A90E2; margin: 20px 0 10px 0; padding-bottom: 5px;
    }
    
    /* Fix pour éviter le texte vertical dans les boutons de formulaire */
    div[data-testid="stForm"] .stButton button {
        width: auto !important;
        min-width: 100px !important;
        height: auto !important;
        padding: 10px 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DONNÉES ET RÉFÉRENTIEL ---
PROV_COLORS = {
    "Bruxelles": "#FFEFA1", "Brabant Wallon": "#A9F1EB", "Hainaut": "#C8B6FF",
    "Liège": "#9AE8FF", "Namur": "#FFCCB6", "Luxembourg": "#FF85F3"
}

conn = st.connection("gsheets", type=GSheetsConnection)
df_db = conn.read(ttl=0).dropna(how="all")

# --- GÉNÉRATION DES 281 COMMUNES ---
@st.cache_data
def get_communes_belges():
    # Liste simplifiée mais structurée pour accueillir vos 281 noms
    data = {
        "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
        "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
        "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Belœil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Écaussinnes", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Honnelles", "Jurbise", "La Louvière", "Le Rœulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
        "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Bullange", "Burdinne", "Burg-Reuland", "Bütgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "La Calamine", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
        "Namur": ["Andenne", "Anhée", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Éghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamelois", "Hastière", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "La Bruyère", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
        "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Érezée", "Étalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
    }
    flat_list = []
    for prov, names in data.items():
        for n in names:
            flat_list.append({"name": n, "prov": prov})
    return flat_list

all_communes = get_communes_belges()

# --- POP-UP D'ENCODAGE ---
@st.dialog("Configuration Commune", width="small")
def edit_commune(name, prov):
    st.title(f":blue[{name}]")
    existing = df_db[df_db['Commune'] == name]
    
    d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pré-paiement"
    d_serv = str(existing['Services'].iloc[0]).split('|') if not existing.empty else []

    pay = st.radio("Mode de paiement", ["Pré-paiement", "Post-paiement"], index=0 if d_pay == "Pré-paiement" else 1, horizontal=True)
    
    st.write("**Services activés :**")
    choices = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
    serv = [c for c in choices if st.checkbox(c, value=(c in d_serv))]

    st.divider()
    # Boutons avec largeur suffisante pour éviter le texte vertical
    c1, c2 = st.columns(2)
    if c1.button("VALIDER", type="primary", use_container_width=True):
        new_row = pd.DataFrame([[name, prov, pay, "|".join(serv)]], columns=["Commune", "Province", "Paiement", "Services"])
        up_df = pd.concat([df_db[df_db['Commune'] != name], new_row], ignore_index=True)
        conn.update(data=up_df)
        st.rerun()
    
    if c2.button("ANNULER", use_container_width=True):
        st.rerun()

# --- INTERFACE ---
col_map, col_list = st.columns([0.4, 0.6])

with col_map:
    st.subheader("🗺️ Carte Interactive")
    for prov, color in PROV_COLORS.items():
        st.markdown(f"<div style='font-weight:bold; margin-top:10px;'>{prov}</div>", unsafe_allow_html=True)
        coms = [c for c in all_communes if c['prov'] == prov]
        grid = st.columns(12) # Plus de carrés par ligne pour compacité
        for i, com in enumerate(coms):
            btn_key = f"map_{com['name']}".replace(" ", "_")
            with grid[i % 12]:
                if st.button(" ", key=btn_key, help=com['name']):
                    edit_commune(com['name'], prov)
                # Injection CSS FORCÉE pour la couleur
                st.markdown(f"<style>button[key='{btn_key}'] {{ background-color: {color} !important; }}</style>", unsafe_allow_html=True)

with col_list:
    st.title("Utilisateurs Creos")
    
    # Filtres
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
        s_prov = f1.selectbox("Province", ["Toutes"] + list(PROV_COLORS.keys()))
        s_pay = f2.selectbox("Paiement", ["Tous", "Pré-paiement", "Post-paiement"])
        s_serv = f3.selectbox("Service", ["Tous", "Cantine", "Garderie", "Activités"])
        if f4.button("Effacer", use_container_width=True):
            st.rerun()

    # Filtrage
    df_f = df_db.copy()
    if s_prov != "Toutes": df_f = df_f[df_f['Province'] == s_prov]
    if s_pay != "Tous": df_f = df_f[df_f['Paiement'] == s_pay]
    if s_serv != "Tous": df_f = df_f[df_f['Services'].str.contains(s_serv, case=False, na=False)]

    # Liste par Province
    provinces_view = list(PROV_COLORS.keys()) if s_prov == "Toutes" else [s_prov]
    for p in provinces_view:
        p_data = df_f[df_f['Province'] == p].sort_values("Commune")
        if not p_data.empty:
            st.markdown(f"<div class='prov-header'>{p.upper()}</div>", unsafe_allow_html=True)
            for _, row in p_data.iterrows():
                l1, l2, l3, l4 = st.columns([0.25, 0.2, 0.45, 0.1])
                l1.write(f"**{row['Commune']}**")
                
                # Badge Paiement
                p_cls = "bg-pre" if row['Paiement'] == "Pré-paiement" else "bg-post"
                l2.markdown(f'<span class="badge {p_cls}">{row["Paiement"]}</span>', unsafe_allow_html=True)
                
                # Badges Services
                s_list = str(row['Services']).split('|')
                s_html = "".join([f'<span class="badge bg-service">{s}</span>' for s in s_list if s and s != 'nan'])
                l3.markdown(s_html, unsafe_allow_html=True)
                
                # ACTIONS : Modifier ou Supprimer
                if l4.button("📝", key=f"edit_{row['Commune']}"):
                    edit_commune(row['Commune'], p)
