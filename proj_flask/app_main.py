from flask import Flask, request, render_template
import requests
import plotly.graph_objects as go
import json
import sqlite3
import pandas as pd
import secrets


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


class CityWeather:
    '''a city with weather

    Instance Attributes
    -------------------
    city_name: str
        the name of the city

    json_file: list
        a list from json that contains the weather of the city in the
        following week
    '''

    def __init__(self, city_name, json_file):
        self.name = city_name
        self.city_weather_list = json_file

    def info(self):
        text_to_print = f"weather of {self.name}"
        return text_to_print


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
        conn = sqlite3.connect('./database/airport_database.sqlite')
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
                      'limit': 20,
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


def plot_attractions_on_map(center, attrs_to_plot):
    ''' plot the attractions around a specified center on map using plotly

    By applying package plotly, this function plots the attractions around the
    given center on map using mapbox. Token is required for this process and is
    contained in the secrets.py file.

    Parameters
    ----------
    center: dict
        a dictionary containing the longitude and latitude information of the
        center of the map to show

    attrs_to_plot:list
        a list containing the attractions, and each attraction in the list
        is a dictionary, containing the longitude and latitude of the
        attraction

    Returns
    -------
        json form of the plot, for the template to render later
    '''

    data_set = []
    for element in attrs_to_plot:
        data_set.append([element['attr_name'], element['lon'], element['lat']])
    attractions = pd.DataFrame(data_set, columns=['name', 'lon', 'lat'])
    fig = go.Figure(go.Scattermapbox(
        lat=attractions.lat,
        lon=attractions.lon,
        marker=go.scattermapbox.Marker(
            size=12,
            color='red',
            opacity=0.8,
            symbol='circle',
        ),
        text=attractions.name,
        textfont={'size': 16},
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=secrets.mapbox_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=center['lat'],
                lon=center['lon']
            ),
            pitch=20,
            zoom=10,
        )
    )
    return fig.to_json()


def plot_hotels_price_and_rating(hotel_list):
    ''' plot the hotels information on a bar plot using plotly

    By applying package plotly, this function plots the hotels near the
    selected attraction in hotel ratings and hotel prices on a bar plot to
    help the users to choose the hotels

    Parameters
    ----------
    hotel_list: list
        a list of hotels, each element in the list is a dictionary, containing
        the information of hotel name, hotel price and hotel rating

    Returns
    -------
        json form of the plot, for the template to render later
    '''

    num_of_hotels = len(hotel_list)
    y = []
    x1 = []
    x1_text = []
    x2 = []
    x2_text = []
    for i in range(num_of_hotels):
        #y.append(str(i+1))
        y.append(hotel_list[i]['hotel_name'])
        x1.append(float(hotel_list[i]['hotel_rating']))
        x1_text.append(hotel_list[i]['hotel_name'] + ':' + f"rating {hotel_list[i]['hotel_rating']}")
        if hotel_list[i]['hotel_price'] != 'not provided':
            x2.append(len(hotel_list[i]['hotel_price']))
        else:
            # if the price is 'not provided', we give the value 0 to plot it
            x2.append(0)
        x2_text.append(hotel_list[i]['hotel_name'] + ':' + f"price {hotel_list[i]['hotel_price']}")
    trace_1 = go.Bar(
        x=y,
        y=x1,
        name="hotel rating",
        hovertext=x1_text,
        # orientation='h',
        marker={'color': 'red'}
    )
    trace_2 = go.Bar(
        x=y,
        y=x2,
        name="hotel price",
        hovertext=x2_text,
        # orientation='h',
        marker={'color': 'blue'}
    )
    trace = [trace_1, trace_2]
    figure = go.Figure(data=trace)
    return figure.to_json()


app = Flask(__name__)

@app.route('/')
def my_index():
    return render_template('index.html')


@app.route('/buying_air_tickets', methods=['POST'])
def get_air_tickets():
    place_of_departure = request.form['dep_city_name']
    place_of_destination = request.form["des_city_name"]
    date_of_flight = request.form['day']
    month_of_flight = request.form['month']
    conn = sqlite3.connect('./database/airport_database.sqlite')
    cur = conn.cursor()

    name_use = place_of_departure.strip().lower().title()
    query = f'''
    SELECT * FROM airports JOIN states on airports.AirportState=states.StateCode 
    WHERE AirportCity="{name_use}"
    '''
    cur.execute(query)
    dep_airport = list(cur)

    name_use = place_of_destination.strip().lower().title()
    query = f'''
    SELECT * FROM airports JOIN states on airports.AirportState=states.StateCode 
    WHERE AirportCity="{name_use}"
    '''
    cur.execute(query)
    des_airport = list(cur)

    if dep_airport == [] or des_airport == []:
        return f"<h2>Either the departure place or the destination place does not have airport in our database</h2>" \
               f"<p>Return <a href='/'>Home Page</a></p>"
    else:
        month = month_of_flight
        day = date_of_flight
        dep_airport_city = dep_airport[0][3]
        dep_airport_state = dep_airport[0][6]
        dep_airport_name = dep_airport[0][2]
        dep_airport_code = dep_airport[0][1]
        des_airport_city = des_airport[0][3]
        des_airport_state = des_airport[0][6]
        des_airport_name = des_airport[0][2]
        des_airport_code = des_airport[0][1]
        base_url_1 = 'https://www.skyscanner.com/transport/flights/'
        url_modified = dep_airport_code.lower()+'/'+des_airport_code.lower()+'/'+'21'+month+day
        base_url_2 = '/?adults=1&adultsv2=1&cabinclass=economy&children=0&childrenv2=&destinationentityid=27539525&inboundaltsenabled=false&infants=0&originentityid=27536211&outboundaltsenabled=false&preferdirects=false&preferflexible=false&ref=home&rtn=0'
        ticket_url= base_url_1 + url_modified + base_url_2
        return render_template('buy_tickets_having_both_airports.html',
                               ticket_month=month,
                               ticket_date=day,
                               dep_city=dep_airport_city,
                               dep_state=dep_airport_state,
                               dep_airport_name=dep_airport_name,
                               dep_airport_code=dep_airport_code,
                               des_city=des_airport_city,
                               des_state=des_airport_state,
                               des_airport_name=des_airport_name,
                               des_airport_code=des_airport_code,
                               ticket_url=ticket_url)


