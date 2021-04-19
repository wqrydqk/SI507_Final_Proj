import sqlite3
import requests
from bs4 import BeautifulSoup
import json


def open_cache(cache_filename):
    ''' opens the cache file if it exists and loads the JSON into
        a dictionary, which it then returns.
        if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    cache_filename: str
        the name of the json file to open

    Returns
    -------
    The opened cache
    '''

    try:
        cache_file = open(cache_filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, cache_filename):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    cache_filename: str
        The name of the cache file

    Returns
    -------
    None
    '''

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_filename,"w")
    fw.write(dumped_json_cache)
    fw.close()


def get_us_state_list(url_to_get_states):

    file_name = 'states_cache.json'
    cache_dict = open_cache(file_name)

    if url_to_get_states in cache_dict:
        print('using cache for us states!')
        return cache_dict[url_to_get_states]
    else:
        print('fetching for us states!')
        response = requests.get(url_to_get_states)
        text_to_parse = response.text
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        all_states = soup.find('tbody').find_all('tr')
        us_states_list = []
        for i in range(len(all_states)):
            temp_state = all_states[i]
            temp_state_info = temp_state.find_all('td')
            temp_dict = {}
            temp_dict['state'] = temp_state_info[0].text.strip()
            temp_dict['state_code'] = temp_state_info[1].text.strip()
            temp_dict['population'] = temp_state_info[2].text.strip()
            temp_dict['capital'] = temp_state_info[3].text.strip()
            us_states_list.append(temp_dict)
        cache_dict[url_to_get_states] = us_states_list
        save_cache(cache_dict, file_name)
        return us_states_list


def get_us_airports_list(url_to_get_airports):

    file_name = "ariports_cache.json"
    cache_dict = open_cache(file_name)

    if url_to_get_airports in cache_dict:
        print("using cache for us airports!")
        return cache_dict[url_to_get_airports]
    else:
        print("fetching for us airports!")
        response = requests.get(url_to_get_airports)
        text_to_parse = response.text
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        my_list_for_airports = soup.find('table', border=1).find_all('tr')[15:]
        airport_list = []
        for element in my_list_for_airports:
            element_info_list = element.find_all('td')
            temp_dict = {}
            temp_dict['airport_code'] = element_info_list[0].text.strip()
            temp_dict['airport_name'] = element_info_list[1].text.strip()
            temp_dict['airport_city'] = element_info_list[2].text.strip()
            temp_dict['airport_state_code'] = element_info_list[3].text.strip()
            airport_list.append(temp_dict)
        cache_dict[url_to_get_airports] = airport_list
        save_cache(cache_dict, file_name)
        return airport_list


def get_us_city_area_list(url_to_get_city_area):

    file_name = 'cityareas_cache.json'
    cache_dict = open_cache(file_name)
    if url_to_get_city_area in cache_dict:
        print('using cache for us city areas!')
        return cache_dict[url_to_get_city_area]
    else:
        print('fetching for us city areas!')
        response = requests.get(url_to_get_city_area)
        text_to_parse = response.text
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        result = soup.find(id="mw-content-text")
        result1 = result.find_all('tbody')
        result2 = result1[1].find_all('tr')
        city_area_list = []
        for element in result2[1:]:
            temp_dict = {}
            temp_dict['city_name'] = element.find('a').text.strip()
            temp_dict['city_state'] = element.find_all('td')[2].text.strip()
            temp_str_list = element.find_all('td')[4].text.strip().split(',')
            temp_area = int(''.join(temp_str_list))
            temp_dict['city_area'] = temp_area
            city_area_list.append(temp_dict)
        cache_dict[url_to_get_city_area] = city_area_list
        save_cache(cache_dict, file_name)
        return city_area_list


if __name__ == "__main__":
    ############################
    # get the data by scraping #
    ############################
    # the states in the US, in list form
    url_for_us_states = "https://www.englisch-hilfen.de/en/texte/states.htm"
    us_states_list_to_store = get_us_state_list(url_for_us_states)

    # the airports in the US, in list form
    url_for_us_airports = 'https://www.airportcodes.us/us-airports.htm'
    us_airports_list_to_store = get_us_airports_list(url_for_us_airports)

    # the largest cities in the US, in list form
    url_for_us_cities = 'http://en.volupedia.org/wiki/List_of_United_States_cities_by_area'
    us_cities_list_to_store = get_us_city_area_list(url_for_us_cities)

    ############################
    # start to create database #
    ############################
    print('with all the data, create the database...')
    # open a connection to the database
    conn = sqlite3.connect("airport_database.sqlite")

    # create an instance of cursor
    cur = conn.cursor()

    # create table "states"
    drop_states = '''DROP TABLE IF EXISTS "states"'''
    create_states = '''
    CREATE TABLE IF NOT EXISTS "states"(
    "Id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    "StateName" TEXT NOT NULL,
    "StateCode" TEXT NOT NULL
    );
    '''
    insert_states = '''
    INSERT INTO states ("StateName", "StateCode") VALUES (?, ?)
    '''
    cur.execute(drop_states)
    cur.execute(create_states)
    for each_state in us_states_list_to_store:
        data_to_insert = [each_state['state'], each_state['state_code']]
        cur.execute(insert_states, data_to_insert)

    # create table "airports"
    drop_airports = '''DROP TABLE IF EXISTS "airports"'''
    create_airports = '''
    CREATE TABLE IF NOT EXISTS "airports"(
    "Number" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    "AirportCode" TEXT NOT NULL,
    "AirportName" TEXT NOT NULL,
    "AirportCity" TEXT NOT NULL,
    "AirportState" TEXT NOT NULL,
    FOREIGN KEY(AirportState) REFERENCES states(StateCode)
    );
    '''
    insert_airports = '''
    INSERT INTO airports ("AirportCode", "AirportName", "AirportCity", "AirportState")
    VALUES (?, ?, ?, ?)
    '''
    cur.execute(drop_airports)
    cur.execute(create_airports)
    for each_airport in us_airports_list_to_store:
        data_to_insert = [each_airport['airport_code'],
                          each_airport['airport_name'],
                          each_airport['airport_city'],
                          each_airport['airport_state_code']]
        cur.execute(insert_airports, data_to_insert)

    # create table "cities_by_area"
    drop_cities_by_area = '''DROP TABLE IF EXISTS "cities_by_area"'''
    create_cities = '''
    CREATE TABLE IF NOT EXISTS "cities_by_area"(
    "Orders" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    "CityName" TEXT NOT NULL,
    "CityState" TEXT NOT NULL,
    "CityArea" INTEGER NOT NULL,
    FOREIGN KEY(CityState) REFERENCES states(StateName)
    );
    '''
    insert_cities = '''
    INSERT INTO cities_by_area ("CityName", "CityState", "CityArea")
    VALUES (?, ?, ?)
    '''
    cur.execute(drop_cities_by_area)
    cur.execute(create_cities)
    for each_city in us_cities_list_to_store:
        data_to_insert = [each_city['city_name'],
                          each_city['city_state'],
                          each_city['city_area']]
        cur.execute(insert_cities, data_to_insert)

    # commit the changes
    conn.commit()

    # close
    conn.close()
    print('DONE!')