from re import X
from turtle import color
import streamlit as st
from PIL import Image
import os
import pandas as pd
import itertools
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pandas as pd
import streamlit as st
import pylab as pl
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import plotly.express as px
import matplotlib
import matplotlib.pyplot as plt


###### CODE CMD
#cd.ipython
#streamlit run viz_projet_2.py

# toute la largeur de la page
st. set_page_config(layout="wide")


# Image
col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2 :
    st.image("movies-1.jpg", width = 550)
with col3:
    st.write("")


# Titre / intro
st.markdown("<h1 style='text-align: center; color: blue;'>df.projet_ </h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: blue;'>Analyse des données du Projet 2 </h1>", unsafe_allow_html=True)

st.subheader("Objectif :")
st.subheader("Analyser les données des films sortis au cinéma entre 1940 et 1990, disponibles sur le site IMDb, dans le but de connaitre les caractéristiques de ces films et s'appuyer sur ces caractéristiques pour compléter l'offre dans le futur")


# multipage
col1, col2 = st.columns(2)
with col1:
    page = st.selectbox("Choisissez votre page", ["1. Préparation du jeux de données", "2. Modélisation des données", "3. Conclusion"]) 
with col2 :
    st.write("")

if page == "1. Préparation du jeux de données":
    st.subheader('1. Préparation du jeux de données')
    st.write("=>  Nettoyage & filtres")
    st.write("=>  Sélection des données suivantes :")
    st.write(   "      - Titre du film")
    st.write(   "      - La durée du film")
    st.write(   "      - Genre du film")
    st.write(   "      - Année de sortie du film")
    st.write(   "      - Actrices, acteurs et réalisateurs")
    st.write(   "      - Note du public (sur 10)")


   
