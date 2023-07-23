from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import requests
import csv


def try_to_load(operation):
    a = True
    while a:
        try:
            operation
            a = False
            return
        except requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout:
            continue

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}
# url must be a category page that contain a list of same product.ex smart phone, bicycle
URL = 'https://www.alibaba.com/catalog/bicycle_cid201588401?spm=a2700.details.0.0.52261d6eaCrjJp'

# force driver to run in background
Options = Options()
Options.headless = True
chrome_driver_path = Service("C:\chromedriver_win32\chromedriver.exe")
driver = webdriver.Chrome(options=Options,service=chrome_driver_path)

try_to_load(driver.get(URL))
sleep(10)

##____________________________________
# get links in page,each link represent a product, all link have same category
soup = BeautifulSoup(driver.page_source,'lxml')
link_elements = soup.select('.app-organic-search__list h2 a',limit=15)

all_links = []
for link_el in link_elements:
    href = link_el["href"][2:]
    all_links.append('https://'+href)

##____________________________________
all_table_dictionary = []
for i in range(len(all_links)):
    print(f'______________________________Geting {i+1}th Product detail___________________________________')
    #try to open url with selenium(using selenium, page will compeletly load 
    #  this way we can get all html code without loosing any line )
    try_to_load(driver.get(all_links[i]))
    sleep(10)

    #make html soup in oder to get items
    soup = BeautifulSoup(driver.page_source,'lxml')
    main_screen = soup.select('.main-screen')
    #get title and price of product
    title = soup.select('.main-screen .product-title h1')[0].get_text()
    price = soup.select('.main-screen .price')[0].get_text()

    if i==0:
        # make a list of items and add title item and price item to it 
        # then make a fieldname dictionary(key=items list,value=none) to use for writing file
        names = soup.select('dl dt span')
        main_names_list = [span.get_text().split(':')[0] for span in names]
        main_names_list[0:0] = ['title','price']
        main_names = dict.fromkeys(main_names_list,"None")

    # make a list of items,add title and price string ,make a list of value and add title and price of product
    names = soup.select('dl dt span')
    name_text = [span.get_text().split(':')[0] for span in names]
    name_text[0:0] = ['title','price']
    values = soup.select('dl dd div')
    value_text = [div.get_text() for div in values]
    value_text[0:0] = [title,price]

    # make a dictionary of item name and value and append to all_table_dictionary
    table_dic = dict(zip(name_text, value_text))
    all_table_dictionary.append(table_dic)

    # in each product if we had new item we must add it filed name 
    # otherwise file can't be create(for all key in row must have corresponding key in filed name)
    # we add new key to filename variable
    for key in name_text:
        if key not in main_names.items():
            main_names[key] = 'none'

#and finally we have a list of dictionary ,each dictionary contain all of item with it's value for a product
# we loop through all dictionary and add then to file
with open('files.csv','w',newline='') as data:
    writer = csv.DictWriter(data, fieldnames=main_names)
    writer.writeheader()
    for dic in all_table_dictionary:
        writer.writerow(main_names | dic)
    
    



