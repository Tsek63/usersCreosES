import streamlit as st

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("❌ Tentative d'enregistrement d'un tableau vide. Action annulée.")
        return

    try:
        # On tente une lecture rapide avec un cache très court (5s) pour limiter les appels API
        df_current = conn.read(worksheet=sheet_name, ttl=5).dropna(how="all")
        
        # Sécurité anti-effacement massif
        if len(df_current) > 10 and len(df_new) < (len(df_current) * 0.7):
            st.error(f"🚨 SÉCURITÉ : L'écart de données est trop important. Enregistrement bloqué.")
            return
    except Exception as e:
        # Si Google API est saturé, on affiche un avertissement mais on ne bloque pas forcément l'écriture
        st.warning("⚠️ Note : Impossible de vérifier l'historique (Serveur Google occupé).")

    # Enregistrement
    try:
        conn.update(worksheet=sheet_name, data=df_new)
        st.toast(f"✅ {sheet_name} mis à jour", icon="💾")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'écriture Google : {e}")
