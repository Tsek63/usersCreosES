from datetime import datetime
import streamlit as st

EXPECTED_COLUMNS = {
    "EcolesConfig": ["Fase école", "Commune", "Province", "Extrascolaire", "Paiement", "Services"],
    "Contacts": ["Province", "Commune", "Titre", "Nom", "Téléphone", "GSM", "Email"],
    "TimeTracking": ["date", "intervenante", "tache", "quantite", "nb_ecoles"]
}

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("Tentative d'écriture vide annulée.")
        return
    
    # Backup
    df_backup = df_new.copy()
    df_backup["__backup_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.update(worksheet=f"{sheet_name}_BACKUP", data=df_backup)
    
    # Update principal
    conn.update(worksheet=sheet_name, data=df_new)
