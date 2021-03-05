import json
from datetime import datetime, timedelta
import pandas as pd
from os import listdir
from os.path import isfile, join


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
    
    print(f'Concatened {file_counter} json files into one.')
    return concatenated_file


df = pd.json_normalize(concatened_json_files('devops/volume/datasets/anime/raw_data/'))


columns_for_treatment = ['Score','Ranked','Popularity','ScoredBy','Members','Favorites']


for column in columns_for_treatment:
    def transform_into_number(df_row):
        if df_row[f'details.{column}'] == 'N/A' or df_row[f'details.{column}'] == '':
            return 0
        if '.' in df_row[f'details.{column}']:
            return float(df_row[f'details.{column}'])
        return int(df_row[f'details.{column}'].replace('#','').replace(',',''))
    df[f'details.{column}'] = df.apply(transform_into_number,axis=1)


columns_for_treatment = ['Producers','Licensors','Studios']

for column in columns_for_treatment:
    def treat_blank_values(df_row):
        if 'add some' in df_row[f'details.{column}'] or 'None found' in df_row[f'details.{column}']:
            return None
        else:
            return df_row[f'details.{column}']
    df[f'details.{column}'] = df.apply(treat_blank_values,axis=1)


def convert_date_format(date):
    try:
        date_transformed = datetime.strptime(date, "%b %d, %Y")
        return datetime.strftime(date_transformed, '%Y-%m-%d')
    except:
        return f'Failed: {date}'

    
def get_aired_from_date(df_row):
    if df_row['details.Aired'] == 'Not available':
        return None
    if len(df_row['details.Aired']) == 4:
        return convert_date_format(f'Jan 1, {df_row["details.Aired"]}')
    if df_row['details.Status'] == 'Not yet aired':
        return None
    else:
        aired = df_row['details.Aired'][:12].rstrip()
        
        if 'to ?' in aired and len(aired) == 9:
            return convert_date_format(f'Jan 1, {aired[:4]}')
        
        if 'to' not in aired and len(aired) == 9:
            partial_date = aired.rstrip().lstrip()
            return convert_date_format(f'{partial_date[:3]} 1, {partial_date[5:]}')
        
        elif 'to' in aired:
            if len(aired) == 9:
                partial_date = aired.replace('to','').rstrip().lstrip()
                return convert_date_format(f'{partial_date[:3]} 1, {partial_date[5:]}')
            if len(aired[:aired.find('to')-1].rstrip()) == 4:
                return convert_date_format(f'Jan 1, {aired[:aired.find("to")-1].rstrip()}')
            
        else:
            return convert_date_format(aired)


def get_aired_to_date(df_row):
    if df_row['details.Aired'] == 'Not available':
        return None
    if len(df_row['details.Aired']) == 4:
        return convert_date_format(f'Jan 1, {df_row["details.Aired"]}')
    if 'to ?' in df_row['details.Aired']:
        return None

    else:
        aired = df_row['details.Aired'][-12:].lstrip()

        if len(aired) == 9:
            partial_date = aired.replace('to','').rstrip().lstrip()
            return convert_date_format(f'{partial_date[:3]} 1, {partial_date[5:]}')

        if 'to' in aired:
            if len(aired[aired.find('to')+3:]) == 4:
                return convert_date_format(f'Dec 31, {aired[aired.find("to")+3:]}')
            if len(aired) == 9:
                partial_date = aired.replace('to','').rstrip().lstrip()
                return convert_date_format(f'{partial_date[:3]} 1, {partial_date[5:]}')

        else:
            return convert_date_format(aired)

    
def calculate_airing_duration(df_row):
    if df_row['details.Aired'] == 'Not available':
        return None
    
    from_date = df_row['aired_from']
    to_date = df_row['aired_to']
    
    if to_date is None and df_row['details.Status'] == 'Currently Airing':
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
    except:
        return 0
    else:
        return int((to_datetime - from_datetime).total_seconds() / 86400)


def get_hours_per_episode(df_row):
    if 'hr' in df_row['details.Duration']:
        return int(df_row['details.Duration'][:df_row['details.Duration'].find('hr')-1])
    else:
        return 0
    

def get_minutes_per_episode(df_row):
    if 'min' in df_row['details.Duration']:
        if 'hr.' in df_row['details.Duration']:
            return int(df_row['details.Duration'][df_row['details.Duration'].find('hr.')+4:df_row['details.Duration'].find('min')-1])
        else:
            return int(df_row['details.Duration'][:df_row['details.Duration'].find('min')-1])
    else:
        return 0

    
def get_seconds_per_episode(df_row):
    if 'sec' in df_row['details.Duration']:
        return int(df_row['details.Duration'][:df_row['details.Duration'].find('sec')-1])
    else:
        return 0
    
    
def calculate_episode_lenght_in_seconds(df_row):
    return df_row['hours_per_episode']*3600 + df_row['minutes_per_episode']*60 + df_row['seconds_per_episode']
    

def calculate_airing_duration_in_seconds(df_row):
    if df_row['details.Aired'] == 'Not available':
        return None
    
    if df_row['details.Episodes'] != 'Unknown':
        return int(df_row['details.Episodes']) * df_row['episode_lenght_in_seconds']
    else:
        return None
    
    
def fix_episodes(df_row): 
    if df_row['details.Episodes'] != 'Unknown':
        return int(df_row['details.Episodes'])
    else:
        return 0


df['aired_from'] = df.apply(get_aired_from_date,axis=1)
df['aired_to'] = df.apply(get_aired_to_date,axis=1)
df['days_in_air'] = df.apply(calculate_airing_duration,axis=1)
df['hours_per_episode'] = df.apply(get_hours_per_episode,axis=1)
df['minutes_per_episode'] = df.apply(get_minutes_per_episode,axis=1)
df['seconds_per_episode'] = df.apply(get_seconds_per_episode,axis=1)
df['episode_lenght_in_seconds'] = df.apply(calculate_episode_lenght_in_seconds,axis=1)
df['seconds_in_air'] = df.apply(calculate_airing_duration_in_seconds,axis=1)
df['details.Episodes'] = df.apply(fix_episodes,axis=1)
df['aired_from'] = pd.to_datetime(df['aired_from'])
df['aired_to'] = pd.to_datetime(df['aired_to'])
df['details.Producers'] = df['details.Producers'].astype(str)
df['details.Studios'] = df['details.Studios'].astype(str)


df.to_parquet(path='devops/volume/datasets/anime/enhanced_data/prepared_animes.parquet')
# df.to_csv('devops/volume/datasets/anime/enhanced_data/prepared_animes.csv',sep=';',index=False)


def parse_list_in_column(data_dict,column_for_parse):
    result_list = []
    for obj in data_dict:
        for value in obj['details'][column_for_parse]:
            result_list.append(value)

    return list(set(result_list))


animes_dict = concatened_json_files('devops/volume/datasets/anime/raw_data/')
genre_df = df[['id','details.Genres']]

for genre in parse_list_in_column(animes_dict,'Genres'):
    def create_genre_column(df_row):
        if genre in df_row['details.Genres']:
            return 1
        else:
            return 0
    genre_df[genre] = genre_df.apply(create_genre_column,axis=1)

genre_df.to_parquet(path='devops/volume/datasets/anime/enhanced_data/animes_genres.parquet')
# genre_df.to_csv('devops/volume/datasets/animes/enhanced_data/animes_genres.csv',sep=';',index=False)