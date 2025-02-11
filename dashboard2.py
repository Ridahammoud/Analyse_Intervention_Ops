import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from io import BytesIO
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px
import os

# Fonction de chargement des données
@st.cache_data
def charger_donnees(fichier):
    return pd.read_excel(fichier)

team_1_Christian = ["Abdelaziz HANI DDAMIR", "Aboubacar TAMADOU", "Alhousseyni DIA", "Berkant INCE",
    "Boubakar Sidiki OUEDRAGO", "Boubou GASSAMA", "Chamsoudine ABDOULWAHAB", "Dagobert EWANE JENE",
    "Dione MBAYE", "Doro DIAW", "Enrique AGUEY - ZINSOU", "Fabien PREVOST", "Fabrice NELIEN",
    "Idrissa YATERA", "Jabbar ARSHAD", "Jacques-Robert BERTRAND", "Karamoko YATABARE",
    "Mahamadou NIAKATE", "Mamadou BAGAYOGO", "Mamadou  KANE Team 1", "Mohamed Lamine SAAD", "Moussa SOUKOUNA",
    "Pascal NOUAGA", "Rachid RAMDANE", "Taha HSINE", "Tommy Lee CASDARD", "Volcankan INCE",
    "Youssef MEZOUAR", "Youssouf WADIOU", "Elyas BOUZAR", "Reda JDI"]

team_2_Hakim =["Abdoul BA", "Aladji SAKHO", "Amadou SOW", "Arfang CISSE", "Bouabdellah AYAD",
    "Cheickne KEBE", "Dany CHANTRE", "David DIOCKOU N'DIAYE", "Dylan BARON", "Fabien TSOP NANG",
    "Fabrice BADIBENGI", "Faker AJILI", "Fodie KOITA CAMARA", "Gaetan GIRARD", "Idy BARRO",
    "Aboubacar CISSE", "Johnny MICHAUD", "Ladji BAMBA", "Mamadou FOFANA", "Mamadou KANE Team 2",
    "Mamadou SANGARE", "Mamadou SOUMARE", "Mohamed BOUCHLEH", "Mostefa MOKHTARI", "Nassur IBRAHIM",
    "Riadh MOUSSA", "Saim Haroun BHATTI", "Samir CHIKH", "Tony ALLOT", "Walter TAVARES","Mishal ABOUL KALAM"]

team_exclus = ["Abdelaziz Hani Ddamir", "Aboubacar Tamadou", "Alhousseyni Dia", "Berkant Ince",
    "Boubakar Sidiki Ouedrago", "Boubou Gassama", "Chamsoudine Abdoulwahab", "Dagobert Ewane Jene",
    "Dione Mbaye", "Doro Diaw", "Enrique Aguey - Zinsou", "Fabien Prevost", "Fabrice Nelien",
    "Idrissa Yatera", "Jabbar Arshad", "Jacques-Robert Bertrand", "Karamoko Yatabare",
    "Mahamadou Niakate", "Mamadou Bagayogo", "Mamadou  Kane", "Mohamed Lamine Saad", "Moussa Soukouna",
    "Pascal Nouaga", "Rachid Ramdane", "Taha Hsine", "Tommy Lee Casdard", "Volcankan Ince",
    "Youssef Mezouar", "Youssouf Wadiou", "Elyas Bouzar", "Reda Jdi","Abdoul Ba", "Aladji Sakho", "Amadou Sow", "Arfang Cisse", "Bouabdellah Ayad",
    "Cheickne Kebe", "Dany Chantre", "David Diockou N'Diaye", "Dylan Baron", "Fabien Tsop Nang",
    "Fabrice Badibengi", "Faker Ajili", "Fodie Koita Camara", "Gaetan Girard", "Idy Barro",
    "Aboubacar Cisse", "Johnny Michaud", "Ladji Bamba", "Mamadou Fofana", "Mamadou Kane",
    "Mamadou Sangare", "Mamadou Soumare", "Mohamed Bouchleh", "Mostefa Mokhtari", "Nassur Ibrahim",
    "Riadh Moussa", "Saim Haroun Bhatti", "Samir Chikh", "Tony Allot", "Walter Tavares"]
