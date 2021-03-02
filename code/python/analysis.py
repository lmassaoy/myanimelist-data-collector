import json
import streamlit as st
import pandas as pd
from pandasql import sqldf
import numpy as np
import altair as alt
from PIL import Image
from os import listdir
from os.path import isfile, join
from datetime import datetime
import matplotlib.pyplot as plt
from utils.images_downloader import ImageRenderDownloader
from random import randint


def session_break(times):
    for i in range(times):
        st.write('')


def generate_donut_chart(agg_column):
    plt.figure(figsize=(5,10))
    grouped_df = joined_df[[agg_column,'id']]\
                    .groupby(agg_column,as_index=False)\
                    .agg('count')
    
    cmap = plt.get_cmap("tab20c")
    outer_colors = cmap(np.arange(3)*4)
    labels = grouped_df[agg_column].values
    sizes = grouped_df['id'].values

    plt.pie(
        sizes,
        labels=labels,
        colors=outer_colors,
        wedgeprops=dict(width=0.3, edgecolor='w'),
        autopct='%1.1f%%'
    )
            
    centre_circle = plt.Circle((0,0),0.80,color='white', fc='white',linewidth=1.25)
    
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    return fig


def concatened_json_files(path):
    directory_path = path
    concatenated_file = []
    file_counter = 0

    file_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]

    for file in file_list:
        file_counter+=1
        with open(f'{directory_path}{file}') as f:
            for obj in json.load(f):
                concatenated_file.append(obj)

    return concatenated_file


def build_image(path):
    return Image.open(path)


# Images
title = 'devops/volume/images/streamlit-title-img.png'

# Framework setup
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 0)
st.set_page_config(layout="wide")

# Data import
pysqldf = lambda q: sqldf(q, globals())

# @st.cache
def generate_datasets():  
    animes_df = pd.read_parquet('devops/volume/datasets/anime/enhanced_data/prepared_animes.parquet')
    genres_df = pd.read_parquet('devops/volume/datasets/anime/enhanced_data/animes_genres.parquet')
    animes_list = concatened_json_files('devops/volume/datasets/anime/raw_data/')
    return animes_df, genres_df, animes_list

animes_df, genres_df, animes_list = generate_datasets()

result_list = []
for obj in animes_list:
    for value in obj['details']['Genres']:
        result_list.append(value)
genres_list = list(set(result_list))


# Sidebar

st.sidebar.title("Navigation")
st.sidebar.header("Filters")

search_by_name_expander = st.sidebar.beta_expander("Search by Name", expanded=False)
with search_by_name_expander:
    search_by_name_text = st.text_input(label='Type the title of a anime')

score_expander = st.sidebar.beta_expander("Score", expanded=False)
with score_expander:
    score_col1, score_col2  = st.beta_columns((8,1))
    with score_col1:
        score_slider = st.slider(label='Select a range of score',min_value=0.0,max_value=10.0,value=(0.0, 10.0))

ranked_expander = st.sidebar.beta_expander("Rank", expanded=False)
with ranked_expander:
    rank_col1, rank_col2  = st.beta_columns((8,1))
    with rank_col1:
        min_rank = int(animes_df['details.Ranked'].min())
        max_rank = int(animes_df['details.Ranked'].max())
        rank_slider = st.slider(label='Select a range of rank',min_value=min_rank,max_value=max_rank,value=(min_rank,max_rank))

popularity_expander = st.sidebar.beta_expander("Popularity", expanded=False)
with popularity_expander:
    popularity_col1, popularity_col2  = st.beta_columns((8,1))
    with popularity_col1:
        min_rank = int(animes_df['details.Popularity'].min())
        max_rank = int(animes_df['details.Popularity'].max())
        popularity_slider = st.slider(label='Select a range of popularity',min_value=min_rank,max_value=max_rank,value=(min_rank,max_rank))

genre_expander = st.sidebar.beta_expander("Genre", expanded=False)
with genre_expander:
    genre_multiselect = st.multiselect('Select the genres',genres_list)
    # genre_selectbox = st.selectbox('Select a genre',genres_list)

type_expander = st.sidebar.beta_expander("Type", expanded=False)
with type_expander:
    type_list = animes_df["details.Type"].drop_duplicates().values.tolist()
    type_multiselect = st.multiselect('Select the types',type_list,type_list)
    # type_selectbox = st.selectbox('Select a type',type_list)

