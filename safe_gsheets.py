import streamlit as st

def safe_write(conn, sheet_name, df_new):
    if df_new.empty:
        st.error("❌ Erreur critique : Le tableau que vous tentez d'enregistrer est vide. Action annulée.")
        return

    try:
        # On lit la version actuelle sur le cloud sans cache
        df_current = conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
        
        # --- LE VERROU ---
        # Si la base actuelle contient des données (ex: 50 lignes)
        # et que vous tentez d'enregistrer un tableau beaucoup plus petit (ex: 1 ligne)
        # ALORS on bloque tout, sauf si c'est une suppression volontaire d'une seule ligne.
        if len(df_current) > 5 and len(df_new) < (len(df_current) - 1):
            st.error(f"🚨 SÉCURITÉ : Perte de données détectée ! "
                     f"Le cloud contient {len(df_current)} lignes, "
                     f"votre action en donnerait {len(df_new)}. "
                     "L'enregistrement a été stoppé pour éviter d'effacer l'historique.")
            return
    except:
        pass 

    # Si le verrou passe, on enregistre
    conn.update(worksheet=sheet_name, data=df_new)
    st.toast(f"✅ {sheet_name} mis à jour", icon="💾")
