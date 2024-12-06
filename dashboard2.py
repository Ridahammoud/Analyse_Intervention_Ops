import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from io import BytesIO
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px

# Fonction de chargement des données
@st.cache_data
def charger_donnees(fichier):
    return pd.read_excel(fichier)

# Fonction pour convertir un dataframe en fichier XLSX
def convert_df_to_xlsx(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Fonction pour appliquer des styles aux moyennes
def style_moyennes(df, top_n=3, bottom_n=5):
    moyenne_totale = df['Repetitions'].mean()

    df_top = df.nlargest(top_n, 'Repetitions')
    df_bottom = df.nsmallest(bottom_n, 'Repetitions')

    def apply_styles(row):
        if row.name in df_top.index:
            return ['background-color: gold; color: black'] * len(row)
        elif row.name in df_bottom.index:
            return ['background-color: lightcoral; color: white'] * len(row)
        elif row['Repetitions'] > moyenne_totale:
            return ['background-color: lightgreen'] * len(row)
        else:
            return ['background-color: lightpink'] * len(row)

    styled_df = df.style.apply(apply_styles, axis=1)
    return styled_df

# Fonction pour générer un PDF
def generate_pdf(df, filename="tableau.pdf"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.drawString(30, height - 40, "Tableau des répétitions des opérateurs")

    y_position = height - 60
    for i, row in df.iterrows():
        text = f"{row['Prénom et nom']} : {row['Repetitions']}"
        c.drawString(30, y_position, text)
        y_position -= 20

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse des Interventions", page_icon="📊", layout="wide")
st.title("📊 Analyse des interventions des opérateurs")

fichier_principal = st.file_uploader("Choisissez le fichier principal (donnee_Aesma.xlsx)", type="xlsx")

if fichier_principal is not None:
    df_principal = charger_donnees(fichier_principal)

    # Ajout du filtre par équipe
    equipes = ["Toutes les équipes", "Team 1 : Christian", "Team 2 : Hakim"]
    equipe_selectionnee = st.selectbox("Choisissez une équipe :", options=equipes)

    if equipe_selectionnee == "Team 1 : Christian":
        team_1 = [
            "Abdelaziz Hani Ddamir", "Aboubacar Tamadou", "Alhousseyni Dia"
            # Ajoutez tous les noms de la Team 1 ici
        ]
        df_principal = df_principal[df_principal['Prénom et nom'].isin(team_1)]
    elif equipe_selectionnee == "Team 2 : Hakim":
        team_2 = [
            "Abdoul Ba", "Aladji Sakho", "Amadou Sow"
            # Ajoutez tous les noms de la Team 2 ici
        ]
        df_principal = df_principal[df_principal['Prénom et nom'].isin(team_2)]

    col1, col2 = st.columns([2, 3])

    with col1:
        col_prenom_nom = df_principal.columns[4]
        col_date = df_principal.columns[6]

        operateurs = df_principal[col_prenom_nom].unique().tolist()
        operateurs.append("Total")
        operateurs_selectionnes = st.multiselect("Choisissez un ou plusieurs opérateurs", operateurs)

        if "Total" in operateurs_selectionnes:
            operateurs_selectionnes = df_principal[col_prenom_nom].unique().tolist()

        periodes = ["Jour", "Semaine", "Mois", "Trimestre", "Année"]
        periode_selectionnee = st.selectbox("Choisissez une période", periodes)

        df_principal[col_date] = pd.to_datetime(df_principal[col_date], errors='coerce')

        date_min = df_principal[col_date].min()
        date_max = df_principal[col_date].max()

        if pd.isna(date_min) or pd.isna(date_max):
            st.warning("Certaines dates dans le fichier sont invalides. Elles ont été ignorées.")
            date_min = date_max = None

        debut_periode = st.date_input("Début de la période", min_value=date_min, max_value=date_max, value=date_min)
        fin_periode = st.date_input("Fin de la période", min_value=debut_periode, max_value=date_max, value=date_max)

    if st.button("Analyser"):
        df_principal = df_principal.dropna(subset=[col_date])

        df_principal['Jour'] = df_principal[col_date].dt.date
        df_principal['Semaine'] = df_principal[col_date].dt.to_period('W').astype(str)
        df_principal['Mois'] = df_principal[col_date].dt.to_period('M').astype(str)
        df_principal['Trimestre'] = df_principal[col_date].dt.to_period('Q').astype(str)
        df_principal['Année'] = df_principal[col_date].dt.year

        df_graph = df_principal[(df_principal[col_date].dt.date >= debut_periode) & (df_principal[col_date].dt.date <= fin_periode)]

        groupby_cols = [col_prenom_nom]
        if periode_selectionnee != "Total":
            groupby_cols.append(periode_selectionnee)

        repetitions_graph = df_graph[df_graph[col_prenom_nom].isin(operateurs_selectionnes)].groupby(groupby_cols).size().reset_index(name='Repetitions')
        repetitions_tableau = df_principal[df_principal[col_prenom_nom].isin(operateurs_selectionnes)].groupby(groupby_cols).size().reset_index(name='Repetitions')

        with col2:
            # Graphique principal
            fig = go.Figure()

            for operateur in operateurs_selectionnes:
                df_operateur = repetitions_graph[repetitions_graph[col_prenom_nom] == operateur]
                fig.add_trace(go.Bar(x=df_operateur[periode_selectionnee],
                                     y=df_operateur['Repetitions'],
                                     name=operateur,
                                     text=df_operateur['Repetitions'],
                                     textposition='inside',
                                     hovertemplate='%{y}'))

            fig.update_layout(title=f"Nombre de rapports d'intervention (du {debut_periode} au {fin_periode})",
                              xaxis_title=periode_selectionnee,
                              yaxis_title="Répetitions",
                              template="plotly_dark")
            st.plotly_chart(fig)

        # Deuxième graphique des moyennes
        moyennes_par_periode = repetitions_graph.groupby([periode_selectionnee, col_prenom_nom])['Repetitions'].mean().reset_index()
        moyenne_globale = moyennes_par_periode['Repetitions'].mean()

        fig1 = go.Figure()

        colors = px.colors.qualitative.Set1
        for i, operateur in enumerate(operateurs_selectionnes):
            df_operateur_moyenne = moyennes_par_periode[moyennes_par_periode[col_prenom_nom] == operateur]
            fig1.add_trace(go.Scatter(
                x=df_operateur_moyenne[periode_selectionnee],
                y=df_operateur_moyenne['Repetitions'],
                mode='lines+markers',
                name=operateur,
                line=dict(color=colors[i % len(colors)]),
                text=df_operateur_moyenne['Repetitions'],
                textposition='top center'
            ))

        fig1.add_trace(go.Scatter(
            x=moyennes_par_periode[periode_selectionnee].unique(),
            y=[moyenne_globale] * len(moyennes_par_periode[periode_selectionnee].unique()),
            mode='lines',
            name='Moyenne Globale',
            line=dict(color='red', dash='dash'),
            hoverinfo='skip'
        ))

        fig1.update_layout(
            title=f"Moyenne des rapports d'interventions par opérateur ({periode_selectionnee}) avec ligne de moyenne globale",
            xaxis_title=periode_selectionnee,
            yaxis_title="Moyenne des rapports d'interventions",
            template="plotly_dark"
        )

        st.plotly_chart(fig1)

        # Tableaux
        col3, col4 = st.columns([2, 3])
        with col3:
            st.write("### Tableau des Moyennes par période et par opérateur")
            styled_df = style_moyennes(moyennes_par_periode)
            st.dataframe(styled_df, use_container_width=True)

        with col4:
            st.write("### Tableau des rapports d'intervention par période et par opérateur")
            st.dataframe(repetitions_tableau, use_container_width=True)
# Affichage des tableaux
        st.subheader("Tirage au sort de deux lignes par opérateur")
        df_filtre = df_principal[(df_principal[col_date].dt.date >= debut_periode) & (df_principal[col_date].dt.date <= fin_periode)]
        for operateur in operateurs_selectionnes:
            st.write(f"### Tirage pour {operateur}:")
            df_operateur = df_filtre[df_filtre[col_prenom_nom] == operateur]
            lignes_tirees = df_operateur.sample(n=min(2, len(df_operateur)))

            if not lignes_tirees.empty:
                for _, ligne in lignes_tirees.iterrows():
                    col_info, col_photo = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"""
                        **Date**: {ligne['Date et Heure début d\'intervention']}
                        **Opérateur**: {ligne['Prénom et nom']}
                        **Équipement**: {ligne['Équipement']}
                        **Localisation**: {ligne['Localisation']}
                        **Type de défaut**: {ligne['']}
                        **Problème**: {ligne['Technique'] if pd.notna(ligne['Technique']) else ligne['Opérationnel']}
                        """)

                    with col_photo:
                        if pd.notna(ligne['Photo']):
                            st.image(ligne['Photo'], width=200)
                        else:
                            st.write("Pas de photo disponible")
            else:
                st.write("Pas de données disponibles pour cet opérateur dans la période sélectionnée.")

        # Téléchargement des rapports
        st.subheader("Télécharger le tableau des rapports d'interventions")
        xlsx_data = convert_df_to_xlsx(repetitions_tableau)
        st.download_button(label="Télécharger en XLSX", data=xlsx_data, file_name="NombredesRapports.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.subheader("Télécharger le tableau des rapports d'interventions en PDF")
        pdf_data = generate_pdf(repetitions_tableau)
        st.download_button(label="Télécharger en PDF", data=pdf_data, file_name="tableau.pdf", mime="application/pdf")

    if st.checkbox("Afficher toutes les données"):
        st.dataframe(df_principal)
