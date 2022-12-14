import requests
from pandas_datareader import data
# import pandas as pd
# import numpy as np
import datetime
import matplotlib.pyplot as plt
import scrapping as utl
import time
import csv
import collections

Alpha_key = "9CZWI7NQ3IAGIFOO"
Polygon_key = "f2N9IZ6EdkGPmFw_AjGB9Y05p4SppIwp"

#Convert CSV to dictionary
def read_csv_to_dicts(filepath, encoding='utf-8', newline='', delimiter=','):
    with open(filepath, 'r', newline=newline, encoding=encoding) as file_obj:
        reader = csv.DictReader(file_obj, delimiter=delimiter)
        return [line for line in reader]

#Classify the dictionary by industry
def classify_by_industry(data):
    industry_dict=collections.defaultdict(list)
    for dict in data:
        if dict['Sector'] is not None:
            industry_dict[dict['Sector']].append(dict['Symbol'])
    return industry_dict

#find the stock in the same sector
def choose_sector(nasdaq_dict):
    interested_company=input("You can check witht the <scrapping_top2000> file and choose which company you want to know more?")
    for dict in nasdaq_dict:
        if interested_company.lower() in dict["Name"].lower():
            sector=dict["Sector"]
            symbol=dict["Symbol"]
            break
    print(f"According to the Nasdaq public information, it belongs to {sector}")
    return sector,symbol

def search_by_character(keywords):
    '''
    Input: Any character the users are thinking about. For example: APP
    Output: A list of stock's symbol which is in the US market, and the stock symbol is based on input. 
    '''
    Alpha_search_url="https://www.alphavantage.co/query?function=SYMBOL_SEARCH&"
    r = requests.get(f"{Alpha_search_url}keywords={keywords}&apikey={Alpha_key}")
    data = r.json()['bestMatches']
    len_data = len(data)
    print(data)
    if len_data==0: 
        print("There are no stocks that match your search. Please input other character  ")
        keywords=input("What letters you like?Please input more than one letter.(For example: AP)  ")
        search_by_character(keywords)
    else:
        print(f"\nThere are {len_data} stocks that match your search. The stock symbols are ")
        symbol_list=[]
        us_symbol_list=[]
        for i in range(len_data):
            symbol_list.append(data[i]['1. symbol'])
            print(i, data[i]['1. symbol'])
            if data[i]['4. region']=='United States':
                us_symbol_list.append(data[i]['1. symbol'])
        print(symbol_list)
        print("Currently we can only support for the stocks which is in United States market. The stocks currently in US are")
        print(us_symbol_list) 

    return us_symbol_list

def stocks_detail(symbol_list):
    '''
    Input: us_symbol_list; the date which users want to have a look.
    Output: the price detail of the stocks on that date 
    '''
    date = input("Which date's price do you want to see? Please ensure it was a trading date! (For example:2022-11-29)  ")
    stocks_detail_url = "https://api.polygon.io/v2/aggs/ticker/"
    stock_detail=[]
    for stock in symbol_list:
        try:
            r = requests.get(f"{stocks_detail_url}{stock}/range/1/day/{date}/{date}?adjusted=true&sort=asc&limit=120&apiKey={Polygon_key}")
            data = r.json()
            print(data)
            stock_detail.append(data)
        except:
            print(f"{stock} is not active anymore. Will be skipped")
    return stock_detail

def price_tree(stock_detail):
    '''
    input: us_symbol_list;
    output:  a tree in the format of a dictionary, which is classified by price.
    '''
    # priceTree = {'$0-$100': [], '$100-$200': [], '>$200': []}
    priceTree = {'$0-$100': {'$0-$50':[], '$50-$100':[]}, '>$100': {'$100-$200':[], '>$200':[]}}
    price_detail_tree={'$0-$100': {'$0-$50':{}, '$50-$100':{}}, '>$100': {'$100-$200':{}, '>$200':{}}}
    for stock in stock_detail:
        if 'results' not in stock.keys():
            continue
        if stock['results'][0]['o']<=100:
            if 0<stock['results'][0]['o']<=50:
                priceTree['$0-$100']['$0-$50'].append(stock['ticker'])
                price_detail_tree['$0-$100']['$0-$50'][stock['ticker']]=stock['results'][0]
            else:
                priceTree['$0-$100']['$50-$100'].append(stock['ticker'])
                price_detail_tree['$0-$100']['$50-$100'][stock['ticker']]=stock['results'][0]
        else:
            if 100<stock['results'][0]['o']<200:
                priceTree['>$100']['$100-$200'].append(stock['ticker'])
                price_detail_tree['>$100']['$100-$200'][stock['ticker']]=stock['results'][0]
            else:
                priceTree['>$100']['>$200'].append(stock['ticker'])
                price_detail_tree['>$100']['>$200'][stock['ticker']]=stock['results'][0]
    return priceTree, price_detail_tree

    