@app.route('/attractions_and_weathers_city_exist_attractions_not_empty', methods=['GET', 'POST'])
def show_attractions_and_weathers():
    my_city = request.form['city_name'].strip().lower()
    attraction = request.form['attraction_type']
    show_type = request.form['presentation_type']
    if my_city == '':
        return f"<h1>The city you input is empty!!</h1>" \
               f"<p>Return <a href='/'>Home Page</a></p>"
    else:
        my_city_loc_dict = get_city_location_info(my_city)
        if my_city_loc_dict == {}:
            return f"<h1>we cannot find '{my_city}' in the US</h1>" \
                   f"<p>Return <a href='/'>Home Page</a></p>"
        else:
            my_city_attr_list = get_city_attractions_info(my_city,
                                                          attraction,
                                                          open_cache('city_location.json'))
            if my_city_attr_list == []:
                return f"<h1> city '{my_city}' does not contain any {attraction}," \
                       f"please try another attraction in '{my_city}'</h1>"\
                       f"<p>Return <a href='/'>Home Page</a></p>"
            else:
                # get the weather
                my_city_weather = get_weather_prediction(my_city, open_cache('city_location.json'))
                temp_city_weather = CityWeather(my_city, my_city_weather)
                for element in temp_city_weather.city_weather_list:
                    sub_elements = element['Timeframes']
                    for time_point in sub_elements:
                        time_str = str(time_point['time'])
                        time_point['time'] = time_str[0:-2] + ':' + time_str[-2:]
                        icon_str = time_point['wx_icon']
                        time_point['wx_icon'] = 'static/pictures/' + icon_str.replace('gif', 'png')
                # get the attractions
                temp_city = CityAttrInfo(my_city,
                                         attraction,
                                         my_city_attr_list)
                num_of_attr = len(temp_city.attractions)
                attractions_list = []
                attractions_str = []
                attractions_position = []
                for i in range(num_of_attr):
                    name_to_modify_list  = temp_city.attractions[i]['name'].split("'")
                    name_modified = ' '.join(name_to_modify_list)
                    temp_attraction = Attraction(name_modified,
                                                 temp_city.attractions[i]['point']['lon'],
                                                 temp_city.attractions[i]['point']['lat'],
                                                 temp_city.attractions[i]['rate'])
                    # print(('[' + str(i+1) + ']').ljust(5), end='')
                    # print(temp_attraction.info())
                    attractions_list.append(temp_attraction)
                    attractions_str.append(temp_attraction.info())
                    attractions_position.append({'lat': temp_attraction.attr_lat,
                                                 'lon': temp_attraction.attr_lon,
                                                 'attr_name': temp_attraction.attr_name})

                city_center = open_cache('city_location.json')[my_city]['position']
                figure_json = plot_attractions_on_map(center=city_center, attrs_to_plot=attractions_position)
                return render_template('attractions_and_weathers_city_exist_attractions_not_empty.html',
                                       my_list=temp_city_weather.city_weather_list,
                                       cityname=temp_city_weather.name,
                                       attraction_type=attraction,
                                       attractions_str=attractions_str,
                                       attractions_position=attractions_position,
                                       plot_content=figure_json,
                                       presentation_type=show_type)


@app.route('/find_hotels_exists', methods=['POST'])
def show_hotels():
    try:
        my_position = request.form['attr_choice']
    except:
        return 'You need to select one of the attractions!'
    hotel_present_type = request.form['hotel_presentation_type']
    new_list = my_position.split(',')
    attr_lat = float(new_list[0].strip())
    attr_lon = float(new_list[1].strip())
    attr_name = new_list[2].strip()
    hotels_response = get_hotels(attr_lon, attr_lat)
    total_hotels = len(hotels_response['businesses'])
    if total_hotels == 0:
        return f"<h2>We cannot find any hotels near the attraction you picked," \
               f" Please go back to the previous page and try another one.</h2>" \

    else:
        hotel_list = []
        hotel_info_list = []
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
            temp_hotel_name_without_quotation_list = temp_hotel.name.split("'")
            temp_hotel.name = " ".join(temp_hotel_name_without_quotation_list)
            hotel_info_list.append({'hotel_name': temp_hotel.name,
                                    'hotel_price': temp_hotel.price,
                                    'hotel_rating': temp_hotel.rating,
                                    'hotel_url': temp_hotel.url,
                                    'hotel_reviews': temp_hotel.review_count,
                                    'hotel_number': i + 1})
        figure_json = plot_hotels_price_and_rating(hotel_info_list)
        return render_template('show_hotels.html',
                               hotels=hotel_info_list,
                               num_hotels=len(hotel_info_list),
                               attraction_name=attr_name,
                               plot_content=figure_json,
                               plot_type=hotel_present_type)


if __name__ == '__main__':
    print('starting Flaks app!', app.name)
    app.run(debug=True)