# 🏫 Creos Extrascolaire - Outil de Pilotage et Gestion

Cette application Streamlit permet de piloter le déploiement de l'Extrascolaire de Creos dans les écoles de la Fédération Wallonie-Bruxelles. Elle centralise les configurations, les contacts et le suivi du temps de travail.

## 🚀 Fonctionnalités principales

L'application est divisée en quatre modules complémentaires :

1.  **📊 Tableau de bord** : Visualisation cartographique du déploiement par province, liste alphabétique des communes actives et centre d'audit automatique (détection des contacts manquants et taux d'implémentation).
2.  **🏫 Écoles par Commune** : Annuaire complet des écoles avec recherche par nom ou code FASE. Gestion détaillée des contacts spécifiques à l'extrascolaire (avec module de modification et liens directs tel/email).
3.  **⚙️ Gestion & Configuration** : Module d'encodage individuel ou de masse (par PO). Génération de rapports de situation avec graphiques et export de sécurité intégral de la base de données vers Excel.
4.  **⏱️ Time Tracking** : Suivi des tâches et du temps passé par les intervenantes.

## 🛠️ Structure du Projet

Pour garantir la maintenance et l'évolution de l'outil, le code est structuré de manière modulaire :

- `app.py` : Point d'entrée de l'application (Navigation et Footer).
- `data_manager.py` : Gestion centralisée de la lecture et du nettoyage des données Google Sheets.
- `ui_components.py` : Composants graphiques réutilisables (CSS, Cartes d'audit, Icônes).
- `safe_gsheets.py` : Moteur d'écriture sécurisé avec système de backup et barrière anti-effacement.
- `AppTimeTracking.py` : Module spécifique au suivi du temps.
- `tabs/` : Dossier contenant la logique métier de chaque onglet (`dashboard.py`, `school_search.py`, `config_schools.py`).

## 📋 Configuration des Données (Google Sheets)

L'application nécessite une connexion à une Google Sheet contenant les feuilles suivantes :

- **Ecoles** : Liste officielle FWB (Colonnes : Province, Commune, Ecole, Fase école, Directeur.rice, Email, Téléphone, etc.).
- **EcolesConfig** : Paramétrage Creos (Colonnes : Fase école, Commune, Province, Extrascolaire, Paiement, Services).
- **Contacts** : Annuaire des responsables (Colonnes : Province, Commune, Titre, Nom, Téléphone, GSM, Email).
- **TimeTracking** : Historique des tâches (Colonnes : date, intervenante, tache, quantite, nb_ecoles).

## 💻 Installation Locale

1. Cloner le projet.
2. Installer les dépendances : 
   ```bash
   pip install -r requirements.txt