def choose_stock(priceTree):
    '''
    choose the stock based on the price-tree
    '''
    price_choice1 = input("Which stock price range you want to choose?(Please choose from: $0-$100, >$100) . ")
    if price_choice1 =='$0-$100':
        price_choice2 = input("Which specific stock price range you want to choose(Please choose from: $0-$50, $50-$100)? ")
    elif price_choice1 =='>$100':
        price_choice2 = input("Which specific stock price range you want to choose(Please choose from: $100-$200, >$200)? ")

    price_stock = priceTree[price_choice1][price_choice2]
    # if priceTree[price_choice] is None:
        # price_choice = ("The price you choose is not availbale for these stocks. Please reentry a price range: ")
        # choose_stock(priceTree)
    # price_stock = priceTree[price_choice]
    print(price_stock)
    stock_choice = input(f"These are the stock which price is {price_choice2}: {price_stock}. Which stock you would like to choose?  ")
    # print("Here is the detail information for this stock")
    return stock_choice


def get_company(stock_choice):
    '''
    Will provide the detailed information about the company
    '''
    get_company_url= "https://api.polygon.io/v3/reference/tickers/"
    ans = input("Do you want to know more about this company? (Yes/No) ")
    if ans.strip().lower() == "yes":
        try:
            r = requests.get(f"{get_company_url}{stock_choice}?apiKey={Polygon_key}")
            data = r.json()     
            key_list = [data["results"].keys()]
            key = input(f"What kind of information you want to know? Please choose from {key_list}")
            print(data["results"][key])
        except: 
            print("Not available information")
    



def SMA(stock_choice):
    '''
    Return SMA to provide some trading recommendation.
    '''
    ans = input("Do you want to have some technicial choice? (Yes/No) ")
    if ans.strip().lower() == "yes":
        print("The following plot is Simple Moving Average (SMA)-5 and SMA-10 days for that stock")
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days = 100)
        price = data.DataReader(stock_choice,'yahoo',
                        start_date,
                        end_date)
        price.head()
        price['ma5'] = price['Adj Close'].rolling(5).mean()
        price['ma20'] = price['Adj Close'].rolling(20).mean()
        price.tail()
        fig = plt.figure(figsize=(16,9))
        ax1 = fig.add_subplot(111, ylabel='Price')
        price['Adj Close'].plot(ax=ax1, color='g', lw=2., legend=True)
        price.ma5.plot(ax=ax1, color='r', lw=2., legend=True)
        price.ma20.plot(ax=ax1, color='b', lw=2., legend=True)
        plt.grid()
        plt.show()
        print("When the short term moving average crosses above the long term moving average, this indicates a buy signal. Contrary, when the short term moving average crosses below the long term moving average, it may be a good moment to sell.")
        print("Hope it helps you! See you. ")
    else:
        print("Good Bye!")


if __name__=='__main__':
    #Convert CSV into dictionary
    nasdaq_dict=read_csv_to_dicts('./nasdaq_list.csv', encoding='utf-8', newline='', delimiter=',')
    utl.write_json('nasdaq_dict.json', nasdaq_dict)
    nasdaq_dict_byindustry=classify_by_industry(nasdaq_dict)
    utl.write_json('nasdaq_byindustry.json', nasdaq_dict_byindustry)
    print(len(nasdaq_dict))
    
    print("Q1-1 Get to know with the Forbes 2000========================================================================")
    answer1 = input("We have scrapped the data from <Forbes Global 2000>, which ranks the largest companies in the world using four metrics: sales, profits, assets, and market value. Among all of these compnaies, which company you want to know? please give a number between 1-2000! ")
    print(utl.scrapping[int(answer1)-1])
    time.sleep(3)

    print("Q1-2 Get to know with Forbes by country======================================================================")
    print("In order to better analyze the data, we have sort these companies by their country")
    print("The country lists are: ")
    print(list(utl.country_list.keys()))
    answer2 = input("Which country you want to know more? ")
    print(f"These are the companies in {answer2} in Forbes Top 2000: ")
    print(utl.country_list[answer2])
    time.sleep(3)
        
    print("Q2 Choose interested company========================================================================")
    sector, symbol = choose_sector(nasdaq_dict)
    time.sleep(3)

    print("Q3 Choose other stock in the same sector========================================================================")
    print("Inorder to form a better trading decision, you can also choose other stockS in the same industry to make a reference!")
    print(f"Here is the stock symbol in the {sector}")
    time.sleep(5)
    print(nasdaq_dict_byindustry[sector])

    print("Q4 Choose benchmarking company========================================================================")
    symbol_string= input("Please input in stock symbol in the above list to make further analysis. Please input at most 10 stocks! (Format: ADT, ADTH, .... )   ")
    symbol_list=symbol_string.split(",")
    #data cleaning
    for i in range(len(symbol_list)):
        symbol_list[i]=symbol_list[i].strip(" ")
    symbol_list.append(symbol)
    print(symbol_list)
    #append the original interested company
    
    print(" Q5 Detail of chosen stock in the input date. ==========================================================================")
    stock_detail = stocks_detail(symbol_list)
    tree_of_price,detail_price_tree = price_tree(stock_detail)
    utl.write_json('detail_price_tree.json', detail_price_tree)
    print(tree_of_price)
    time.sleep(3)

    print("Q6 Choose the stock based on the price tree============================================================================")
    stock_choice = choose_stock(tree_of_price)
    get_company(stock_choice)
    time.sleep(3)

    print("Q7 Moving average plot for trading advice==========================================================================")
    SMA(stock_choice)

