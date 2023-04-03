import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os

import json
  

def get_soup():

    #url of the page we want to scrape
    url = "https://www.wm.edu/about/visiting/campusmap/academic/index.php"
    
    # initiating the webdriver. Parameter includes the path of the webdriver.
    driver = webdriver.Chrome('./chromedriver') 
    driver.get(url) 

    time.sleep(3) 

    html = driver.page_source
    driver.close()

    buildings = []
    
    # Now, we could simply apply bs4 to html variable
    soup = BeautifulSoup(html, "html.parser")
    map_results = soup.find_all('ul', class_='map_results')[0]
    list_elements = map_results.find_all('li')
    print(list_elements)
    for list in list_elements:
        print('Scraping', list)
        ref = list.find('a')
        sub_url = ref['href']
        #print(sub_url)
        true_url = f'https://www.wm.edu{sub_url}'
        #print(true_url)

        driver = webdriver.Chrome('./chromedriver') 
        driver.get(true_url) 

        time.sleep(4) 

        html = driver.page_source
        driver.close()

        sub_soup = BeautifulSoup(html, "html.parser")
        title = sub_soup.find('h1', class_='m-title__main-title').text
        address = sub_soup.find('p', class_='map_address').get_text(separator="<br\>").replace('<br\>', ' ')
        print('Title and address', title, address)

        building_dict = {
            'BUILDING_NAME': title,
            'BUILDING_ADDRESS': address
        }

        buildings.append(building_dict)
    
    dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir, 'academic_buildings.json'), 'w') as out:
        out.write(str(buildings))


    print('FINISHED SCRAPING')

    



        #print(list.prettify())

get_soup()
