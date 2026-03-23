from datetime import datetime
import streamlit as st

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("❌ Tentative d'enregistrement d'un tableau vide. Action annulée.")
        return

    # SÉCURITÉ : Lecture de l'ancienne version pour comparer la taille
    try:
        df_old = conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
        # Si on perd plus de 20% des données d'un coup, on bloque
        if len(df_old) > 20 and len(df_new) < (len(df_old) * 0.8):
            st.error(f"⚠️ PROTECTION : L'écart de données est trop grand ({len(df_old)} vs {len(df_new)}). Enregistrement bloqué.")
            return
    except:
        pass 

    # Mise à jour du Backup (Il ne s'écrase que si la sécurité ci-dessus est passée)
    df_backup = df_new.copy()
    df_backup["__backup_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.update(worksheet=f"{sheet_name}_BACKUP", data=df_backup)
    
    # Mise à jour réelle
    conn.update(worksheet=sheet_name, data=df_new)
    st.toast("💾 Données sauvegardées !", icon="✅")
