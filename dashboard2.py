import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px

def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

def filtrer_donnees(df, operateur, date_colonne, date_debut, date_fin):
    df[date_colonne] = pd.to_datetime(df[date_colonne]).dt.date
    date_debut = pd.to_datetime(date_debut).date()
    date_fin = pd.to_datetime(date_fin).date()
    mask = (df['Prénom et nom'] == operateur) & (df[date_colonne] >= date_debut) & (df[date_colonne] <= date_fin)
    return df[mask]

st.title("Analyse des interventions des opérateurs")

fichier_principal = st.file_uploader("Choisissez le fichier principal (donnee_Aesma.xlsx)", type="xlsx")

if fichier_principal is not None:
    df_principal = charger_donnees(fichier_principal)
    
    operateurs = df_principal['Prénom et nom'].unique()
    operateur_selectionne = st.selectbox("Choisissez un opérateur", operateurs)
    
    date_colonne = st.selectbox("Choisissez la colonne de date", df_principal.columns)
    
    periodes = ["Jour", "Semaine", "Mois", "Trimestre", "Année", "Personnalisé"]
    periode_selectionnee = st.selectbox("Choisissez une période", periodes)
    
    today = datetime.now().date()
    
    if periode_selectionnee == "Jour":
        date_debut = date_fin = st.date_input("Choisissez le jour", today)
    elif periode_selectionnee == "Semaine":
        date_debut = st.date_input("Début de la semaine", today - timedelta(days=today.weekday()))
        date_fin = date_debut + timedelta(days=6)
    elif periode_selectionnee == "Mois":
        date_debut = st.date_input("Choisissez le mois", today.replace(day=1))
        date_fin = (date_debut.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif periode_selectionnee == "Trimestre":
        trimestre = (today.month - 1) // 3 + 1
        date_debut = st.date_input("Début du trimestre", datetime(today.year, 3 * trimestre - 2, 1).date())
        date_fin = (date_debut.replace(day=1) + timedelta(days=93)).replace(day=1) - timedelta(days=1)
    elif periode_selectionnee == "Année":
        date_debut = st.date_input("Choisissez l'année", today.replace(month=1, day=1))
        date_fin = date_debut.replace(month=12, day=31)
    else:  # Personnalisé
        date_debut = st.date_input("Date de début")
        date_fin = st.date_input("Date de fin")
    
    if st.button("Analyser"):
        df_filtre = filtrer_donnees(df_principal, operateur_selectionne, date_colonne, date_debut, date_fin)
        
        st.write(f"Nombre d'interventions pour {operateur_selectionne} du {date_debut} au {date_fin} : {len(df_filtre)}")
        
        if len(df_filtre) >= 2:
            lignes_tirees = df_filtre.sample(n=2)
            st.write("Deux interventions tirées au hasard :")
            st.dataframe(lignes_tirees)
        else:
            st.write("Pas assez de données pour tirer deux lignes au hasard.")
        
        # Graphique des répétitions
        df_graph = df_filtre.groupby(df_filtre[date_colonne]).size().reset_index(name='Répétitions')
        fig = px.bar(df_graph, x=date_colonne, y='Répétitions', title=f"Répétitions pour {operateur_selectionne}")
        st.plotly_chart(fig)
        
        try:
            fichier_resultat = f"resultat_par_{periode_selectionnee.lower()}.xlsx"
            df_resultat = charger_donnees(fichier_resultat)
            ligne_resultat = df_resultat[df_resultat['Prénom et nom'] == operateur_selectionne]
            if not ligne_resultat.empty:
                st.write(f"Données du fichier {fichier_resultat} pour {operateur_selectionne} :")
                st.dataframe(ligne_resultat)
            else:
                st.write(f"Aucune donnée trouvée pour {operateur_selectionne} dans {fichier_resultat}")
        except FileNotFoundError:
            st.write(f"Le fichier {fichier_resultat} n'a pas été trouvé.")

    if st.checkbox("Afficher toutes les données"):
        st.dataframe(df_principal)