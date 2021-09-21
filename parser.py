import requests
from bs4 import BeautifulSoup
import lxml
import json
import os

HEADERS = {
    'Accept': '*/*',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.2.381 Yowser/2.5 Safari/537.36'
}

#Creating the "data" folder if it's not in the current directory
if not os.path.isdir("data"):
     os.mkdir("data")
     print('\n' + '#' * 34)
     print('The folder "data" will be created!')
     print('#' * 34 + '\n')

#Collecting links from all festivals
fests_urls_list = []
for i in range (0, 96, 24):
    url = f'https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=&to_date=&maxprice=500&o={i}&bannertitle=October'
    
    req = requests.get(url = url, headers = HEADERS)

    json_data = json.loads(req.text)
    html_response = json_data['html']

    #Saving pages with a list of festivals
    with open(f'data/index{i}.html', 'w') as file:
        file.write(html_response)

    with open(f'data/index{i}.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    cards = soup.find_all('a', class_ = 'card-details-link')

    for link in cards:
        fest_url = 'https://www.skiddle.com' + link.get('href')
        fests_urls_list.append(fest_url)

count = 0
#Collecting information from festivals
fest_result_list = []
for url in fests_urls_list:
    count += 1
    print(f'Iteration №{count} = {url}')
    req = requests.get(url = url, headers = HEADERS)

    try:
        soup = BeautifulSoup(req.text, 'lxml')
        fest_info = soup.find('div', class_ = 'top-info-cont')

        fest_name = fest_info.find('h1').text.strip()
        fest_date = fest_info.find('h3').text.strip()
        fest_location_url = 'https://www.skiddle.com' + fest_info.find('a', class_ = 'tc-white').get('href')
        
        #Getting contact details and information
        req = requests.get(url = fest_location_url, headers = HEADERS)
        soup = BeautifulSoup(req.text, 'lxml')

        contact_details = soup.find('h2', string = 'Venue contact details and info').find_next()
        items = [item.text for item in contact_details.find_all('p')]
        
        contact_details_dict = {}
        for contact_detail in items:
            contact_detail_list = contact_detail.split(':')

            if len(contact_detail_list) == 3:
                contact_details_dict[contact_detail_list[0].strip()] = contact_detail_list[1].strip() + ':' + contact_detail_list[2].strip()
            else:
                contact_details_dict[contact_detail_list[0].strip()] = contact_detail_list[1].strip()
            
        fest_result_list.append(
            {
                'Festival name': fest_name,
                'Festival date': fest_date,
                'Contacts data': contact_details_dict
            }
        )

    except Exception as error:
        print('There was some error: ')
        print(error)

#Deleting the old file "festivals_results.json" to avoid repeating old data
if os.path.isfile('festivals_results.json'):
    os.remove('festivals_results.json')
    print('\n' + '#' * 55)
    print('The old file "festivals_results.json" has been deleted!\nA new file will be created!')
    print('#' * 55 + '\n')
else:
    print('\n' + '#' * 50)
    print('The file "festivals_results.json" will be created!')
    print('#' * 50 + '\n')

#Saving festivals data to a json file
with open('festivals_results.json', 'a', encoding = 'utf-8') as file:
    json.dump(fest_result_list, file, indent = 4, ensure_ascii = False)