# Ajouter une colonne pour les équipes
def assign_team(name):
    if name in team_1_Christian:
        return "Team 1 Christian"
    elif name in team_2_Hakim:
        return "Team 2 Hakim"
    else:
        return "Non assigné"

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


    with col1:
        col_prenom_nom = df_principal.columns[4]
        col_date = df_principal.columns[6]

        operateurs = df_principal[col_prenom_nom].unique().tolist()
        teams = df_principal['Team'].unique().tolist()     
        teams.insert(0, "Team")

        selection_type = st.selectbox("Sélectionner par", ["Opérateur", "Team"])
        if selection_type == "Opérateur":
            operateurs_selectionnes = st.multiselect("Choisissez un ou plusieurs opérateurs", operateurs)
            if "Total" in operateurs_selectionnes:
                operateurs_selectionnes = df_principal[col_prenom_nom].unique().tolist()
        else:
            teams_selectionnes = st.multiselect("Choisissez une ou plusieurs teams", teams)
            if "Team 1 Christian" in teams_selectionnes:
                df_principal = df_principal[df_principal['Team']=='Team 1 Christian']
                teams_selectionnes = df_principal['Prénom et nom'].unique().tolist()
                operateurs_selectionnes = df_principal[df_principal['Prénom et nom'].isin(teams_selectionnes)]['Prénom et nom'].unique().tolist()
            elif "Team 2 Hakim" in teams_selectionnes:
                df_principal = df_principal[df_principal['Team']=='Team 2 Hakim']
                teams_selectionnes = df_principal['Prénom et nom'].unique().tolist()
                operateurs_selectionnes = df_principal[df_principal['Prénom et nom'].isin(teams_selectionnes)]['Prénom et nom'].unique().tolist()
 
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

        nombre_lignes = st.slider("Nombre de lignes à tirer au sort", min_value=1, max_value=10, value=2)

    if st.button("Analyser"):
        df_principal = df_principal.dropna(subset=[col_date])
        df_principal['Jour'] = df_principal[col_date].dt.date
        df_principal['Semaine'] = df_principal[col_date].dt.to_period('W').astype(str)
        df_principal['Mois'] = df_principal[col_date].dt.to_period('M').astype(str)
        df_principal['Trimestre'] = df_principal[col_date].dt.to_period('Q').astype(str)
        df_principal['Année'] = df_principal[col_date].dt.year

        df_graph = df_principal[(df_principal[col_date].dt.date >= debut_periode) & (df_principal[col_date].dt.date <= fin_periode)]
        df_graph = df_graph[df_graph['Prénom et nom'].isin(operateurs_selectionnes)]

        groupby_cols = [col_prenom_nom]
        if periode_selectionnee != "Total":
            groupby_cols.append(periode_selectionnee)

        repetitions_graph = df_graph.groupby(groupby_cols).size().reset_index(name='Repetitions')
        repetitions_tableau = df_principal[df_principal['Prénom et nom'].isin(operateurs_selectionnes)].groupby(groupby_cols).size().reset_index(name='Repetitions')

        with col2:
            # Graphique principal (barres)
            fig = go.Figure()
            for operateur in operateurs_selectionnes:
                df_operateur = repetitions_graph[repetitions_graph[col_prenom_nom] == operateur]
                fig.add_trace(go.Bar(x=df_operateur[periode_selectionnee], y=df_operateur['Repetitions'], name=operateur, text=df_operateur['Repetitions'], textposition='inside', hovertemplate='%{y}'))

            fig.update_layout(title=f"Nombre de rapports d'intervention (du {debut_periode} au {fin_periode})", xaxis_title=periode_selectionnee, yaxis_title="Répetitions", template="plotly_dark")
            st.plotly_chart(fig)

            # Calcul des moyennes par opérateur et par période
            moyennes_par_periode = repetitions_graph.groupby([periode_selectionnee, col_prenom_nom])['Repetitions'].mean().reset_index()
            col_prenom_nom_exclus = df_principal[df_principal['Prénom et nom'].isin(team_exclus)].columns[4]
            moyennes_par_periode_exclus = repetitions_graph.groupby([periode_selectionnee, col_prenom_nom_exclus])['Repetitions'].mean().reset_index()
            moyennes_par_operateur = moyennes_par_periode.groupby(['Prénom et nom'])['Repetitions'].mean().reset_index()
            moyenne_globale = moyennes_par_operateur['Repetitions'].mean()           
            par_mois = df_principal.groupby(['Prénom et nom', 'Mois']).size().reset_index(name='Repetitions_Mois')
            df_moyenne = df_principal.groupby(groupby_cols).size().reset_index(name='Repetitions')
            moy_Mensuel = par_mois.groupby(['Prénom et nom']).mean('Repetitions_Mois')
            moy_Mensuel = moy_Mensuel.reset_index()
            moy_Mensuel = moy_Mensuel[moy_Mensuel['Prénom et nom'].isin(team_exclus)]
            moy_Mensuel['Repetitions_Mois'] = pd.to_numeric(moy_Mensuel['Repetitions_Mois'], errors='coerce')
            moyenne_total = df_moyenne['Repetitions'].mean()

