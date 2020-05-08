#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 20:58:49 2020

@author: daria_pirogova
"""
import requests
import re
from bs4 import BeautifulSoup
import json

#there are two categories of items, which include women and men's collections, 
#therefore I have decided to work with the paths to these collection directly instead of trying 
#to collect all links from the website

women_url = 'https://5karmanov.ru/cat/zhenskaya-kollektsiya'
women_new_collection = 'https://5karmanov.ru/cat/novaya-kollektsiya-zhenskaya-odezhda'

men_url = 'https://5karmanov.ru/cat/muzhskaya-kollektsiya'
men_new_collection = 'https://5karmanov.ru/cat/novaya-kollektsiya-dlya-muzhchin'

#extracting the page number
def extracting_page_number(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    my_a = []
    ul = soup.find('ul', attrs={'class' : 'pagination'})
    if ul:
        for a in ul.find_all('a'):
            my_a.append(a.attrs['data-page'])
    return my_a

#extracting item links
def getting_urls(url, number):#women_url, my_a[-2]
    urls = []
    for i in range(1, int(number)):
        p = {'page': i}
        req = requests.get(url, params=p)
        temp_soup = BeautifulSoup(req.content, 'html.parser')
        divs = temp_soup.find_all('div', attrs={'itemprop' : 'itemListElement'})
        for div in divs:
            urls.append('https://5karmanov.ru' + div.find('a').attrs['href'])
    return urls

#extracting new items based on a badge of an item preview
def getting_new_items(url, number):
    new_items = []
    for i in range(1, int(number)):
        p = {'page': i}
        req = requests.get(url, params=p)
        temp_soup = BeautifulSoup(req.content, 'html.parser')
        divs = temp_soup.find_all('div', attrs={'itemprop' : 'itemListElement'})
        for div in divs:
            if div.find('span', attrs = {'class' : 'text'}):
                if div.find('span', attrs = {'class' : 'text'}).text == 'New':
                    new_items.append(url + "/" + div.find('a').attrs['href'])
    return new_items

#extracting new items which are included in the new collection 
def getting_new_collection_items(url, number):
    urls = []
    for i in range(1, int(number)):
        p = {'page': i}
        req = requests.get(url, params=p)
        temp_soup = BeautifulSoup(req.content, 'html.parser')
        divs = temp_soup.find_all('div', attrs={'itemprop' : 'itemListElement'})
        for div in divs:
            urls.append(url + "/" + div.find('a').attrs['href'])
    return urls
    
   
#creating a list of tuples which would include a size and and its category
#some size categories were not taken into account as the website provides different variations of them
#and sometimes it can be hard to categorize all of them
def extracting_sizes(soup):    
    inter = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '2XL', '3XL', '4XL', '5XL']
    ru = ['36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56']
    sizes = [] 
    if soup.find('div', {'class' : 'size-number'}):
        for label in soup.find('div', {'class' : 'size-number'}).find_all('label'):
            if label.find('span', {'class' : 'label-text'}).text in inter:
                sizes.append((label.find('span', {'class' : 'label-text'}).text, 'INT'))
            elif len(label.find('span', {'class' : 'label-text'}).text) > 4 and label.find('span', {'class' : 'label-text'}).text[0] == 'W' and label.find('span', {'class' : 'label-text'}).text[4] == 'L':
                sizes.append((label.find('span', {'class' : 'label-text'}).text, 'INCH'))
            elif label.find('span', {'class' : 'label-text'}).text in ru:
                sizes.append((label.find('span', {'class' : 'label-text'}).text, 'RU'))
            elif len(label.find('span', {'class' : 'label-text'}).text) > 0 and label.find('span', {'class' : 'label-text'}).text[0] == '2':
                sizes.append((label.find('span', {'class' : 'label-text'}).text, 'cm'))
            else:
                sizes.append(label.find('span', {'class' : 'label-text'}).text)           
    else:
        sizes.append('One Size')
    return sizes
  
#extracting the availability of an intem
def extracting_availability(soup):
    availabilities = []    
    if soup.find('div', {'class' : 'size-number'}):
        for label in soup.find('div', {'class' : 'size-number'}).find_all('label'):
            if len(label.attrs['class']) > 1 and label.attrs['class'][1] == 'disabled':
                availabilities.append((label.find('span', {'class' : 'label-text'}).text, 'None'))
            else:
                availabilities.append((label.find('span', {'class' : 'label-text'}).text, 'Available'))
    return availabilities

#extracting the color of the item
def finding_color(page):
    spans = []
    des = page.find('div', attrs={'itemprop' : 'description'})
    for span in des.find_all('span', attrs={'class' : 'value'}):
        spans.append(span.text)
    if len(spans) > 1:
        return spans[1]
    else:
        return None

#extracting fabric
def extracting_fabric(page):
    des = page.find('div', attrs={'itemprop' : 'description'})
    if des.find('span', attrs={'class' : 'value'}):
        return des.find('span', attrs={'class' : 'value'}).text
    else:
        return None

def extracting_vendor_code(page):
    if page.find('div', attrs={'class': 'vendorCode'}):
        return page.find('div', attrs={'class': 'vendorCode'}).find('span').text.split()[1]

def extracting_brand(page):
    return(page.find('a', attrs={'itemprop' : 'brand'}).text)

def extracting_categories(page):
    categories = []   
    lis = page.find_all('li', attrs={'itemprop' : 'itemListElement'})
    for li in lis:
        for a in li.find('a', attrs={'itemprop' : 'item'}):
            categories.append(a.text)
    return categories[1:-1]

def extracting_images(page):
    images_urls = []
    images = page.findAll('img', attrs={'itemprop' : 'image'})
    for image in images:
        images_urls.append(image.attrs['src'])
    return images_urls

#extracting the description of the item
def extracting_characteristics(page):
    characteristics = []
    if page.find('div', attrs={'class' : 'body', 'itemprop' : 'description'}):
        divs = page.find('div', attrs={'class' : 'body', 'itemprop' : 'description'}).find_all('div')
        for div in divs:
            for child in div.find_all('li'):
                characteristics.append(child.text)
    return characteristics

def extracting_name(page):
    name = page.find('meta', attrs={'itemprop' : 'name'})
    return(name.attrs['content'])

#there was no category labeld as a gender 
#therefore I took this way to determinate the gender category of an item
def extracting_gender(page):
    my_list = extracting_categories(page)
    if len(my_list) > 0:
        if my_list[0].startswith('Жен') or my_list[1].startswith('Жен'):
            return ('Женский')
        elif my_list[0].startswith('Муж') or my_list[1].startswith('Муж'):
            return ('Мужской')
        else:
            return None

def extracting_old_price(soup):
    if soup.find('span', {'class': 'old-price'}):
        return soup.find('span', {'class': 'old-price'}).text[:-2]
    else:
        return None

#creating a dictionary which afterwords would be converted to json and printed
def creating_dic(page, new_coll_page):
    euro = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '2XL']
    req = requests.get(page)
    temp_soup = BeautifulSoup(req.content, 'html.parser')
    pages = extracting_page_number(page)
    if len(pages) > 2:
        items = getting_urls(page, pages[-2])
        new_items_frst = getting_new_items(page, pages[-2])
        new_items_scnd = getting_new_collection_items(new_coll_page, pages[-2])
        for item in items:
            main = {}
            data = {}
            main.update({"url":"https://5karmanov.ru"})
            main.update({"company":"5karmanov"})
            main.update({"currencies":[["RUR","1"]]})
            main.update({"name":"5karmanov"})
            data.update({"shop_info" : main})
            offer = {}
            param = {}
            new_req = requests.get(item)
            tmp_sp = BeautifulSoup(new_req.content, 'html.parser')
            sizes = extracting_sizes(tmp_sp)
            availability = extracting_availability(tmp_sp)
            for size in sizes:
                if len(size) > 0:
                    if size[0] == availability[0] and availability[1] == 'Available':
                        offer.update({'available' : 'true'})
                    else:
                        offer.update({'available' : 'false'})
                param.update({'размер' : size})    
                offer.update({"old_price" : extracting_old_price(tmp_sp)})
                offer.update({'vendorCode' :  extracting_vendor_code(tmp_sp)})
                offer.update({'vendor' : extracting_brand(tmp_sp)})
                offer.update({'picture' : extracting_images(tmp_sp)})
                offer.update({'name' : extracting_name(tmp_sp)})
                if len(extracting_characteristics(tmp_sp)) > 0:
                    offer.update({'description' : " ".join(extracting_characteristics(tmp_sp))})
                offer.update({'url' : item})
                offer.update({"cuarrencyId" : "RUR"})
                if item in new_items_frst or item in new_items_scnd:
                    param.update({'new' : "1"})
                else:
                    param.update({'new' : "0"})
                    param.update({'color' : finding_color(tmp_sp)})
                    #param.update({'sizes' : extracting_sizes(tmp_sp)})
                param.update({'fabric' : extracting_fabric(tmp_sp)})
                param.update({'categories' : extracting_categories(tmp_sp)})
                param.update({"Возраст": "Взрослый"})
                param.update({'gender' : extracting_gender(tmp_sp)})
                offer.update({'param' : param})
                data.update({'offer' : offer})
                #print(items.index(item))
                print(json.dumps(data, ensure_ascii=False))

#applying the function both to women and men's categories
creating_dic(women_url, women_new_collection)
creating_dic(men_url, men_new_collection)
    
    