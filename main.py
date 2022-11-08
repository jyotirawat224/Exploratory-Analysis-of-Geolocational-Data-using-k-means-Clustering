import json
import pandas as pd
from pandas.io.json import json_normalize
import requests
from tabulate import tabulate
from sklearn.cluster import KMeans
import random
import numpy as np
import pandas as pd
import folium

# Fetching data form HERE API
def classify(city,lati, longi):
    la = lati
    ln = longi
    city = city
    print(la,ln)
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        lati, longi, 10000, 'apartment')
    data = requests.get(url).json()
    #print(data)
    d = json_normalize(data['items'])
    d.to_csv('ap.csv')
    #print(d['title'])

    # Cleaning API data
    d2 = d[['title', 'address.label', 'distance', 'access', 'position.lat', 'position.lng', 'address.postalCode', 'id']]
    d2.to_csv('ap.csv')
    d2.dropna(inplace=True)
    # Counting no. of cafes, department stores and gyms near apartments around IIT Bombay
    df_final = d2[['position.lat', 'position.lng']]

    CafeList = []
    DepList = []
    GymList = []
    latitudes = list(d2['position.lat'])
    longitudes = list(d2['position.lng'])
    for lat, lng in zip(latitudes, longitudes):
        radius = '1000'  # Set the radius to 1000 metres
        latitude = lat
        longitude = lng

        search_query = 'cafe'  # Search for any cafes
        url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
            latitude, longitude, radius, search_query)
        results = requests.get(url).json()
        venues = json_normalize(results['items'])
        if venues.empty:
            CafeList.append(0)
        else:
            print(venues['title'])
            CafeList.append(venues['title'].count())

        search_query = 'gym'  # Search for any gyms
        url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
            latitude, longitude, radius, search_query)
        results = requests.get(url).json()
        venues = json_normalize(results['items'])
        GymList.append(venues['title'].count())

        search_query = 'department-store'  # search for supermarkets
        url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
            latitude, longitude, radius, search_query)
        results = requests.get(url).json()
        venues = json_normalize(results['items'])
        DepList.append(venues['title'].count())

    df_final['Cafes'] = CafeList
    df_final['Department Stores'] = DepList
    df_final['Gyms'] = GymList

    print(tabulate(df_final, headers='keys', tablefmt='github'))

    # Run K-means clustering on dataframe
    kclusters = 3

    kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_final)
    df_final['Cluster'] = kmeans.labels_
    df_final['Cluster'] = df_final['Cluster'].apply(str)

    print(tabulate(df_final, headers='keys', tablefmt='github'))

    # Plotting clustered locations on map using Folium

    # define coordinates of the college
    map_bom = folium.Map(location=[la, ln], zoom_start=12)

    # instantiate a feature group for the incidents in the dataframe
    locations = folium.map.FeatureGroup()


    # set color scheme for the clusters
    def color_producer(cluster):
        if cluster == '0':
            return 'green'
        elif cluster == '1':
            return 'orange'
        else:
            return 'red'


    latitudes = list(df_final['position.lat'])
    longitudes = list(df_final['position.lng'])
    labels = list(df_final['Cluster'])
    names = list(d2['title'])
    for lat, lng, label, names in zip(latitudes, longitudes, labels, names):
        folium.CircleMarker(
            [lat, lng],
            fill=True,
            fill_opacity=1,
            popup=folium.Popup(names, max_width=300),
            radius=5,
            color=color_producer(label)
        ).add_to(map_bom)

    # add locations to map
    map_bom.add_child(locations)
    folium.Marker([la, ln], popup=city).add_to(map_bom)

    # saving the map
    return map_bom.save("templates/map.html")

#map_bom