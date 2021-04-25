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


cities = open_cache('city_location.json')
print('+--------------------------------+')
print('# of cities have been searched:', end='')
print(len(cities))

city_attractions = open_cache('city_location_attraction.json')
print('+--------------------------------+')
print('# of attractions in different cities have been searched:', end='')
print(len(city_attractions))

hotels = open_cache('hotels_cache.json')
print('+--------------------------------+')
print('# of hotels near different attractions have been searched:', end='')
print(len(hotels))
