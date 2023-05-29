import os
import json
import requests
import folium
from geopy import distance
from flask import Flask

APIKEY = os.environ['APIKEY']


def fetch_coordinates(APIKEY, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": APIKEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    print(found_places)

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def all_incom(i):
    return i.get('distance')


def display_map():
    with open('index.html') as file:
        return file.read()


def func_new():
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        read_file = my_file.read()
        coffee_shops = json.loads(read_file)
        return coffee_shops

def func_coffee(coffee_shops, my_coordinates):
    all_coffees = []
    for coffee in coffee_shops:
        coffees_coordinate = coffee["Latitude_WGS84"], coffee["Longitude_WGS84"]
        one_of_coffee = dict()
        one_of_coffee['title'] = coffee['Name']
        one_of_coffee['distance'] = distance.distance(
          my_coordinates, coffees_coordinate).km
        one_of_coffee['latitude'] = coffee["Latitude_WGS84"]
        one_of_coffee['longitude'] = coffee["Longitude_WGS84"]
        all_coffees.append(one_of_coffee)
    return all_coffees

def main():
    place = input("Где вы находитесь? ")
    my_coordinates = fetch_coordinates(APIKEY, place)
    my_coordinates = my_coordinates[1], my_coordinates[0]

    coffee_shops = func_new()
    
    all_coffees = func_coffee(coffee_shops, my_coordinates)
    #print(all_coffees)

    sorted_coffees = sorted(all_coffees, key=all_incom)
    sorted_coffees = sorted_coffees[:5]

    m = folium.Map(
        location=[my_coordinates[0], my_coordinates[1]], zoom_start=15,
        tiles="Stamen Terrain")
    folium.Marker(
        [my_coordinates[0], my_coordinates[1]], popup="<i>My location</i>",
        tooltip="Моё месторасположение", icon=folium.Icon(color="red")
        ).add_to(m)
    for i in range(0, len(sorted_coffees)):
        folium.Marker(
            [sorted_coffees[i]['latitude'], sorted_coffees[i]['longitude']],
            popup="<i>Сoffee house</i>", tooltip=sorted_coffees[i]['title']
            ).add_to(m)
    m.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'Map_of_coffee', display_map)
    app.run('0.0.0.0')
    main()

if __name__ == '__main__':
    main()
