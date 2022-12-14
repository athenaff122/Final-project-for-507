import requests
from bs4 import BeautifulSoup
import json
import time

scrapping={}
country_list={}
def write_json(filepath, data, encoding='utf-8'):
    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj)


## Make the soup --scrapping the data from Frobes page <2000>
forbes_page_url = "https://www.forbes.com/lists/global2000/?sh=1d4699995ac0"
response = requests.get(forbes_page_url)
print(response)
soup = BeautifulSoup(response.text, 'html.parser')
company_listing_parent = soup.find_all('div')
company_listing_parent2 = soup.find_all(class_='table-row-group') 
rank=1
for div in company_listing_parent2:
    company_listing_divs = div.find_all('a', recursive=False)
    for i in range(len(company_listing_divs)):
        company={}
        company_name=company_listing_divs[i].find('div', class_='organizationName second table-cell name').string
        scrapping[company_name]={}

        # rank=company_listing_divs[i].find('div', class_='rank first table-cell  rank')
        scrapping[company_name]["rank"]=rank
        rank+=1

        country=company_listing_divs[i].find('div', class_='country table-cell country').string
        scrapping[company_name]["country"]=country

        if scrapping[company_name]["country"] not in country_list:
            country_list[scrapping[company_name]["country"]]=[company_name]
        else:
            country_list[scrapping[company_name]["country"]].append(company_name)

        sales=company_listing_divs[i].find('div', class_='revenue table-cell sales').string
        scrapping[company_name]["sales"]=sales
        profit=company_listing_divs[i].find('div', class_='profits table-cell profit').string
        scrapping[company_name]["profit"]=profit
        asset=company_listing_divs[i].find('div', class_='assets table-cell assets').string
        scrapping[company_name]["asset"]=asset
        mkt_value=company_listing_divs[i].find('div', class_='marketValue table-cell market value').string
        scrapping[company_name]["market value"]=mkt_value

# print(scrapping)
# scrapping_json=json.dump(scrapping) ##dump
# print(scrapping_json[0])
# write_json('scrapping.json', scrapping_json)

scrapping = list(scrapping.items())
with open("scrapping_top2000.json", "w") as file:
  json.dump(scrapping, file)


with open("by country_list.json", "w") as file:
  json.dump(country_list, file)

# if __name__=='__main__':
    # print("Q1========================================================================")
    # answer1 = input("We have scrapped the data from <Forbes Global 2000>, which ranks the largest companies in the world using four metrics: sales, profits, assets, and market value. Among all of these compnaies, which company you want to know? please give a number between 1-2000! ")
    # print(scrapping[int(answer1)-1])
    # time.sleep(3)

    # print("Q2========================================================================")
    # print("In order to better analyze the data, we have sort these companies by their country")
    # print("The country lists are: ")
    # print(list(country_list.keys()))
    # answer2 = input("Which country you want to know more? ")
    # print(f"These are the companies in {answer2} in Forbes Top 2000: ")
    # print(country_list[answer2])
    # time.sleep(3)

    # print("Q3========================================================================")
    # print(f"Now we only accpet to search the companies in United states")
    # print(f"These are the companies in United States in Forbes Top 2000: ")
    # print(country_list["United States"])