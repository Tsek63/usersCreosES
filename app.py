import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# Couleurs de l'application
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
        .stats-duck-blue {{
            background-color: {COLORS['Bleu-Canard']};
            color: white;
            border-radius: 10px;
            padding: 20px;
        }}
        .stat-badge {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 2px;
            margin-right: 8px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
    </style>
    <div class="main-header">
        <div class="header-title">Utilisateurs de Creos Extrascolaire</div>
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

# --- 4. ONGLETS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord", "✏️ Gestion des Communes"])

with tab1:
    # On affiche simplement le tableau pour vérifier que les données sont là
    st.subheader("Aperçu des communes enregistrées")
    st.dataframe(df_gsheets, use_container_width=True, hide_index=True)

with tab2:
    # --- CALCULS POUR LE BLOC STATS ---
    total_val = len(df_gsheets)
    pre_val = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    post_val = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    
    # Comptage des services
    s_c_jour = df_gsheets['Services'].str.contains("Cantine Jour", na=False).sum()
    s_c_sem = df_gsheets['Services'].str.contains("Cantine Semaine", na=False).sum()
    s_c_mois = df_gsheets['Services'].str.contains("Cantine Mois", na=False).sum()
    s_gard = df_gsheets['Services'].str.contains("Garderie", na=False).sum()
    s_act = df_gsheets['Services'].str.contains("Activités", na=False).sum()

    col_form, col_stats = st.columns([1.5, 1])

    with col_form:
        st.subheader("✏️ Gestion des données")
        prov_selected = st.selectbox("1. Choisir une Province", list(data_fwb.keys()))
        
        with st.form("edit_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                comm_selected = st.selectbox("2. Choisir une Commune", data_fwb[prov_selected])
            with f_col2:
                pay_val = st.radio("3. Mode de paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_val = st.multiselect("4. Services actifs", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            
            if st.form_submit_button("💾 ENREGISTRER / MODIFIER", use_container_width=True):
                new_row = pd.DataFrame([{
                    "Commune": comm_selected, 
                    "Province": prov_selected, 
                    "Paiement": pay_val, 
                    "Services": "|".join(serv_val)
                }])
                df_final = pd.concat([df_gsheets[df_gsheets['Commune'] != comm_selected], new_row], ignore_index=True)
                conn.update(data=df_final)
                st.success(f"Mise à jour réussie pour {comm_selected} !")
                st.rerun()

    with col_stats:
        # AFFICHAGE DU BLOC BLEU CANARD DYNAMIQUE
        st.markdown(f"""
            <div class="stats-duck-blue">
                <div style="font-size: 0.85em; opacity: 0.9; text-transform: uppercase;">Total des communes actives</div>
                <div style="font-size: 3.5em; font-weight: bold; margin-bottom: 20px;">{total_val}</div>
                
                <div style="display: flex; gap: 25px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">PAIEMENT</div>
                        <div style="font-size: 0.9em; margin-bottom: 8px;"><span class="stat-badge" style="background:#fb923c"></span>Pré : <b>{pre_val}</b></div>
                        <div style="font-size: 0.9em;"><span class="stat-badge" style="background:#38bdf8"></span>Post : <b>{post_val}</b></div>
                    </div>
                    <div style="flex: 1.3;">
                        <div style="font-size: 0.75em; font-weight: bold; margin-bottom: 12px; opacity: 0.8;">SERVICES</div>
                        <div style="font-size: 0.85em; margin-bottom: 4px;"><span class="stat-badge" style="background:#fb923c"></span>Cantine Jour : <b>{s_c_jour}</b></div>
                        <div style="font-size: 0.85em; margin-bottom: 4px;"><span class="stat-badge" style="background:#f59e0b"></span>Cantine Semaine : <b>{s_c_sem}</b></div>
                        <div style="font-size: 0.85em; margin-bottom: 4px;"><span class="stat-badge" style="background:#d97706"></span>Cantine Mois : <b>{s_c_mois}</b></div>
                        <div style="font-size: 0.85em; margin-bottom: 4px;"><span class="stat-badge" style="background:#38bdf8"></span>Garderie : <b>{s_gard}</b></div>
                        <div style="font-size: 0.85em; margin-bottom: 4px;"><span class="stat-badge" style="background:#4ade80"></span>Activités : <b>{s_act}</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
