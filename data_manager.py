import pandas as pd
import streamlit as st

PROV_NORM = {
    "liege": "Liège", "liège": "Liège", "province de liège": "Liège",
    "hainaut": "Hainaut", "namur": "Namur", "luxembourg": "Luxembourg",
    "brabant wallon": "Brabant Wallon", "bruxelles": "Bruxelles",
}

class DataManager:
    def __init__(self, conn):
        self.conn = conn

    def clean_df(self, df):
        for col in ['Fase école', 'Fase PO', 'Code postal']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df.fillna("-").replace("nan", "-")

    @st.cache_data(ttl=60)
    def load_all_data(_self):
        try:
            df_ecoles = _self.clean_df(_self.conn.read(worksheet="Ecoles", ttl=60).dropna(how="all"))
            df_config = _self.clean_df(_self.conn.read(worksheet="EcolesConfig", ttl=60).dropna(how="all"))
            df_contacts = _self.clean_df(_self.conn.read(worksheet="Contacts", ttl=60).dropna(how="all"))
            try:
                df_time = _self.conn.read(worksheet="TimeTracking", ttl=60).dropna(how="all")
            except:
                df_time = pd.DataFrame(columns=["date", "intervenante", "tache", "quantite", "nb_ecoles"])
            
            data_fwb = {}
            for _, row in df_ecoles.iterrows():
                p_raw = str(row.get('Province', '')).lower().strip()
                prov = PROV_NORM.get(p_raw, row.get('Province', 'Inconnu'))
                comm = str(row.get('Commune', '')).strip()
                if not comm or comm.startswith('Province'): continue
                if prov not in data_fwb: data_fwb[prov] = set()
                data_fwb[prov].add(comm)
            
            return df_ecoles, df_config, df_contacts, df_time, {k: sorted(list(v)) for k, v in data_fwb.items()}
        except Exception as e:
            st.error("🔌 Erreur de connexion avec Google Sheets. Veuillez patienter 30 secondes et actualiser.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
