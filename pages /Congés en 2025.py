import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta
import plotly.express as px

# Configuration de la page Streamlit
st.set_page_config(page_title="Calendrier des Congés 2025", layout="wide")
st.title("Calendrier des Congés 2025")

# Fonction pour charger les données depuis le fichier Excel
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        return None

    # Vérifier et renommer les colonnes si nécessaire
    expected_columns = ['Prénom et nom', 'Type', 'Type de congé', 'Début', 'Fin',
                        'Succursale', 'Position', 'Ressources', 'Total (h)', 'Note',
                        '# de la demande', 'Créée le', 'Approuvé à', 'Approbateur', 'Justification']
    if not all(col in df.columns for col in expected_columns):
        st.error("Les colonnes du fichier ne correspondent pas au format attendu.")
        return None

    return df

# URL du fichier Excel (Google Sheets exporté en .xlsx)
file_path = "https://docs.google.com/spreadsheets/d/1IO_1-v5i0IZQSF6UUfYEuKlTn6i-3hSI/export?format=xlsx"
df = load_data(file_path)

# Vérifier si le DataFrame a été chargé correctement
if df is None or df.empty:
    st.warning("Aucune donnée à afficher.")
    st.stop()

# Convertir les colonnes 'Début' et 'Fin' en format datetime
df['Début'] = pd.to_datetime(df['Début'], errors='coerce')
df['Fin'] = pd.to_datetime(df['Fin'], errors='coerce')

# Filtrer les congés pour l'année 2025
df = df[(df['Début'].dt.year == 2025) | (df['Fin'].dt.year == 2025)]

# Fonction pour créer un calendrier mensuel sous forme de grille
def create_month_grid(year, month, data):
    # Récupérer le premier jour du mois et le nombre de jours dans le mois
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    # Créer un calendrier avec les jours de la semaine (lundi, mardi, ... dimanche)
    days_in_month = [day for day in range(1, calendar.monthrange(year, month)[1] + 1)]
    weeks = calendar.monthcalendar(year, month)

    # Calculer les événements pour chaque jour du mois
    day_events = {day: 0 for day in days_in_month}
    for _, row in data.iterrows():
        start_date = row['Début']
        end_date = row['Fin']
        
        for day in pd.date_range(start=start_date, end=end_date, freq='D'):
            if day.year == year and day.month == month:
                day_events[day.day] += 1

    # Préparer les couleurs : rouge pour plus de 3 congés, vert pour 1-3 congés, gris pour aucun congé
    colors = []
    for day in days_in_month:
        if day_events[day] > 3:
            colors.append('red')
        elif day_events[day] > 0:
            colors.append('green')
        else:
            colors.append('gray')

    # Créer la grille avec Plotly
    fig = go.Figure()

    # Ajout des jours au calendrier
    for week_idx, week in enumerate(weeks):
        for day_idx, day in enumerate(week):
            if day != 0:  # Ignore les jours vides (0 représente un jour vide dans le mois)
                color = colors[day - 1]
                fig.add_trace(go.Scatter(
                    x=[day_idx], y=[week_idx],
                    mode='markers+text',
                    marker=dict(color=color, size=40),
                    text=[f"{day}\n{day_events[day]}"],
                    textposition="middle center",  # Correction ici pour que le texte soit au centre
                    hovertext=f"{calendar.day_name[day_idx]} {day} : {day_events[day]} congé(s)",
                    hoverinfo="text"
                ))

    # Mise en forme du graphique pour ressembler à un vrai calendrier
    fig.update_layout(
        title=f"Calendrier des Congés - {calendar.month_name[month]} {year}",
        xaxis=dict(
            tickvals=list(range(7)),
            ticktext=["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            title="Jours de la semaine",
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            tickvals=list(range(len(weeks))),
            ticktext=[f"Semaine {i+1}" for i in range(len(weeks))],
            title="Semaines",
            showgrid=False,
            zeroline=False,
        ),
        showlegend=False,
        plot_bgcolor="white",
        height=500,
        width=800,
    )

    return fig

# Affichage de l'interaction avec les mois et les années
month_select = st.selectbox("Choisir un mois", options=range(1, 13), format_func=lambda x: calendar.month_name[x])

# Créer le calendrier interactif pour le mois sélectionné
fig = create_month_grid(2025, month_select, df)

# Afficher le calendrier dans Streamlit
st.plotly_chart(fig)

# Détails du congé sélectionné
st.subheader("Détails des Congés")
selected_date = st.date_input("Sélectionner une date", min_value=datetime(2025, 1, 1), max_value=datetime(2025, 12, 31))
selected_day_conges = df[(df['Début'].dt.date <= selected_date) & (df['Fin'].dt.date >= selected_date)]

if selected_day_conges.empty:
    st.write(f"Aucun congé programmé pour le {selected_date}.")
else:
    for _, row in selected_day_conges.iterrows():
        st.write(f"**Nom**: {row['Prénom et nom']}")
        st.write(f"**Type de congé**: {row['Type de congé']}")
        st.write(f"**Justification**: {row['Justification']}")
        st.write(f"**Période**: {row['Début'].strftime('%Y-%m-%d')} à {row['Fin'].strftime('%Y-%m-%d')}")
        st.write("---")
