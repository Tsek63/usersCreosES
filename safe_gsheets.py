from datetime import datetime
import streamlit as st

EXPECTED_COLUMNS = {
    "EcolesConfig": [
        "Fase école", "Commune", "Province",
        "Extrascolaire", "Paiement", "Services"
    ],
    "Contacts": [
        "Province", "Commune", "Titre",
        "Nom", "Téléphone", "GSM", "Email"
    ],
    "TimeTracking": [
        "Date", "Utilisateur", "Commune",
        "Heures", "Description"
    ]
}

def backup_sheet(conn, sheet_name, df):
    df_copy = df.copy()
    df_copy["__backup_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.update(worksheet=f"{sheet_name}_BACKUP", data=df_copy)

def safe_write(conn, sheet_name, df_new):
    # 1. DF vide = interdit
    if df_new.empty:
        st.error(f"❌ Tentative d'écriture vide dans {sheet_name}")
        return

    # 2. Colonnes manquantes = interdit
    expected = EXPECTED_COLUMNS[sheet_name]
    if not all(col in df_new.columns for col in expected):
        st.error(f"❌ Colonnes manquantes dans {sheet_name}")
        return

    # 3. Lire la version actuelle
    try:
        df_old = conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
    except:
        df_old = df_new.copy()

    # 4. Protection contre pertes massives
    if len(df_new) < len(df_old) - 1:
        st.error(f"❌ Perte de données détectée dans {sheet_name} : écriture annulée")
        return

    # 5. Backup
    backup_sheet(conn, sheet_name, df_new)

    # 6. Écriture
    conn.update(worksheet=sheet_name, data=df_new)
