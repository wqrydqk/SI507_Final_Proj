import requests
import plotly
import json
import sqlite3
import webbrowser
import secrets


attraction_types_to_choose = [
    'bridges', 'historic_architecture', 'lighthouses', 'skyscrapers',
    'towers', 'museums', 'theatres_and_entertainments', 'urban_environment',
    'archaeology', 'burial_places', 'fortifications', 'historical_places',
    'monuments_and_memorials', 'beaches', 'geological_formations', 'glaciers',
    'islands', 'natural_springs', 'nature_reserves', 'water',
    'buddhist_temples', 'cathedrals', 'egyptian_temples', 'hindu_temples',
    'monasteries', 'mosques', 'synagogues', 'other_temples',
]


class CityAttrInfo:
    '''a city with a given attraction type

    Instance Attributes
    -------------------
    city_name: str
        the name of the city to search

    attraction_type: str
        the type of the attraction in the city to search

    city_attraction_lists: list
        a list of attractions given the city and the attraction type
    '''

    def __init__(self, city_name, city_attraction_type, city_attraction_list):
        self.name = generate_unique_city_attraction_name(city_name, city_attraction_type)
        self.attractions = city_attraction_list

    def info(self):
        return self.name


class Attraction:
    '''an attraction

    Instance Attributes
    -------------------
    attr_name: str
        the name of the attraction
    attr_lon: float
        the longitude of the attraction
    attr_lat: float
        the latitude of the attraction
    attr_rate: int
        minimum rating of attraction's popularity
    '''

    def __init__(self, attr_name, attr_lon, attr_lat, attr_rate):
        if attr_name != '':
            self.attr_name = attr_name
        else:
            self.attr_name = '<name not provided!>'
        self.attr_lon = attr_lon
        self.attr_lat = attr_lat
        self.attr_rate = attr_rate

    def info(self):
        return f"{self.attr_name} at lon: {self.attr_lon}, lat: {self.attr_lat}"


class Hotel:
    '''a hotel

    Instance Attributes
    -------------------
    hotel_name: str
        the name of the hotel
    hotel_price: str
        the price of the hotel, eg. "$", "$$", "$$$", "$$$$", or "$$$$$"
    hotel_rating: float
        the rating of the hotel
    hotel_url: str
        the url of the hotel on yelp
    hotel_reviews: int
        the number of reviews on this hotel
    hotel_phone: str
        the phone of the hotel
    '''

    def __init__(self, hotel_name, hotel_price, hotel_rating, hotel_url,
                 hotel_reviews, hotel_phone):
        self.name = hotel_name
        self.price = hotel_price
        self.rating = hotel_rating
        self.url = hotel_url
        self.review_count = hotel_reviews
        self.phone = hotel_phone

    def info(self):
        return f"{self.name}---price: {self.price}, rating: {self.rating}"


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


# conn = sqlite3.connect('../my_data_base/airport_database.sqlite')
# cur = conn.cursor()

def get_city_location_info(city_to_search):
    ''' get the location of the city

    This function takes in the name of a city, and uses OpenTripMap API (url:
    https://opentripmap.io/product) to get the longitude and latitude of the
    city

    Parameters
    ----------
    city_to_search: str
        the name of the city to search using OpenTripMap API

    Returns
    -------
    dict
    '''

    file_name = 'city_location.json'
    cache_dict = open_cache(file_name)
    if city_to_search in cache_dict:
        #print('using cache to get the city location!')
        return cache_dict[city_to_search]
    else:
        #print('getting the data from api to get the cty location!')
        base_url_for_geo_name = 'https://api.opentripmap.com/0.1/en/places/geoname'
        params = {'name': city_to_search,
                  'apikey': secrets.opentripmap_api_key}
        response = requests.get(base_url_for_geo_name, params).json()
        if response['status'] != 'OK':
            #print('the city you input does not exist! please try another')
            return {}
        else:
            if response['country'] != 'US':
                #print('the city you input do exist, but not in the US, try another!')
                return {}
            else:
                #print('this a valid US city, we can use it!')
                temp_dict = {}
                position_of_the_city = {'lat': round(response['lat'], 2),
                                        'lon': round(response['lon'], 2)}
                name_of_the_city = response['name']
                temp_dict['position'] = position_of_the_city
                temp_dict['name'] = name_of_the_city
                cache_dict[city_to_search] = temp_dict
                save_cache(cache_dict, file_name)
                return temp_dict