rating_expander = st.sidebar.beta_expander("Rating", expanded=False)
with rating_expander:
    rating_list = animes_df["details.Rating"].drop_duplicates().values.tolist()
    rating_multiselect = st.multiselect('Select the ratings',rating_list,rating_list)

episodes_expander = st.sidebar.beta_expander("Episodes", expanded=False)
with episodes_expander:
    min_ep = int(animes_df['details.Episodes'].min())
    max_ep = int(animes_df['details.Episodes'].max())
    episodes_col1, score_col2  = st.beta_columns((8,1))
    with episodes_col1:
        episodes_slider = st.slider(label='Select a range of episode',min_value=min_ep,max_value=max_ep,value=(min_ep, max_ep))

status_expander = st.sidebar.beta_expander("Status", expanded=False)
with status_expander:
    status_list = animes_df["details.Status"].drop_duplicates().values.tolist()
    status_multiselect = st.multiselect('Select the status',status_list,status_list)

search_by_producer_expander = st.sidebar.beta_expander("Search by Producer", expanded=False)
with search_by_producer_expander:
    search_by_producer_text = st.text_input(label='Type the name of a producer')

search_by_studio_expander = st.sidebar.beta_expander("Search by Studio", expanded=False)
with search_by_studio_expander:
    search_by_studio_text = st.text_input(label='Type the name of a studio')

# aired_expander = st.sidebar.beta_expander("Aired", expanded=False)
# with aired_expander:
#     min_aired = animes_df['aired_from'].min()
#     max_aired = animes_df['aired_to'].max()
#     aired_col1, aired_col2  = st.beta_columns((8,1))
#     with aired_col1:
#         aired_slider = st.slider(
#             "From - To",
#             min_value=datetime.strptime(min_aired.strftime('%y-%m-%d'),'%y-%m-%d'),
#             max_value=datetime.strptime(max_aired.strftime('%y-%m-%d'),'%y-%m-%d'),
#             value=(datetime.strptime(min_aired.strftime('%y-%m-%d'),'%y-%m-%d'),datetime.strptime(max_aired.strftime('%y-%m-%d'),'%y-%m-%d')),
#             format="YYYY-MM-DD"
#         )


# Filtering the dataset
joined_df = pd.merge(animes_df, genres_df, on='id')

# Name
joined_df = joined_df[joined_df['title'].str.contains(search_by_name_text)]

# Score
joined_df = joined_df[joined_df['details.Score'].fillna(0.0).between(score_slider[0], score_slider[1])]

# Rank
joined_df = joined_df[joined_df['details.Ranked'].fillna(0).between(rank_slider[0], rank_slider[1])]

# Popularity
joined_df = joined_df[joined_df['details.Popularity'].fillna(0).between(popularity_slider[0], popularity_slider[1])]

# Genres
for genre in genre_multiselect:
    joined_df = joined_df[joined_df[genre] == 1]

# Types
joined_df = joined_df[joined_df['details.Type'].isin(type_multiselect)]

# Rating
joined_df = joined_df[joined_df['details.Rating'].isin(rating_multiselect)]

# Episodes
joined_df = joined_df[joined_df['details.Episodes'].fillna(1).between(episodes_slider[0], episodes_slider[1])]

# Status
joined_df = joined_df[joined_df['details.Status'].isin(status_multiselect)]

# Producers
joined_df = joined_df[joined_df['details.Producers'].str.contains(search_by_producer_text)]

# Studios
joined_df = joined_df[joined_df['details.Studios'].str.contains(search_by_studio_text)]

# Aired
# joined_df = joined_df[joined_df['aired_from'] >= aired_slider[0]]
# joined_df = joined_df[joined_df['aired_to'] <= aired_slider[1]]


# ------------------------------------------------------------------------------------------------------------------------

# Main panel

header_col1, header_col2 = st.beta_columns((2,1))

with header_col1:
    st.title("**Analysis**")
    st.text('Data exploration of Animes')

with header_col2:
    title_img = build_image(title)
    st.image(title_img)

