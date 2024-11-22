import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuration du style Streamlit
st.set_page_config(
    page_title="Analyse des Interventions",
    page_icon="📊",
    layout="wide"
)

# Style personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTitle {
        color: #2C3E50;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 30px;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def charger_donnees(fichier):
    df = pd.read_excel(fichier)
    return df

def filtrer_donnees(df, operateurs, date_colonne, date_debut, date_fin):
    df[date_colonne] = pd.to_datetime(df[date_colonne]).dt.date
    date_debut = pd.to_datetime(date_debut).date()
    date_fin = pd.to_datetime(date_fin).date()
    mask = (df['Prénom et nom'].isin(operateurs)) & (df[date_colonne] >= date_debut) & (df[date_colonne] <= date_fin)
    return df[mask]

def analyse_statistiques(df_filtre, operateurs):
    # Création de métriques détaillées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📅 Période analysée", 
            value=f"{df_filtre[date_colonne].min()} au {df_filtre[date_colonne].max()}"
        )
    
    with col2:
        st.metric(
            label="👥 Nombre d'opérateurs", 
            value=len(operateurs)
        )
    
    with col3:
        st.metric(
            label="🔢 Total des interventions", 
            value=len(df_filtre)
        )

def creation_graphique_avance(df_graph):
    # Graphique interactif avec Plotly
    fig = go.Figure()
    
    # Ajout de traces pour chaque opérateur
    for operateur in df_graph['Prénom et nom'].unique():
        df_op = df_graph[df_graph['Prénom et nom'] == operateur]
        fig.add_trace(go.Scatter(
            x=df_op[date_colonne], 
            y=df_op['Répétitions'],
            mode='lines+markers',
            name=operateur,
            line=dict(width=3),
            marker=dict(size=10)
        ))
    
    # Personnalisation du layout
    fig.update_layout(
        title={
            'text': "Comparaison détaillée des interventions",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center', 
            'yanchor': 'top',
            'font': dict(size=20)
        },
        xaxis_title="Date",
        yaxis_title="Nombre d'interventions",
        legend_title="Opérateurs",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Interface principale
st.title("🚀 Tableau de Bord des Interventions")

# Reste du code précédent...
# (Gardez la logique de chargement et de filtrage des données)

# Après le filtrage des données
if st.button("Analyser") and operateurs_selectionnes:
    # Filtrage des données
    df_filtre = filtrer_donnees(df_principal, operateurs_selectionnes, date_colonne, date_debut, date_fin)
    
    # Section des statistiques
    st.header("📊 Statistiques Générales")
    analyse_statistiques(df_filtre, operateurs_selectionnes)
    
    # Graphique avancé
    st.header("📈 Visualisation des Interventions")
    df_graph = df_filtre.groupby([df_filtre[date_colonne], 'Prénom et nom']).size().reset_index(name='Répétitions')
    creation_graphique_avance(df_graph)
    
    # Détails supplémentaires
    st.header("🔍 Détails des Interventions")
    for operateur in operateurs_selectionnes:
        st.subheader(f"Détails pour {operateur}")
        df_op = df_filtre[df_filtre['Prénom et nom'] == operateur]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre d'interventions", len(df_op))
        
        with col2:
            if len(df_op) >= 2:
                lignes_tirees = df_op.sample(n=2)
                st.write("Deux interventions tirées au hasard :")
                st.dataframe(lignes_tirees)
