import folium


def open_file(path):
    """"
    file -> dict
    Return a dictionary made with information in the file.
    """
    f = open(path, encoding='utf-8', errors='ignore')
    data = f.readlines()
    list_with_rows = []
    for i in data:
        i = i.replace('\n', '').split(',')
        list_with_rows.append(i[:2] + [i[-1]])
    new_lst = []
    for i in list_with_rows:
        i = ','.join(i)
        new_lst.append(i)
    new_lst = list(set(new_lst))
    list_with_locations = []
    for i in new_lst:
        i = i.split(',')
        if (i[-1] != "NO DATA") and (type(i[1]) == str):
            list_with_locations.append(i)
    dict_with_years = {}
    for i in list_with_locations:
        if i[1] not in dict_with_years.keys():
            dict_with_years[i[1]] = [[i[0], i[2]]]
        else:
            dict_with_years[i[1]].append([i[0], i[2]])
    return dict_with_years


def find_films_and_locations_by_the_year(year):
    """
    int -> dict
    Return a dictionary with locations as keys and films as values in the certain year.
    """
    dictionary = open_file('locations.csv')
    list_with_data = dictionary[year]
    dict_with_locations = {}
    for i in list_with_data:
        if i[1] not in dict_with_locations.keys():
            dict_with_locations[i[1]] = [i[0]]
        else:
            dict_with_locations[i[1]].append(i[0])
    return dict_with_locations


year = input()

locations = []
location_dict = find_films_and_locations_by_the_year(year)
for i in location_dict.keys():
    locations.append(i)

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
geolocator = Nominatim(timeout=100)
from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
dict_with_location = {}
for point in locations:
    try:
        location = geolocator.geocode(point)
        dict_with_location[(location.latitude, location.longitude)] = location_dict[point]
        if len(dict_with_location) == 1000:
            break
    except AttributeError:
        pass


map = folium.Map(location=[48.314775, 25.082925], zoom_start=2)


def color_creator(films_number):
    """
    int -> str
    Define a color by the number.
    """
    if films_number < 3:
        return "green"
    elif 3 <= films_number <= 10:
        return "yellow"
    else:
        return "red"


fg_pp = folium.FeatureGroup(name="Population")
fg_hc = folium.FeatureGroup(name="Films")

for loc in dict_with_location:
        number_of_films = len(dict_with_location[loc])
        fg_hc.add_child(folium.CircleMarker(location=[loc[0], loc[1]],
                                            radius=10,
                                            popup=', '.join(dict_with_location[loc]),
                                            fill_color=color_creator(number_of_films),
                                            color='blue',
                                            fill_opacity=2))

fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
                             encoding='utf-8-sig').read(),
                             style_function=lambda x: {'fillColor':'green'
    if x['properties']['POP2005'] < 10000000
    else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
    else 'red'}))

map.add_child(fg_pp)
map.add_child(fg_hc)
map.add_child(folium.LayerControl())

map.save('My_world_map_with_films.html')