# Affichage des graphiques et tableaux côte à côte

        col_graph, col_tableau = st.columns(2)
        with col_graph:
            fig1 = go.Figure()
            colors = px.colors.qualitative.Set1
            # Ligne de moyenne globale
            fig1.add_trace(go.Scatter(
                x=moyennes_par_periode[periode_selectionnee].unique(),
                y=[moyenne_total] * len(moyennes_par_periode[periode_selectionnee].unique()),
                mode='lines',
                name='Moyenne Globale',
                line=dict(color='red', dash='dash'),
                hoverinfo='skip'
            ))
            fig1.add_trace(go.Scatter(
                x=moyennes_par_periode[periode_selectionnee].unique(),
                y=[moyenne_globale] * len(moyennes_par_periode[periode_selectionnee].unique()),
                mode='lines',
                name='Moyenne Ops Selectionnés',
                line=dict(color='green', dash='dash'),
                hoverinfo='skip'
            ))
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
            fig1.update_layout(
                title=f"Moyenne des rapports d'interventions par opérateur ({periode_selectionnee})",
                xaxis_title=periode_selectionnee,
                yaxis_title="Moyenne des rapports d'interventions",
                template="plotly_dark"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_tableau:
            st.write("### Tableau des Moyennes par opérateur")
            styled_df = style_moyennes(moyennes_par_operateur)
            st.dataframe(styled_df, use_container_width=True)
            st.markdown("""
            **Légende :**
            - <span style='background-color: gold; color: black; padding: 2px 5px;'>Top 3</span>
            - <span style='background-color: lightgreen; padding: 2px 5px;'>Supérieur à la moyenne</span>
            - <span style='background-color: lightpink; padding: 2px 5px;'>Inférieur à la moyenne</span>
            - <span style='background-color: lightcoral; color: white; padding: 2px 5px;'>Flop 5</span>
            """, unsafe_allow_html=True)

        # Affichage des tableaux
        st.markdown(f"### La Moyenne des Opérateurs selectionnés par {periode_selectionnee} est : {moyenne_globale}")
        st.markdown(f"### La Moyenne Globale des rapports d'intervention par {periode_selectionnee} est : {moyenne_total}")
        st.write("### Tableau des rapports d'intervention par période et par opérateur")
        st.dataframe(repetitions_tableau, use_container_width=True)

        # Affichage des tableaux
        # Assurez-vous que le chemin est correct et relatif au script
        script_dir = os.path.dirname(__file__)
        st.subheader(f"Tirage au sort de {nombre_lignes} lignes par opérateur")
        df_filtre = df_principal[(df_principal[col_date].dt.date >= debut_periode) & (df_principal[col_date].dt.date <= fin_periode)]

        for operateur in operateurs_selectionnes:
            st.write(f"### Tirage pour {operateur}:")
            df_operateur = df_filtre[df_filtre[col_prenom_nom] == operateur]
            lignes_tirees = df_operateur.sample(n=min(nombre_lignes, len(df_operateur)))
            if not lignes_tirees.empty:
                for _, ligne in lignes_tirees.iterrows():
                    col_info, col_photo = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"""
                        **Date**: {ligne['Date et Heure début d\'intervention']}
                        **Opérateur**: {ligne['Prénom et nom']}
                        **Équipement**: {ligne['Équipement']}
                        **Localisation**: {ligne['Localisation']}
                        **Type de défaut**: {'Technique' if pd.notna(ligne['Technique']) else 'Opérationnel'}
                        **Problème**: {ligne['Technique'] if pd.notna(ligne['Technique']) else ligne['Opérationnel']}
                        """)
                        with col_photo:
                            if pd.notna(ligne['Photo']):
                                if ligne['Photo'].startswith('http'):
                                    st.image(ligne['Photo'], width=200)
                                else:
                                    # Si ce n'est aps une URL, assurez que le chemin est correct
                                    image_path = ligne['Photo']
                                    if not os.path.isabs(image_path):
                                        image_path = os.path.join(script_dir, image_path)
                                        try:
                                            st.image(image_path, width=200)
                                        except Exception as e:
                                            st.error(f"Erreur de chargement de l'image : {e}")
                                    else:
                                        st.write("Pas de photo disponible")
                            else:
                                st.write("Pas de données disponibles pour cet opérateur dans la période sélectionnée.")
