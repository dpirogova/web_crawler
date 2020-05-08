#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 02:02:50 2020

@author: daria_pirogova
"""

import requests
import re
from bs4 import BeautifulSoup
import json
import pandas as pd

#this url contains all needed information for extractig shops' entities
url = 'https://5karmanov.ru/shops'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

#extracting the nanems of the cities where the shops are located
def extracting_cities(page):
    cities_names = []
    cities = page.find('select', attrs={'name' : 'shop_city'})
    if page.find('select', attrs={'name' : 'shop_city'}):
        for city in cities.findChildren('option'):
            cities_names.append(city.attrs['value'])
    return(cities_names[1:])

cities = extracting_cities(soup)

#extracting jsons which contain all the information we need to create a csv
def extracting_jsons(my_url, list_of_cities):
    my_jsons = []
    p = {'action': 'getPoints', 'ajax': '3'}
    for city in list_of_cities:
        r = requests.get(url + '/' + city, params = p)
        my_jsons.append(json.loads(r.text))
    return my_jsons

def getting_shop_keys(lst):
    shop_keys = []
    for dic in lst:
        for key in dic['list'].keys(): 
            shop_keys.append(key)
    return shop_keys

def extracting_entities(dic, lst, key):
    entities = []
    for number in lst:
        entities.append(dic[number][key]) 
    return entities

shop_ids = getting_shop_keys(extracting_jsons(url, cities))

temp = {}
for el in extracting_jsons(url, cities):
    temp.update(el['list'])

def changing_phone_format(phone):
    new_phone = []
    for el in phone:
        if el != ' ' and el != '(' and el != ')' and el != '-':
            new_phone.append(el)
    return "".join(new_phone)

#creating a dictionary which would be used to create a pandas dataframe
data = {'mall_name' : extracting_entities(temp, shop_ids, 'shop_name'),
        'outlet_id' : extracting_entities(temp, shop_ids, 'info_shop_id'),
        'store_name' : extracting_entities(temp, shop_ids, 'shop_location'),
        'store_phone' : [changing_phone_format(numb) for numb in extracting_entities(temp, shop_ids, 'shop_phone')],
        'store_adress' : extracting_entities(temp, shop_ids, 'shop_address')}

#creating a pandas dataframe
my_dataframe = pd.DataFrame(data, columns=['mall_id', 'mall_name',
                                           'outlet_id', 'store_name', 'store_phone', 'store_adress'])

my_csv = my_dataframe.to_csv(index = None, sep = ';', quotechar = '\'')
print(my_csv)
 