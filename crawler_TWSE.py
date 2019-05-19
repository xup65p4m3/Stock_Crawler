from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import time

target_Stock = "1773" #股票代碼
target_Stock_Listing_Date = "201801" #起始日期

def Generate_Date(start_date):
    consider_date = []
    current_date = datetime.datetime.now()
    current_date_str = "".join(str(current_date).split("-")[:2])
    consider_date.append(current_date_str)
    while start_date != consider_date[-1]:
        current_month_first_day = datetime.date(current_date.year, current_date.month, 1)
        pre_month = current_month_first_day - datetime.timedelta(days = 1)
        first_day_of_pre_month = datetime.date(pre_month.year, pre_month.month, 1)
        consider_date.append("".join(str(first_day_of_pre_month).split("-")[:2]))
        current_date = first_day_of_pre_month
    return consider_date[::-1]

def Get_Data(Year_Month, Stock_ID):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"}
    url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date="+ Year_Month +"01&stockNo="+ Stock_ID +"&_=1532940199447"
    session = requests.Session()
    resp = session.get(url, headers=headers)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    a = soup.text.split("\"data\":[")[1]
    a = a.split("],\"notes\"")[0]
    a = a.split("\"")
    a = [a[i] for i in range(len(a)) if i % 2 != 0]
    result = pd.DataFrame(index=range(int(len(a)/9)), columns=["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"])
    for i in range(len(a)):
        if i % 9 == 0:
            result.iloc[int(i/9),:] = a[i:i+9]
    return result

consider_Date_list = Generate_Date(target_Stock_Listing_Date)
all_date = pd.DataFrame(columns=["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"])

for i in consider_Date_list:
    time.sleep(3)
    all_date =  pd.concat([all_date, Get_Data(i, target_Stock)], axis=0, ignore_index=True)
all_date = all_date.drop(columns=["漲跌價差","成交筆數"])
all_date = all_date[["日期","開盤價","最高價","最低價","收盤價","成交股數","成交金額"]]

for i in range(len(all_date)):
    temp = str(int("".join(all_date.iloc[i,0].split("/")))+19110000)
    all_date.iloc[i,0] = temp[:4]+"/"+temp[4:6]+"/"+temp[6:]
    all_date.iloc[i,5] = round(float("".join(all_date.iloc[i,5].split(",")))/1000)
    all_date.iloc[i,6] = round(float("".join(all_date.iloc[i,6].split(",")))/1000)