# my_city = input('Which city is your destination?').strip().lower()
# my_city_dict = get_city_location_info(my_city)
# print(my_city_dict)


def generate_unique_city_attraction_name(city_name, attraction_type):
    ''' generate the unique key by city name and attraction type

    this function generates a unique string given city name and attraction
    type, the generated string takes the form:
    <city_name>_<attraction_type>

    Parameters
    ----------
    city_name:　str
        the name of the city

    attraction_type: str
        the name of the attraction type

    Returns
    -------
    str
    '''

    return city_name + '_' + attraction_type


def generate_unique_hotel_name(lon, lat):
    ''' generate the unique key by longitude and latitude

    this function generates a unique string given longitude and latitude of the
    attraction, the returned string takes the form of:
    lon_<longitude>_and_lat_<latitude>

    Parameters
    ----------
    lon: float
        the longitude of the attraction

    lat: float
        the latitude of the attraction

    Returns
    -------
    str
    '''

    return f"lon_{str(lon)}_and_lat_{str(lat)}"


def get_city_attractions_info(city_name, attraction_type, dict_for_location):
    ''' get the attraction of the city

    This function takes in the city name, attraction type, and the pre-stored
    dictionary for location of the city. Then it uses OpenTripMap API (url:
    https://opentripmap.io/product) to get the specific attraction type in the
    specific city

    Parameters
    ----------
    city_name: str
        the name of the city

    attraction_type: str
        the attraction type interested in the given city

    dict_for_location: dict
        the dictionary containing key as city names, and value as city locations
        this dictionary is constructed in advance
    Returns
    -------
    list
    '''

    file_name = 'city_location_attraction.json'
    cache_dict = open_cache(file_name)
    unique_name = generate_unique_city_attraction_name(city_name, attraction_type)
    if unique_name in cache_dict:
        #print('using cache to get city attractions!')
        return cache_dict[unique_name]
    else:
        #print('getting the data from api to get city attraction!')
        # firstly, get the radians for search from database, this parameter
        # depends on the size of the city interested, so we scraped the city data
        # if the city size is smaller than the smallest city in our database
        # we will use the data of the smallest city, 196, to determine the
        # characteristic searching radius
        conn = sqlite3.connect('../my_data_base/airport_database.sqlite')
        cur = conn.cursor()
        name_use = city_name.strip().lower().title()
        query = f'SELECT * FROM cities_by_area WHERE CityName = "{name_use}"'
        cur.execute(query)
        cur_list = list(cur)
        #print(cur_list)
        if len(cur_list) > 0:
            search_radius = round((cur_list[0][3])**0.5, 3) * 1000
            # print('xx')
        else:
            search_radius = 14 * 1000
        conn.close()
        if city_name in dict_for_location:
            base_url_for_city_attr = 'https://api.opentripmap.com/0.1/en/places/radius'
            params = {'radius': search_radius,
                      "lat": dict_for_location[city_name]['position']['lat'],
                      "lon": dict_for_location[city_name]['position']['lon'],
                      'format': 'json',
                      'apikey': secrets.opentripmap_api_key,
                      'limit': 10,
                      'kinds': attraction_type, }
            print(search_radius)
            rp = requests.get(base_url_for_city_attr, params)
            rp_json = rp.json()
            cache_dict[unique_name] = rp_json
            save_cache(cache_dict, file_name)
            return rp_json
        else:
            #print("your input is not a valid US city!")
            return []


