import streamlit as st
import pandas as pd
from safe_gsheets import safe_write
from ui_components import icon_po

def render(conn, df_ecoles, df_config, data_fwb, df_contacts):
    df_ecoles = df_ecoles.fillna("-").astype(str).replace("nan", "-")
    df_contacts = df_contacts.fillna("-").astype(str).replace("nan", "-")
    active_communes = set(df_config[df_config['Extrascolaire'] == 'Oui']['Commune'].unique())

    # BANDEAU STATS (Correction Total nunique)
    st.markdown(f"""<div style="display:flex; gap:12px; margin-bottom:20px;">
<div style="flex:1; background:#4169E1; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">TOTAL ÉCOLES</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Fase école'].nunique()}</div>
</div>
<div style="flex:1; background:#008080; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">COMMUNES / PO</div>
<div style="font-size:48px; font-weight:bold;">{df_ecoles['Commune'].nunique()}</div>
</div>
<div style="flex:1.5; background:#1e293b; color:white; padding:20px; border-radius:10px; text-align:center;">
<div style="font-size:13px; opacity:0.8;">UTILISATEURS CREOS EXTRASCOLAIRE</div>
<div style="font-size:48px; font-weight:bold; color:#4ade80;">{len(active_communes)}</div>
</div>
</div>""", unsafe_allow_html=True)

    # (Le reste du fichier reste identique, n'oublie pas d'utiliser df_ecoles['Fase école'].nunique() partout)
    # ... Je te laisse copier le reste de ta version validée pour cet onglet ...