kpi_expander = st.beta_expander("KPIs", expanded=False)
with kpi_expander:
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6, kpi_col7 = st.beta_columns(7)

    with kpi_col1:
        st.markdown(f'## {len(joined_df.index)}')
        st.markdown('###### Animes')

    with kpi_col2:
        st.markdown(f'## {len(genres_list)}')
        st.markdown('###### Genres')

    with kpi_col3:
        st.markdown(f"## {len(joined_df['id'][joined_df['details.Type'] == 'TV'].index)}")
        st.markdown('###### TV')

    with kpi_col4:
        st.markdown(f"## {len(joined_df['id'][joined_df['details.Type'] == 'Movie'].index)}")
        st.markdown('###### Movie')

    with kpi_col5:
        st.markdown(f"## {len(joined_df['id'][joined_df['details.Type'].isin(['OVA','ONA'])].index)}")
        st.markdown('###### OVA & ONA')

    with kpi_col6:
        st.markdown(f"## {len(joined_df['id'][joined_df['details.Type'] == 'Special'].index)}")
        st.markdown('###### Special')

    with kpi_col7:
        st.markdown(f"## {len(joined_df['id'][joined_df['details.Type'].fillna('NOTFOUND') == 'NOTFOUND'].index)}")
        st.markdown('###### Other types')

session_break(2)

tops_expander = st.beta_expander("Top N", expanded=False)

with tops_expander:
    tops_n_col1, tops_n_col2 = st.beta_columns((1,10))
    with tops_n_col1:
        top_n = int(st.text_input(label='Number of TOP',value=5))

    tops_col1, tops_col2 = st.beta_columns(2)
    with tops_col1:
        top_10_rank = joined_df[joined_df['details.Ranked']>0]\
                        .sort_values('details.Ranked',ascending=True)\
                        .head(top_n)[['details.Ranked','id','title','details.Genres_x']]\
                        .rename(columns={'details.Ranked': 'Position', 'id': 'ID', 'title': 'Title', 'details.Genres_x': 'Genres'})\
                        .reset_index(drop=True)

        st.subheader('Rank')
        st.dataframe(top_10_rank)

    with tops_col2:
        top_10_popularity = joined_df[joined_df['details.Popularity']>0]\
                        .sort_values('details.Popularity',ascending=True)\
                        .head(top_n)[['details.Popularity','id','title','details.Genres_x']]\
                        .rename(columns={'details.Popularity': 'Position', 'id': 'ID', 'title': 'Title', 'details.Genres_x': 'Genres'})\
                        .reset_index(drop=True)

        st.subheader('Popularity')
        st.dataframe(top_10_popularity)

    tops_col1, tops_col2 = st.beta_columns(2)
    with tops_col1:
        top_10_members = joined_df[joined_df['details.Members']>0]\
                        .sort_values('details.Members',ascending=False)\
                        .head(top_n)[['details.Members','id','title','details.Genres_x']]\
                        .rename(columns={'details.Members': 'Members', 'id': 'ID', 'title': 'Title', 'details.Genres_x': 'Genres'})\
                        .reset_index(drop=True)

        st.subheader('Members')
        st.dataframe(top_10_members)

    with tops_col2:
        top_10_score = joined_df\
                        .sort_values('details.Score',ascending=False)\
                        .head(top_n)[['details.Score','id','title','details.Genres_x']]\
                        .rename(columns={'details.Score': 'Score', 'id': 'ID', 'title': 'Title', 'details.Genres_x': 'Genres'})\
                        .reset_index(drop=True)
        st.subheader('Score')
        st.dataframe(top_10_score.style.format({"Score": "{:.2f}"}))

    tops_col1, tops_col2, tops_col3 = st.beta_columns((1,2,1))
    with tops_col2:
        top_10_episodes = joined_df\
                        .sort_values('details.Episodes',ascending=False)\
                        .head(top_n)[['details.Episodes','id','title','details.Genres_x']]\
                        .rename(columns={'details.Episodes': 'Episodes', 'id': 'ID', 'title': 'Title', 'details.Genres_x': 'Genres'})\
                        .reset_index(drop=True)

        st.subheader('Episodes')
        st.dataframe(top_10_episodes)

session_break(2)

viz_expander = st.beta_expander("Data Visualizations", expanded=False)

