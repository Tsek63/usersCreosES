import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Creos Dashboard")

# --- RÉFÉRENTIEL ---
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

@st.cache_data
def get_all_communes():
    # Liste complète abrégée (insérez ici votre liste complète de 281)
    return [
        {"name": "Anderlecht", "prov": "Bruxelles"}, {"name": "Auderghem", "prov": "Bruxelles"}, {"name": "Bruxelles", "prov": "Bruxelles"},
        {"name": "Wavre", "prov": "Brabant Wallon"}, {"name": "Nivelles", "prov": "Brabant Wallon"}, {"name": "Waterloo", "prov": "Brabant Wallon"},
        {"name": "Mons", "prov": "Hainaut"}, {"name": "Charleroi", "prov": "Hainaut"}, {"name": "Tournai", "prov": "Hainaut"},
        {"name": "Liège", "prov": "Liège"}, {"name": "Oreye", "prov": "Liège"}, {"name": "Huy", "prov": "Liège"},
        {"name": "Namur", "prov": "Namur"}, {"name": "Dinant", "prov": "Namur"}, {"name": "Gembloux", "prov": "Namur"},
        {"name": "Arlon", "prov": "Luxembourg"}, {"name": "Bastogne", "prov": "Luxembourg"}, {"name": "Durbuy", "prov": "Luxembourg"}
        # ... rajoutez les 281 ici
    ]

all_communes_list = get_all_communes()

# --- INTERFACE (35% / 65%) ---
col_sidebar, col_main = st.columns([0.35, 0.65])

with col_sidebar:
    st.title("🗺️ État d'avancement")
    
    # Légende (uniquement provinces)
    st.markdown("**Provinces**")
    cols_leg = st.columns(3)
    for i, (p, c) in enumerate(PROV_COLORS.items()):
        cols_leg[i % 3].markdown(f"<span style='color:{c}; font-size:18px;'>■</span> {p}", unsafe_allow_html=True)
    
    st.divider()
    search = st.text_input("🔍 Filtrer...", "").strip().lower()

# CSS pour CARRÉS PLEINS, PETITS ET PROPRES
    st.markdown("""
        <style>
        div.stButton > button {
            height: 25px !important;
            width: 25px !important;
            min-width: 25px !important;
            border-radius: 4px;
            padding: 0px !important;
            margin: 1px !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            transition: transform 0.2s;
        }
        div.stButton > button:hover {
            transform: scale(1.2);
            border: 1px solid black !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    display_list = [c for c in all_communes_list if search in c['name'].lower()]
    grid_cols = st.columns(10) # Plus de colonnes car carrés plus petits
    
    for i, com in enumerate(display_list):
        tile_color = PROV_COLORS.get(com['prov'], "#EEE")
        
        with grid_cols[i % 10]:
            # Le bouton prend la couleur de la province via le paramètre style injecté
            if st.button(" ", key=f"t_{com['name']}", help=f"{com['name']} ({com['prov']})"):
                st.session_state.active_com = com['name']
                st.session_state.active_prov = com['prov']
                st.rerun()
            # Injection de couleur de fond forcée pour le bouton spécifique
            st.markdown(f"<style>button[key='t_{com['name']}'] {{ background-color: {tile_color} !important; }}</style>", unsafe_allow_html=True)

with col_main:
    # --- STATS & EXPORTS ---
    st.header("📊 Statistiques & Exports")
    
    s1, s2, s3 = st.columns(3)
    s1.metric("Communes", f"{len(df_db)} / 281")
    
    # Boutons d'export
    if not df_db.empty:
        # Export Excel
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
            df_db.to_excel(writer, index=False, sheet_name='Data')
        
        st.download_button(label="📥 Télécharger Excel", data=buffer_excel.getvalue(), file_name="creos_export.xlsx", mime="application/vnd.ms-excel")
        
        # Export PDF (Format CSV pour simplicité immédiate ou message de génération)
        st.download_button(label="📥 Télécharger PDF (CSV)", data=df_db.to_csv(index=False).encode('utf-8'), file_name="creos_export.csv", mime="text/csv")

    st.divider()

    # --- FORMULAIRE ---
    target = st.session_state.get('active_com')
    target_prov = st.session_state.get('active_prov', "Inconnue")

    if target:
        existing = df_db[df_db['Commune'] == target]
        with st.container(border=True):
            st.subheader(f"📍 {target} ({target_prov})")
            with st.form("form_val"):
                c1, c2 = st.columns(2)
                d_pay = existing['Paiement'].iloc[0] if not existing.empty else "Pre"
                d_serv = existing['Services'].iloc[0].split('|') if not existing.empty and isinstance(existing['Services'].iloc[0], str) else []

                with c1:
                    new_pay = st.radio("Paiement", ["Pre", "Post"], index=0 if d_pay == "Pre" else 1, horizontal=True)
                with c2:
                    new_serv = st.multiselect("Services", ["Cantine Jour", "Cantine Semaine", "Cantine Mois", "Garderie", "Activités"], default=d_serv)

                if st.form_submit_button("✅ ENREGISTRER"):
                    new_row = pd.DataFrame([[target, target_prov, new_pay, "|".join(new_serv)]], 
                                         columns=["Commune", "Province", "Paiement", "Services"])
                    updated_df = pd.concat([df_db[df_db['Commune'] != target], new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.toast("Mise à jour réussie !")
                    st.rerun()
    else:
        st.info("Sélectionnez une commune (carré coloré) pour l'éditer.")

    if not df_db.empty:
        st.subheader("Répartition par province")
        st.bar_chart(df_db['Province'].value_counts())
