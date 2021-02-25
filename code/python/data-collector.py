import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import pytz
import concurrent.futures
import argparse


def parseArgs():
    parser = argparse.ArgumentParser(
        prog='app',
        usage='%(prog)s [OPTIONS]',
        description='Script for web scraping'
    )

    parser.add_argument("-s", metavar="start", type=str, help="ID to start the scrap")
    parser.add_argument("-e", metavar="end", type=str, help="ID limit to scrap")

    args = parser.parse_args()

    if args.s is None or args.e is None:
        parser.print_help()
        exit(1)

    return args


def get_anime_title(soup):
    return soup.find(class_='title-name h1_bold_none').find('strong').contents[0]


def get_anime_photo(soup):
    try:
        return soup.find('td').find('img').get('data-src')
    except:
        return None


def get_anime_links(soup):
    links_dict = {}
    wanted_links = ['Episodes','Characters & Staff','Stats']

    try:
        for link_block in soup.find('table').find('tr').find_all('li'):
            if link_block.find('a').contents[0] in wanted_links:
                links_dict[link_block.find('a').contents[0].lower()] = link_block.find('a').get('href')
    
        return links_dict
    except:
        return None  


def get_anime_synopsis(soup):
    synopsis = ''

    if soup.find('table').find('tr').find('p').get('itemprop') == 'description':
        for block in soup.find('table').find('tr').find('p'):
            if '<br/>' not in str(block) and 'Written by MAL Rewrite' not in str(block) and str(block) != '\n':
                synopsis = synopsis + str(block)
                
    return synopsis.replace('\r','').replace('\n',' ').replace('<i>','').replace('</i>','')


def get_anime_background(soup):
    if 'No background information' in soup.find('table').contents[1].find_all('td')[9].find('td').contents[4]:
        return 'No background information'
    
    background = ''
    counter = 4

    content_list = soup.find('table').contents[1].find_all('td')[9].find('td')
    while counter < len(content_list):
        content = content_list.contents[counter]
        if 'div' not in str(content):
            background = background+str(content)
        counter+=1

    return background.replace('\r','').replace('\n',' ').replace('<i>','').replace('</i>','')


def get_anime_details(soup):
    type_info = soup.find_all('td')[0].find_all('div')

    details_dict = {}

    iterator = 7
    while iterator <= len(type_info):
        try:
            if 'Type' in type_info[iterator].contents[1].contents[0]:
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = type_info[iterator].find('a').contents[0].rstrip().lstrip()
                iterator+=1
            elif 'Premiered' in type_info[iterator].contents[1].contents[0]:
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = type_info[iterator].find('a').contents[0].rstrip().lstrip()
                iterator+=1
            elif 'Producers' in type_info[iterator].contents[1].contents[0]:
                producers_list = []
                for producer in type_info[iterator].find_all('a'):
                    producers_list.append(producer.contents[0])
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = producers_list
                iterator+=1
            elif 'Licensors' in type_info[iterator].contents[1].contents[0]:
                licensors_list = []

                if 'None found' in type_info[iterator].contents[2]:
                    licensors_list.append('None found')
                else:
                    for licensor in type_info[iterator].find_all('a'):
                        licensors_list.append(licensor.contents[0])
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = licensors_list
                iterator+=1
            elif 'Studios' in type_info[iterator].contents[1].contents[0]:
                studios_list = []
                for studio in type_info[iterator].find_all('a'):
                    studios_list.append(studio.contents[0])
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = studios_list
                iterator+=1
            elif 'Genres' in type_info[iterator].contents[1].contents[0]:
                genres_list = []
                for genre in type_info[iterator].find_all('a'):
                    genres_list.append(genre.contents[0])
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = genres_list
                iterator+=1
            elif 'Score' in type_info[iterator].contents[1].contents[0]:    
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = type_info[iterator].contents[3].contents[0].rstrip().lstrip()
                details_dict['ScoredBy'] = type_info[iterator].contents[6].contents[0].rstrip().lstrip()
                iterator+=2
            elif 'Ranked' in type_info[iterator].contents[1].contents[0]:    
                details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = type_info[iterator].contents[2].rstrip().lstrip()
                iterator+=2
            else:
                try:
                    details_dict[type_info[iterator].contents[1].contents[0].replace(':','')] = type_info[iterator].contents[2].rstrip().lstrip()
                    iterator+=1
                except:
                    iterator+=1
        except:
            iterator+=1
            
    return details_dict


def build_anime_dict(soup):
    brazil_time = pytz.timezone("America/Sao_Paulo")
    anime_dict = {}
    
    anime_dict['id'] = get_anime_title(soup)
    anime_dict['title'] = get_anime_title(soup)
    anime_dict['photo'] = get_anime_photo(soup)
    anime_dict['links'] = get_anime_links(soup)
    anime_dict['synopsis'] = get_anime_synopsis(soup)
    anime_dict['background'] = get_anime_background(soup)
    anime_dict['details'] = get_anime_details(soup)
    anime_dict['date_extraction'] = datetime.datetime.now().astimezone(brazil_time).strftime("%Y-%m-%d %H:%M:%S")
    
    return anime_dict


def scrap_animes(start,end):
    result_dict = []
    counter = start
    limit = end
    not_found_counter = 0
    slice_size = 100
    last_slice = 0
    
    while counter <= limit:
        r = requests.get(f'https://myanimelist.net/anime/{counter}')

        if r.status_code == 403:
            print(f'ID: {counter}, StatusCode: {r.status_code} --- Counter 404: {not_found_counter}')
            print('waiting 1 minute because heavy traffic')
            time.sleep(60)
            r = requests.get(f'https://myanimelist.net/anime/{counter}')
            if r.status_code == 403:
                counter-=1

        if r.status_code == 200:
            print(f'ID: {counter}, StatusCode: {r.status_code} --- Counter 404: {not_found_counter}')
            soup = BeautifulSoup(r.text, 'html.parser')
            anime_dict = build_anime_dict(soup)
            anime_dict['id'] = counter

            result_dict.append(anime_dict)
            not_found_counter = 0
        elif r.status_code == 404:
            print(f'ID: {counter}, StatusCode: {r.status_code} --- Counter 404: {not_found_counter}')
            not_found_counter+=1

        #  --- Condition to stop the job if a target number of sequential of 404 resposes is reached ---
        # if not_found_counter == 2000:
        #     print('1000 calls returned 404 NOT FOUND')
        #     return None

        if counter != start and counter % slice_size == 0:
            last_slice = counter
            with open(f'devops/volume/datasets/anime/raw_data/{counter-slice_size+1}-{last_slice}.json', 'w') as outfile:  
                json.dump(result_dict, outfile)
            result_dict = []

        time.sleep(0.5)
        counter+=1

    with open(f'devops/volume/datasets/anime/raw_data/{last_slice+1}-{counter}.json', 'w') as outfile:  
        json.dump(result_dict, outfile)


def main():
    args = parseArgs()
    start = int(args.s)
    end = int(args.e)
    
    print('Scrap process starting')

    start_time = time.time()

    scrap_animes(start,end)

    print(f'--- It took {(time.time() - start_time)} seconds to complete all scraps ---')


if __name__ == '__main__':
    main()