import streamlit as st
from ui_components import service_badges

def render(df_ecoles, df_config, data_fwb):
    st.subheader("🔍 Consultation par Commune")
    
    c1, c2 = st.columns(2)
    with c1:
        prov = st.selectbox("Province", ["Choisir..."] + list(data_fwb.keys()))
    with c2:
        communes = data_fwb.get(prov, []) if prov != "Choisir..." else []
        commune_sel = st.selectbox("Commune", [""] + communes)

    if commune_sel:
        schools = df_ecoles[df_ecoles['Commune'] == commune_sel]
        for _, s in schools.iterrows():
            config = df_config[df_config['Fase école'] == s['Fase école']]
            status_html = "✅ Active" if not config.empty and config.iloc[0]['Extrascolaire'] == 'Oui' else "⚪ Inactive"
            
            st.markdown(f"""
                <div class="school-card">
                    <div style="display:flex; justify-content:space-between;">
                        <b>{s['Ecole']}</b> <span>{status_html}</span>
                    </div>
                    <div style="font-size:12px; color:gray;">Fase: {s['Fase école']} | Dir: {s.get('Directeur.rice','-')}</div>
                    <div>{service_badges(config.iloc[0]['Services'] if not config.empty else "")}</div>
                </div>
            """, unsafe_allow_html=True)
