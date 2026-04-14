from datetime import datetime
import streamlit as st

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("❌ Tentative d'enregistrement d'un tableau vide. Action annulée.")
        return

    # SÉCURITÉ : On vérifie la taille avant d'écraser
    try:
        df_old = conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
        # Si le nouveau tableau est beaucoup plus petit que l'ancien, on bloque !
        if len(df_old) > 20 and len(df_new) < (len(df_old) * 0.8):
            st.error(f"⚠️ PROTECTION : Écart de données trop important ({len(df_old)} -> {len(df_new)}). Sauvegarde bloquée.")
            return
    except:
        pass 

    # Mise à jour de la feuille réelle uniquement
    conn.update(worksheet=sheet_name, data=df_new)
    st.toast(f"💾 {sheet_name} mis à jour !", icon="✅")