elif page == "2. Modélisation des données":
    st.subheader('2. Modélisation des données')
    st.write("À partir de ces données, nous avons tracé des graphiques que les librairies Pandas, Matplotlib, Seaborn permettent.")

    ## GRAPH 1 - CARTOGRAPHIE DES OEUVRES PAR DECENIES
    st.write("1. Nombre d'oeuvres par décénnies => nombre d'oeuvres total 15048")

    path_file = os.path.join("c:\\", 'Users', 'celin', 'Downloads','title_abr.tsv')
    path_file = os.path.normpath(path_file)
    title_abr = pd.read_csv(path_file, sep="\t")

    # 1er filtre sélection de la période : 1940 à 1990 (bornes inclusives)
    title_abr = title_abr[(title_abr['startYear'] >= 1940) & (title_abr['startYear'] <= 1990)] 
    print(f'filtre 1 (by years): {title_abr.shape[0]}')

    # 2ème filtre : les genres
    title_abr['titleType'].unique() # sélection des types : movies et tvMovie
    title_abr = title_abr[title_abr['titleType'].isin(['movie', 'tvMovie'])]
    print(f'filtre 2 (by type): {title_abr.shape[0]}')

    # 3ème filtre : filmes avec un minimum d'avis (min : 1er quartile)
    title_abr = title_abr[title_abr['numVotes'].notna()]
    print(f'filtre (without votes): {title_abr.shape[0]}')

    quartile_1 = np.quantile(title_abr['numVotes'], 0.25) # 67 avis minimum
    title_abr = title_abr[title_abr['numVotes'] >= quartile_1]
    print(f'filtre 3 (by votes): {title_abr.shape[0]}')

    # 4ème filtre : films avec un rating minimum (min: 1er quartile) # rating de 5.6 minimum
    title_abr = title_abr[title_abr['averageRating'].notna()]
    print(f'filtre (without rating): {title_abr.shape[0]}')

    quartile_1 = np.quantile(title_abr['averageRating'], 0.25)
    title_abr = title_abr[title_abr['averageRating'] >= quartile_1]
    print(f'filtre 4 (by rating): {title_abr.shape[0]}')

    # fonction pour regrouper les années
    def decennie(list_year):
        gen_list = []
        for x in list_year:
            if x == np.nan:
                gen_list.append('unknown')
            elif (x >= 1940) and (x < 1950):
                gen_list.append('40\'s')
            elif x < 1960:
                gen_list.append('50\'s')
            elif x < 1970:
                gen_list.append('60\'s')
            elif x < 1980:
                gen_list.append('70\'s')
            elif x <= 1990:
                gen_list.append('80\'s')
                
        return gen_list

    title_abr['generation'] = decennie(title_abr['startYear'])
    title_abr.sort_values('generation', ascending=True, inplace=True)
    title_abr['generation'].value_counts()

    # graphique pie
    labels = "40's = 1969","50's = 2955","60's = 3093","70's = 3335","80's = 3696"
    sizes = [1969,2955,3093,3335,3696]
    explode = (0,0,0,0,0.1)
    colors = sns.color_palette('pastel')[0:5]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  
    st.pyplot(fig1)


    ## GRAPHIQUE 2 - Répartition des genres par décénnies

    # import index_genres
    path_file = os.path.join("c:\\", 'Users', 'celin', 'Downloads','index_genres.tsv')
    path_file = os.path.normpath(path_file)
    index_genres = pd.read_csv(path_file, sep="\t")
    full_gen = pd.merge(title_abr, index_genres, how='left', on='tconst')


    # Calcul de la moyenne pondérée par genre
    total_vote = full_gen['numVotes'].sum()
    full_gen['sumVotes'] = full_gen.apply(lambda row: row['averageRating'] * row['numVotes'], axis=1)
    full_gen.rename(columns={'tconst':'tconst','titleType':'titleType', 'title': 'title','averageRating':'averageRating', 'numVotes':'numVotes', 'isAdult':'isAdult','startYear':'startYear' , 'runtimeMinutes':'runtimeMinutes', 'genres_x':'genres_x', 'generation':'generation', 'genres_y':'genres','sumVotes':'sumVotes'}, inplace=True)
    total_vote = full_gen['numVotes'].sum()

    pivot_gen = pd.pivot_table(full_gen, index='genres', values=['numVotes','sumVotes'], aggfunc=np.sum).reset_index()
    pivot_gen['avg_pond_g'] = pivot_gen.apply(lambda row: row['sumVotes'] / row['numVotes'], axis=1)
    pivot_gen['avg_pond_t'] = pivot_gen.apply(lambda row: row['sumVotes'] * row['avg_pond_g'] / total_vote, axis=1)

    pivot_gen['rank'] = pivot_gen['avg_pond_t'].rank(ascending=False) 
    pivot_gen.sort_values('rank', ascending=True, inplace=True)
    pivot_gen = pivot_gen.reindex(columns=['rank', 'genres', 'numVotes', 'generation','sumVotes', 'avg_pond_g', 'avg_pond_t']).reset_index(drop=True)
    top10 = pivot_gen[pivot_gen['rank'] <= 10]

    # 2 graphiques
    st.write("2. Répartition des genres par décénnies")

    # Hist plot genres/generations
    fig, ax = plt.subplots(figsize = (10, 10))
    ax = plt.subplot()
    viz_correlation = sns.histplot(full_gen,x="generation", hue="genres",multiple="stack")
    st.write(f'Genres par génération')
    viz_correlation =plt.xlabel("Générations de 1940 à 1990", fontsize=10)  
    viz_correlation =plt.ylabel("Nombres de films par genre", fontsize=10)
    viz_correlation = sns.move_legend(ax, bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    st.pyplot(fig)

    st.write(" Les Meilleurs genres par génération en fonction des notes des films" )

    # Subplot genres/generations/rating
    col_choice = st.selectbox(label='Choissez une génération', options= full_gen.generation.unique())
    new_df = full_gen[full_gen.generation == col_choice]
    fig, ax = plt.subplots(figsize=(30,30))
    fig=px.bar(new_df,x = 'genres', y='averageRating',color="genres")
    st.plotly_chart(fig)

    ## GRAPHIQUE 3
    st.write("3. Actrices / Acteurs ")

    #### TOP 10 des acteurs (avg pondérée)
    # import name_bas_f
    path_file = os.path.join("c:\\", 'Users', 'celin', 'Downloads','name_bas_f.tsv')
    name_bas_f = pd.read_csv(path_file, sep='\t')
    name_bas_f.head(3)
    # import title_prin
    path_file = os.path.join("c:\\", 'Users', 'celin', 'Downloads','title_prin.tsv')
    title_prin = pd.read_csv(path_file, sep='\t')
    title_prin.head(3)
    # import index_prof
    path_file = os.path.join("c:\\", 'Users', 'celin', 'Downloads','index_prof.tsv')
    index_prof = pd.read_csv(path_file, sep='\t')
    index_prof.head(3)
    # Récupérer les films populaires sur Imdb
    # Récupérer les id des films puis identifier les acteurs qui ont joué dedans et proposer les films knownForTitles les mieux notés (idem pour les réalisateurs ?)
    full_dir = pd.merge(title_abr, title_prin, how='left', on='tconst')
    full_dir = pd.merge(full_dir, name_bas_f, how='left', on='nconst')
    full_dir.drop(columns=['titleType', 'runtimeMinutes', 'characters', 'primaryProfession', 'knownForTitles'], inplace=True)
    full_dir = full_dir.reindex(columns=['tconst', 'title', 'genres', 'averageRating', 'numVotes', 'startYear', 'generation', 'isAdult', 'nconst',	'category', 'primaryName',	'birthYear', 'deathYear'])
    full_dir.head()
    # Filtre sur les acteurs, actrices 
    print(f'taille de l\'échantillon : {full_dir.shape[0]}')
    full_act = full_dir[full_dir['category'].isin(['actress', 'actor'])]
    full_act1 = full_dir[full_dir['category'].isin(['actress'])]
    full_act2 = full_dir[full_dir['category'].isin(['actor'])]

    # Contrôler des valeurs nulles 
    full_act['primaryName'].isna().value_counts() # 138 NaN
    full_act = full_act[full_act['primaryName'].isna() == False]
    print(f'filtre sur les valeurs non nulles : {full_act.shape[0]}')
    full_act.head()


    ## WORDCLOUD Actrices / acteurs les plus présentes
    st.write(f'Actrices les plus présententes dans le jeux de données')


    new_df = Counter(full_act1.primaryName.values)
    fig = plt.figure(figsize=(10, 10))
    ax2 = plt.subplot(222) 

    wordcloud = WordCloud(collocations = False,colormap= 'gist_rainbow_r',width=500, height=80, background_color = 'white',max_font_size=100, prefer_horizontal = 0.9, min_font_size=4)
    wordcloud.generate_from_frequencies(dict(new_df.most_common(5)))
    fig, ax = plt.subplots(figsize=(2,2))
    wordcloud=ax.imshow(wordcloud, interpolation="bilinear")
    wordcloud=plt.axis("off")
    wordcloud=plt.margins(x=0, y=0)
    st.pyplot(fig)


    st.write(f'Acteurs les plus présent dans le jeux de données')
    fig = plt.figure(figsize=(10, 10))
    ax2 = plt.subplot(222) 

    full_act2 = full_act[full_act['primaryName'].isnull() == False]

    full_act2 = full_act[full_act['primaryName'].isnull() == False]
    resultat = Counter(full_act2.primaryName.values)

    wordcloud = WordCloud(collocations = False, colormap= 'rainbow', width=500, height=80, background_color = 'white', max_font_size=100, prefer_horizontal = 0.9, min_font_size=4)
    wordcloud.generate_from_frequencies(dict(resultat.most_common(5)))
    fig, ax = plt.subplots(figsize=(2,2))
    wordcloud=ax.imshow(wordcloud, interpolation="bilinear")
    wordcloud=plt.axis("off")
    wordcloud=plt.margins(x=0, y=0)
    st.pyplot(fig)

    ## HISTPLOT DE LA REPARTITION DES ACTEURS/ACTRICES PAR GENERATION
    st.write(f'Acteurs-Actrices / génération')

    full_act['generation'] = decennie(full_act['startYear'])
    full_act.sort_values('generation', ascending=True, inplace=True)
    full_act['generation'].value_counts()
    full_act1['generation'] = decennie(full_act1['startYear'])
    full_act1.sort_values('generation', ascending=True, inplace=True)
    full_act1['generation'].value_counts()
    full_act2['generation'] = decennie(full_act2['startYear'])
    full_act2.sort_values('generation', ascending=True, inplace=True)
    full_act2['generation'].value_counts()


    fig, ax = plt.subplots(figsize=(7, 5))
    ax = plt.subplot()

    full_act2 = full_dir[full_dir['category'].isin(['actor'])]
    viz_correlation =sns.histplot(data=full_act2, x='generation', color="pink")
    full_act1 = full_dir[full_dir['category'].isin(['actress'])]
    viz_correlation =sns.histplot(data=full_act1, x='generation', color="powderblue")


    plt.legend(labels=["Acteurs","actrices"])
    ax.set_ylabel('Nombre d\'actrices d\'acteurs')
    ax.set_xlabel('Générations')
    plt.title('Actrices/Acteurs selon les générations', fontsize=16)
    st.pyplot(fig)

    ## GRAPHIQUE 5
    ## 5. Correlation du nombre de votes par notes

    file_path = os.path.join("c:\\", 'Users', 'celin', 'Downloads', 'title.ratings.tsv.gz')
    fix_path = os.path.normpath(file_path)
    title_rate=pd.read_csv(file_path, sep="\t")
    full_gen = pd.merge(title_abr, title_rate, how='left', on='tconst')
    full_gen.drop(columns=['averageRating_y','numVotes_y' ], inplace=True)
    full_gen.rename(columns={'tconst':'tconst','titleType':'titleType', 'title': 'title','averageRating_x':'notes', 'numVotes_x':'nombre_de_votes', 'isAdult':'films_pour_adultes','startYear':'date_de_sortie' , 'runtimeMinutes':'durée_des_films', 'genres_x':'genres', 'generation':'generation', 'genres_y':'genres','sumVotes':'sumVotes'}, inplace=True)

    st.write("4. Visualisation des correlations")

    fig = plt.figure(figsize=(10, 10))
    ax1 = plt.subplot(221) 
    st.write(f'Nombres notes par votes')
    ax1 = sns.regplot(x="notes",y = "nombre_de_votes", data = full_gen)
    ax1 =plt.xlabel("Notes de 6 à 10", fontsize=10)  
    ax1 =plt.ylabel("Nombres de votes", fontsize=10)
    ax1= plt.xlim(6,9, 0.2)
    ax1= plt.xticks([6,7,8,9])
    ax1= plt.ylim(0,200000)
    st.pyplot(fig)


    fig = plt.figure(figsize=(10, 10))
    ax2 = plt.subplot(222) 
    annot=True
    st.write(f'Correlation entre les données')
    ax2 =sns.heatmap(full_gen.corr(),annot=annot, center=0.5,cmap="BuPu")
    st.pyplot(fig)

    ## 6. Durée / génération et Durée / averagerating
    st.write("5. Analyse de la durée des films")

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.color_palette("YlOrBr", as_cmap=True)
    sns.boxenplot(ax=ax, data=full_gen, x="generation", y="durée_des_films")
    st.pyplot(fig)

    st.write("7. Analyse de la durée par note")

    fig=plt.figure(figsize=(10, 10))
    fig=sns.jointplot(data= full_gen,x='notes', y="durée_des_films")
    st.pyplot(fig)

    # st.write("8. Analyse des notes par rapport au nombre de votes")

    # fig2 = plt.figure(figsize=(10, 10))
    # fig2=sns.jointplot(data=full_gen, x='notes', y="nombre_de_votes")
    # st.pyplot(fig2)




if page == "3. Conclusion":
    st.write("Conclusion")
    st.write("La préparation, la modélisation statistique, la visualisation des données avec une grande variété de graphique, ont permis de représenter une vue globale des films sortis au cinéma entre 1940 et 1990.")

    st.write ("L’interprétation de ces graphiques met en avant les éléments suivants :")
    st.write ("* Le nombre de films augmente de génération en génération, ")
    st.write ("* Les drames, les comédies et les fimms de romance sont les plus présents dans le jeux de données et les mieux notés par le public,")
    st.write ("* Bette Davis et John Ways sont le nom de l'actrice et de l'acteur qui reviennent le plus souvent,")
    st.write ("* Plus d'acteurs que d'actrices sont présent pour chaque générations,")
    st.write ("* Les notes et le nombre de votes ne sont pas correlés,")
    st.write ("* Il n'y a pas de correlations non plus entre les dates de sortie, les durées des films et les films pour adultes,")
    st.write ("* Les films durent 100 minutes en moyenne,")
    st.write ("* Pour qu'un film soit bien noté, il doit durer entre 60 et 200 minutes.")

