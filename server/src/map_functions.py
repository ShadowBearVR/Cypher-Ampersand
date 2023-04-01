import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests
import googlemaps

from helper_functions import *

## MAPS API FUNCTIONS ##

set_env_vars()
maps_api_key = get_env_var('GOOGLE_MAPS_API_KEY')

def get_travel_time_estimate(mode, lat_1, long_1, lat_2, long_2):
    print('get_travel_time_estimate', mode, lat_1, long_1, lat_2, long_2)

    now = datetime.now()

    loc_1 = f'{lat_1},{long_1}'
    loc_2 = f'{lat_2},{long_2}'

    gmaps = googlemaps.Client(key=maps_api_key)

    directions_result = gmaps.directions(loc_1,
                                         loc_2,
                                         mode=mode,
                                         departure_time=now
                                        )

    travel_time_estimate = directions_result[0]['legs'][0]['duration']['text']

    print('travel_time_estimate', travel_time_estimate)

    return travel_time_estimate

def get_travel_time_estimate(mode, address_1, address_2):
    print('get_travel_time_estimate', mode, address_1, address_2)

    now = datetime.now()

    gmaps = googlemaps.Client(key=maps_api_key)

    directions_result = gmaps.directions(address_1,
                                         address_2,
                                         mode=mode,
                                         departure_time=now
                                        )

    travel_time_estimate = directions_result[0]['legs'][0]['duration']['text']

    print('travel_time_estimate', travel_time_estimate)

    return travel_time_estimate