with viz_expander:
    viz_col1, viz_col2, viz_col3, viz_col4, viz_col5 = st.beta_columns((1.5,0.5,0.5,2,0.5))
    with viz_col1:
        st.subheader('Type')
        type_fig = generate_donut_chart('details.Type')
        st.pyplot(type_fig)

    with viz_col4:
        st.subheader('Status')
        status_fig = generate_donut_chart('details.Status')
        st.pyplot(status_fig)

    st.subheader('Genres')

    genres_labels = []
    genres_sizes = []

    if genre_multiselect != []:
        filter_genres_list = genre_multiselect
    else:
        filter_genres_list = genres_list

    for genre in filter_genres_list:
        filtered_genre_df = joined_df[joined_df[genre]==1]
        genre_agg_df = filtered_genre_df[[genre,'id']]\
                            .groupby(genre, as_index=False)\
                            .agg('count')
        genres_labels.append(genre)
        genres_sizes.append(genre_agg_df['id'].values[0])

    genres_dict = {'Genres': genres_labels, 'Animes': genres_sizes}  
    genre_agg_df = pd.DataFrame(genres_dict)

    bar = alt.Chart(genre_agg_df).mark_bar().encode(
        x=alt.X('Genres:O', sort='-y'),
        y='Animes:Q',
        color=alt.Color(
            'Genres:O',
            legend=None
        )
    )

    text = bar.mark_text(
        align='left',
        baseline='middle',
        dx=-12,
        dy=-7
    ).encode(
        text='Animes:Q'
    )

    st.altair_chart((bar+text), use_container_width=True)
    
session_break(2)

xray_expander = st.beta_expander('X-Ray (closer look into a title)', expanded=True)

with xray_expander:
    xray_filter_col1, xray_filter_col2 = st.beta_columns((1,1))
    with xray_filter_col1:
        title_list = animes_df[['id','title']].sort_values('id',ascending=True).drop_duplicates().values.tolist()
        xray_selection = st.selectbox(label='ID, Title',options=title_list,index=10)

        selected_anime = animes_df[animes_df['id']==xray_selection[0]]

    xray_header_col1, xray_header_col2, xray_header_col3, xray_header_col4, xray_header_col5 = st.beta_columns((0.5,0.5,0.5,0.5,2.5))
    with xray_header_col1:
        st.header(float(selected_anime['details.Score']))
        st.markdown('###### Score')
    with xray_header_col2:
        st.header(int(selected_anime["details.Ranked"]))
        st.markdown('###### Rank')
    with xray_header_col3:
        st.header(int(selected_anime["details.Popularity"]))
        st.markdown('###### Popularity')
    with xray_header_col4:
        st.header(int(selected_anime['details.Members']))
        st.markdown('###### Members')
    with xray_header_col5:
        st.subheader('Links')
        st.markdown(f'###### **Episodes**: {str(selected_anime["links.episodes"].values[0])}')
        st.markdown(f'###### **Stats**: {str(selected_anime["links.stats"].values[0])}')
        st.markdown(f'###### **Characters & Staff**: {str(selected_anime["links.characters & staff"].values[0])}')

    session_break(2)

    xray_body_col1, xray_body_col2, xray_body_col3, xray_body_col4 = st.beta_columns((1,1,1,1))
    with xray_body_col1:
        download_agent = ImageRenderDownloader(int(selected_anime["id"].values[0]),str(selected_anime["photo"].values[0]))
        folder_path = download_agent.download()
        st.image(build_image(folder_path))
    with xray_body_col2:
        st.subheader('Information')
        session_break(1)
        st.write(f'**Type**: {str(selected_anime["details.Type"].values[0])}')
        st.write(f'**Episodes**: {selected_anime["details.Episodes"].values[0]}')
        st.write(f'**Status**: {str(selected_anime["details.Status"].values[0])}')
        st.write(f'**Aired**: {str(selected_anime["details.Aired"].values[0])}')
        st.write(f'**Premiered**: {str(selected_anime["details.Premiered"].values[0])}')
    with xray_body_col3:
        session_break(4)
        st.write(f'**Broadcast**: {str(selected_anime["details.Broadcast"].values[0])}')
        st.write(f'**Producers**: {selected_anime["details.Producers"].values[0]}')
        st.write(f'**Licensors**: {selected_anime["details.Licensors"].values[0]}')
        st.write(f'**Studios**: {str(selected_anime["details.Studios"].values[0])}')
    with xray_body_col4:
        session_break(4)
        st.write(f'**Source**: {str(selected_anime["details.Source"].values[0])}')
        st.write(f'**Genres**: {selected_anime["details.Genres"].values[0]}')
        st.write(f'**Duration**: {str(selected_anime["details.Duration"].values[0])}')
        st.write(f'**Rating**: {str(selected_anime["details.Rating"].values[0])}')

    xray_syn_col1, xray_syn_col2 = st.beta_columns((1,0.01))
    with xray_syn_col1:
        st.subheader('Synopsis')
        st.markdown(str(selected_anime["synopsis"].values[0]))
        st.subheader('Background')
        st.markdown(str(selected_anime["background"].values[0]))