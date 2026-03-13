import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import streamlit.components.v1 as components
import io
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Extrascolaire")

# CSS PERSONNALISÉ
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Style des boutons Bleu Canard */
        .stDownloadButton > button, .canard-button > div > button {
            background-color: #008080 !important;
            color: white !important;
            border: none !important;
        }
        
        /* Aligner le bouton Reset verticalement avec les selects */
        .reset-container {
            display: flex;
            align-items: flex-end;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Header (votre code original)
st.markdown("""
    <div style="background-color: #4169E1; padding: 15px 25px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; color: white;">
        <div style="font-size: 24px; font-weight: bold;">Utilisateurs de Creos Extrascolaire</div>
        <a href="https://timetracking-az7ibzngb3zrfbgmrgygn8.streamlit.app" target="_blank" style="background-color: white; color: #4169E1; padding: 8px 18px; border-radius: 5px; text-decoration: none; font-weight: bold;">⏱️ Time Tracking</a>
    </div>
""", unsafe_allow_html=True)

# --- 2. DONNÉES & CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_gsheets = conn.read(ttl=0).dropna(how="all")

data_fwb = {
    "Bruxelles": ["Anderlecht", "Auderghem", "Berchem-Sainte-Agathe", "Bruxelles", "Etterbeek", "Evere", "Forest", "Ganshoren", "Ixelles", "Jette", "Koekelberg", "Molenbeek-Saint-Jean", "Saint-Gilles", "Saint-Josse-ten-Noode", "Schaerbeek", "Uccle", "Watermael-Boitsfort", "Woluwe-Saint-Lambert", "Woluwe-Saint-Pierre"],
    "Brabant Wallon": ["Beauvechain", "Braine-l'Alleud", "Braine-le-Château", "Chastre", "Chaumont-Gistoux", "Court-Saint-Étienne", "Genappe", "Grez-Doiceau", "Hélécine", "Incourt", "Ittre", "Jodoigne", "La Hulpe", "Lasne", "Mont-Saint-Guibert", "Nivelles", "Orp-Jauche", "Ottignies-Louvain-la-Neuve", "Perwez", "Ramillies", "Rebecq", "Rixensart", "Tubize", "Villers-la-Ville", "Walhain", "Waterloo", "Wavre"],
    "Hainaut": ["Aiseau-Presles", "Anderlues", "Antoing", "Ath", "Beaumont", "Beloeil", "Bernissart", "Binche", "Boussu", "Braine-le-Comte", "Brugelette", "Brunehaut", "Celles", "Chapelle-lez-Herlaimont", "Charleroi", "Châtelet", "Chièvres", "Chimay", "Colfontaine", "Comines-Warneton", "Courcelles", "Dour", "Ecaussines", "Ellezelles", "Enghien", "Erquelinnes", "Estaimpuis", "Estinnes", "Farciennes", "Fleurus", "Flobecq", "Fontaine-l'Évêque", "Frameries", "Frasnes-lez-Anvaing", "Froidchapelle", "Gerpinnes", "Ham-sur-Heure-Nalinnes", "Hensies", "Jurbise", "La Louvière", "Le Roeulx", "Lens", "Les Bons Villers", "Lessines", "Leuze-en-Hainaut", "Lobbes", "Manage", "Merbes-le-Château", "Momignies", "Mons", "Mont-de-l'Enclus", "Montigny-le-Tilleul", "Morlanwelz", "Mouscron", "Pecq", "Péruwelz", "Pont-à-Celles", "Quaregnon", "Quévy", "Quiévrain", "Rumes", "Saint-Ghislain", "Seneffe", "Silly", "Sivry-Rance", "Soignies", "Thuin", "Tournai"],
    "Liège": ["Amay", "Amblève", "Ans", "Anthisnes", "Aubel", "Awans", "Aywaille", "Baelen", "Bassenge", "Berloz", "Beyne-Heusay", "Blegny", "Braives", "Büllingen", "Burdinne", "Burg-Reuland", "Butgenbach", "Chaudfontaine", "Clavier", "Comblain-au-Pont", "Crisnée", "Dalhem", "Dison", "Donceel", "Engis", "Esneux", "Eupen", "Faimes", "Ferrières", "Fexhe-le-Haut-Clocher", "Flémalle", "Fléron", "Geer", "Grâce-Hollogne", "Hamoir", "Hannut", "Héron", "Herstal", "Herve", "Huy", "Jalhay", "Juprelle", "Kelmis", "Liège", "Lierneux", "Limbourg", "Lincent", "Lontzen", "Malmedy", "Marchin", "Modave", "Nandrin", "Neupré", "Olne", "Oreye", "Ouffet", "Oupeye", "Pepinster", "Plombières", "Raeren", "Remicourt", "Saint-Georges-sur-Meuse", "Saint-Nicolas", "Saint-Vith", "Seraing", "Soumagne", "Spa", "Sprimont", "Stavelot", "Stoumont", "Theux", "Thimister-Clermont", "Tinlot", "Trois-Ponts", "Trooz", "Verlaine", "Verviers", "Visé", "Waimes", "Wanze", "Waremme", "Wasseiges", "Welkenraedt"],
    "Namur": ["Andenne", "Anhee", "Assesse", "Beauraing", "Bièvre", "Cerfontaine", "Ciney", "Couvin", "Dinant", "Doische", "Eghezée", "Fernelmont", "Floreffe", "Florennes", "Fosses-la-Ville", "Gedinne", "Gembloux", "Gesves", "Hamois", "Hastiere", "Havelange", "Houyet", "Jemeppe-sur-Sambre", "Mettet", "Namur", "Ohey", "Onhaye", "Philippeville", "Profondeville", "Rochefort", "Sambreville", "Sombreffe", "Somme-Leuze", "Viroinval", "Vresse-sur-Semois", "Walcourt", "Yvoir"],
    "Luxembourg": ["Arlon", "Attert", "Aubange", "Bastogne", "Bertogne", "Bertrix", "Bouillon", "Chiny", "Daverdisse", "Durbuy", "Erezée", "Etalle", "Fauvillers", "Florenville", "Gouvy", "Habay", "Herbeumont", "Hotton", "Houffalize", "La Roche-en-Ardenne", "Léglise", "Libin", "Libramont-Chevigny", "Manhay", "Marche-en-Famenne", "Martelange", "Meix-devant-Virton", "Messancy", "Musson", "Nassogne", "Neufchâteau", "Paliseul", "Rendeux", "Rouvroy", "Sainte-Ode", "Saint-Hubert", "Saint-Léger", "Tellin", "Tenneville", "Tintigny", "Vaux-sur-Sûre", "Vielsalm", "Virton", "Wellin"]
}

# --- 4. TABS ---
tab1, tab2 = st.tabs(["📊 Tableau de bord", "✏️ Gestion"])

with tab2:
    nt = len(df_gsheets)
    p_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Prépaiement'])
    po_stat = len(df_gsheets[df_gsheets['Paiement'] == 'Post-paiement'])
    
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("✏️ Éditer une commune")
        p_sel = st.selectbox("Province", list(data_fwb.keys()))
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1: com_sel = st.selectbox("Commune", data_fwb[p_sel])
            with c2: 
                pay_v = st.radio("Paiement", ["Prépaiement", "Post-paiement"], horizontal=True)
                serv_v = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"])
            if st.form_submit_button("Enregistrer"):
                new_r = pd.DataFrame([{"Commune": com_sel, "Province": p_sel, "Paiement": pay_v, "Services": "|".join(serv_v)}])
                df_u = pd.concat([df_gsheets[df_gsheets['Commune'] != com_sel], new_r], ignore_index=True)
                conn.update(data=df_u); st.rerun()

    with col_right:
        # Bloc Statistique Bleu Canard
        st.markdown(f"""
            <div style="background-color:#008080; padding:20px; border-radius:15px; color:white; text-align:center;">
                <div style="font-size:14px; opacity:0.8;">COMMUNES ACTIVES</div>
                <div style="font-size:60px; font-weight:bold;">{nt}</div>
                <div style="display:flex; justify-content:space-around; border-top:1px solid rgba(255,255,255,0.2); padding:15px 0;">
                    <div><b style="color:#ec4899; font-size:20px;">{p_stat}</b><br><small>Pré</small></div>
                    <div><b style="color:#38bdf8; font-size:20px;">{po_stat}</b><br><small>Post</small></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- FILTRES ALIGNÉS ---
    if 'rc' not in st.session_state: st.session_state.rc = 0
    
    f1, f2, f3, f4 = st.columns([2, 1.5, 2, 0.8])
    with f1: fl_p = st.multiselect("Province", sorted(df_gsheets['Province'].unique()) if not df_gsheets.empty else [], key=f"p_{st.session_state.rc}")
    with f2: fl_m = st.multiselect("Paiement", ["Prépaiement", "Post-paiement"], key=f"m_{st.session_state.rc}")
    with f3: fl_s = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], key=f"s_{st.session_state.rc}")
    with f4:
        st.write(" ") # Espacement pour aligner
        if st.button("❌ RESET", use_container_width=True): 
            st.session_state.rc += 1
            st.rerun()

    # --- BOUTONS BLEU CANARD ---
    df_filtered = df_gsheets.copy()
    if fl_p: df_filtered = df_filtered[df_filtered['Province'].isin(fl_p)]
    if fl_m: df_filtered = df_filtered[df_filtered['Paiement'].isin(fl_m)]
    for s in fl_s: df_filtered = df_filtered[df_filtered['Services'].str.contains(s, na=False)]
    df_sorted = df_filtered.sort_values(['Province', 'Commune'])

    b_exp1, b_exp2, _ = st.columns([1.5, 1.5, 5])
    with b_exp1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_sorted.to_excel(writer, index=False)
        st.download_button("📥 EXPORTER EXCEL", buffer.getvalue(), "creos_export.xlsx", mime="application/vnd.ms-excel")
    
    with b_exp2:
        if st.button("📄 IMPRIMER HTML"):
            f_txt = f"Province: {', '.join(fl_p) if fl_p else 'Toutes'} | Mode: {', '.join(fl_m) if fl_m else 'Tous'}"
            rows = ""
            for _, r in df_sorted.iterrows():
                rows += f"""<tr><td><b>{r.Province}</b></td><td>{r.Commune}</td>
                <td><span style="color:{'#ec4899' if r.Paiement=='Prépaiement' else '#38bdf8'}">{r.Paiement}</span></td>
                <td>{r.Services.replace('|', ' • ')}</td></tr>"""
            
            st.session_state.print_data = f"""
                <html><head><style>
                body{{font-family:sans-serif; color:#333;}} table{{width:100%; border-collapse:collapse;}} 
                th{{background:#008080; color:white; padding:10px; text-align:left;}} td{{padding:8px; border-bottom:1px solid #eee;}}
                </style></head><body>
                <h2 style="color:#4169E1;">Rapport Creos Extrascolaire</h2>
                <p style="background:#f0f0f0; padding:10px; border-radius:5px;">{f_txt}</p>
                <table><thead><tr><th>Province</th><th>Commune</th><th>Paiement</th><th>Services</th></tr></thead>
                <tbody>{rows}</tbody></table></body></html>"""

    if 'print_data' in st.session_state:
        st.download_button("💾 CLIQUEZ POUR TÉLÉCHARGER LE FICHIER D'IMPRESSION", st.session_state.print_data, "print.html", "text/html")
        del st.session_state.print_data

    # --- LISTE ET GRAPHIQUES COULEURS ---
    c_list, c_viz = st.columns([6, 4])
    with c_list:
        st.dataframe(df_sorted, use_container_width=True, hide_index=True)

    with c_viz:
        if not df_sorted.empty:
            # Graphique Paiement avec vos couleurs
            fig_p = px.pie(df_sorted, names='Paiement', hole=0.4, 
                           color='Paiement', color_discrete_map={'Prépaiement':'#ec4899', 'Post-paiement':'#38bdf8'})
            fig_p.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0), title="Répartition Paiements")
            st.plotly_chart(fig_p, use_container_width=True)

            # Graphique Services avec vos couleurs
            all_s = ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"]
            counts = [df_sorted['Services'].str.contains(s, na=False).sum() for s in all_s]
            fig_s = px.bar(x=all_s, y=counts, color=all_s,
                           color_discrete_map={
                               "Cantine Jour": "#ec4899", "Cantine Semaine": "#db2777",
                               "Cantine Mois": "#be185d", "Garderie": "#38bdf8", "Activités": "#4ade80"
                           })
            fig_s.update_layout(height=250, showlegend=False, margin=dict(t=30, b=0, l=0, r=0), title="Services actifs")
            st.plotly_chart(fig_s, use_container_width=True)