def get_weather_prediction(city_name, dict_for_location):
    ''' get the weather prediction of the given city

    This function takes in the city name, and the pre-stored dictionary for
    location of the city. Then it uses Weather Unlocked API (url:
    https://developer.weatherunlocked.com/) to get the weather of the given city

    Parameters
    ----------
    city_name: str
        the name of the city

    dict_for_location: dict
        the dictionary containing key as city names, and value as city locations
        this dictionary is constructed in advance
    Returns
    -------
    list
    '''

    # dynamic, we will not use cache
    if city_name in dict_for_location:
        base_url = 'http://api.weatherunlocked.com/api'
        use_type = '/forecast'
        temp_lon = dict_for_location[city_name]['position']['lon']
        temp_lat = dict_for_location[city_name]['position']['lat']
        location = f'/{temp_lat},{temp_lon}'
        paras = {
            'app_id': secrets.weatherunlocked_api_id,
            'app_key': secrets.weatherunlocked_api_key,
        }
        url = base_url + use_type + location
        rep = requests.get(url, paras)
        rep_json = rep.json()
        return rep_json['Days']
    else:
        return []


def get_hotels(attr_lon, attr_lat):
    ''' get the hotel given the longitude and the latitude

    This function takes in the longitude and latitude of a location, and get
    the hotels near this location using Yelp Fusion API (url:
    https://www.yelp.com/developers/documentation/v3)

    Parameters
    ----------
    attr_lon: float
        longitude of the location

    attr_lat: float
        latitude of the location

    Returns
    -------
    dict
    '''

    filename = 'hotels_cache.json'
    cache_dict = open_cache(filename)
    unique_name = generate_unique_hotel_name(attr_lon, attr_lat)
    if unique_name in cache_dict:
        print('cache')
        return cache_dict[unique_name]
    else:
        print('fetch')
        base_url = 'https://api.yelp.com/v3/businesses/search'
        params = {'latitude': attr_lat,
                  "longitude": attr_lon,
                  'radius': 3000,
                  'categories': 'hotels'}
        headers = {'Authorization': f'Bearer {secrets.yelp_api_key}'}
        rep = requests.get(url=base_url, headers=headers, params=params).json()
        cache_dict[unique_name] = rep
        save_cache(cache_dict, filename)
        return rep


