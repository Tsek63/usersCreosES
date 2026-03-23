from datetime import datetime
import streamlit as st

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("❌ Tentative d'enregistrement d'un tableau vide. Action annulée pour protéger vos données.")
        return

    # Tentative de lecture de l'ancien fichier pour comparer la taille
    try:
        df_old = conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
        # SÉCURITÉ : Si on perd plus de 20% des lignes d'un coup, on bloque
        if len(df_old) > 10 and len(df_new) < (len(df_old) * 0.8):
            st.error(f"⚠️ Alerte sécurité : Vous essayez de passer de {len(df_old)} à {len(df_new)} lignes. "
                     "L'écart est trop grand, l'enregistrement est bloqué. Contactez l'administrateur.")
            return
    except:
        pass # Si la feuille n'existe pas encore

    # Mise à jour du Backup avec date
    df_backup = df_new.copy()
    df_backup["__backup_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.update(worksheet=f"{sheet_name}_BACKUP", data=df_backup)
    
    # Mise à jour de la feuille réelle
    conn.update(worksheet=sheet_name, data=df_new)
    st.toast("💾 Données sauvegardées avec succès !", icon="✅")