if __name__ == '__main__':
    attractions_list = []
    hotel_list = []
    while True:
        if attractions_list == []:
            my_city = input('Which city is your destination? "exit" to end the program').strip().lower()
            if my_city == "exit":
                break
            else:
                while True:
                    attraction_type_search = input(
                        'What kind of attraction do yo want to search? input a number between 1 to 28').strip()
                    if attraction_type_search.isnumeric():
                        if 1 <= int(attraction_type_search) <= 28:
                            break
                        else:
                            print('you should input a number between 1 and 28!')
                    else:
                        print('you should input a number!!')

                index = int(attraction_type_search)
                my_city_loc_dict = get_city_location_info(my_city)
                print(my_city_loc_dict)
                my_city_attr_list = get_city_attractions_info(my_city,
                                                              attraction_types_to_choose[index - 1],
                                                              open_cache('city_location.json'))
                my_city_weather = get_weather_prediction(my_city, open_cache('city_location.json'))
                print('+____________________+')
                #print(my_city_attr_list)

                if my_city_loc_dict != {}:
                    temp_city = CityAttrInfo(my_city,
                                             attraction_types_to_choose[index - 1],
                                             my_city_attr_list)
                    print(temp_city.info())
                    #print(temp_city.attractions)
                    #print(type(temp_city.attractions))
                    num_of_attr = len(temp_city.attractions)
                    print(num_of_attr)
                    print(f'temperature in {my_city}')
                    print('min_temp:', my_city_weather[2]['temp_min_c'], 'max_temp', my_city_weather[1]['temp_max_c'])
                    if num_of_attr == 0:
                        print(f'the input city {my_city} does not have {attraction_types_to_choose[index-1]}')
                        attractions_list = []
                        print('cannot have choice for hotels!!!')
                    else:
                        attractions_list = []
                        for i in range(num_of_attr):
                            temp_attraction = Attraction(temp_city.attractions[i]['name'],
                                                         temp_city.attractions[i]['point']['lon'],
                                                         temp_city.attractions[i]['point']['lat'],
                                                         temp_city.attractions[i]['rate'])
                            #print(('[' + str(i+1) + ']').ljust(5), end='')
                            #print(temp_attraction.info())
                            attractions_list.append(temp_attraction)
                    # print('min_temp:',my_city_weather[2]['temp_min_c'], 'max_temp', my_city_weather[1]['temp_max_c'])

                else:
                    print('cannot establish the city instance!')
                    print(my_city_weather)

                print(len(open_cache('city_location.json')))
                print(len(open_cache('city_location_attraction.json')))


        if attractions_list != []:
            if hotel_list == []:
                for i in range(len(attractions_list)):
                    print(('[' + str(i+1) + ']').ljust(5), end='')
                    print(attractions_list[i].info())
                query_hotels_nearby = input('you want hotels near which attraction?')
                if query_hotels_nearby.strip().isnumeric():
                    if 0 < int(query_hotels_nearby.strip()) <= len(attractions_list):
                        attraction_instance_picked = attractions_list[int(query_hotels_nearby.strip()) - 1]
                        print(f'now search for the hotels near {attraction_instance_picked.attr_name}...')
                        hotels_response = get_hotels(attraction_instance_picked.attr_lon,
                                                     attraction_instance_picked.attr_lat)
                        total_hotels = len(hotels_response['businesses'])
                        # print(hotels_response)
                        if total_hotels == 0:
                            hotel_list = []
                            print(f'no hotels near the attraction {attraction_instance_picked.attr_name}')
                        else:
                            hotel_list = []
                            for i in range(total_hotels):
                                hotel_name = hotels_response['businesses'][i]['name']
                                try:
                                    hotel_price = hotels_response['businesses'][i]['price']
                                except:
                                    hotel_price = 'not provided'
                                hotel_rating = hotels_response['businesses'][i]['rating']
                                hotel_url = hotels_response['businesses'][i]['url']
                                hotel_reviews = hotels_response['businesses'][i]['review_count']
                                hotel_phone = hotels_response['businesses'][i]['display_phone']
                                temp_hotel = Hotel(hotel_name,
                                                   hotel_price,
                                                   hotel_rating,
                                                   hotel_url,
                                                   hotel_reviews,
                                                   hotel_phone)
                                hotel_list.append(temp_hotel)

                    else:
                        print(f'please input a positive number less than or equal to {len(attractions_list)}')
                elif query_hotels_nearby.strip().lower() == "exit":
                    break
                elif query_hotels_nearby.strip().lower() == "back":
                    attractions_list = []
                else:
                    print('you should input a valid number, "exit" or "back" here!')

            if hotel_list != []:
                for i in range(len(hotel_list)):
                    print(('[' + str(i + 1) + ']').ljust(5), end='')
                    print(hotel_list[i].info())
                query_hotels = input('you want to search which hotel?')
                if query_hotels.strip().isnumeric():
                    if 0 < int(query_hotels.strip()) <= len(hotel_list):
                        hotel_instance_picked = hotel_list[int(query_hotels.strip()) - 1]
                        print(f'now search for the hotel {hotel_instance_picked.name}...')
                        #print(hotel_instance_picked.url)
                        webbrowser.open(hotel_instance_picked.url)
                    else:
                        print(f'please input a positive number less than or equal to {len(hotel_list)}')
                elif query_hotels.strip().lower() == "exit":
                    break
                elif query_hotels.strip().lower() == "back":
                    hotel_list = []
                else:
                    print('you should input a valid number, "exit" or "back" here!!!')