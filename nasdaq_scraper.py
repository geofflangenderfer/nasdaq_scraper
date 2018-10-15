#!/usr/bin/env python3
from datetime import datetime
from lxml import html
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np
import os
import pandas as pd
import random
import re
import requests
import sys
import time
import xlsxwriter

def removeDups(wl):
    "Remove duplicates and return a Series of tickers"
    # only unique values in watchlist
    symbols = wl.unique()

    return symbols

def getData(u, t):
    """
    return a df row for a stock with all relevant info.
    """


    headers = {
				"Accept":"p_with_data/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				"Accept-Encoding":"gzip, deflate",
				"Accept-Language":"en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
				"Connection":"keep-alive",
				"Host":"www.nasdaq.com",
				"Referer":"http://www.nasdaq.com",
				"Upgrade-Insecure-Requests":"1",
				"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
	}

    for retries in range(5):
        response = requests.get(u, headers = headers, verify = False)

        status_code = response.status_code
        if status_code != 200:
            print("Bad response from webserver, HTTP status code: %s"%status_code)
            print('url:', u)
            sys.exit(0)

        print("Parsing %s" %(u))
        # Add random delay
        time.sleep(random.randint(1,3))

        parser = html.fromstring(response.text)
        xpath1 = '//div[@id="left-column-div"]/h2/text()'
        xpath2 = '//span[@id="two_column_main_content_reportdata"]/text()'
        text1 = parser.xpath(xpath1)[0]
        text2 = parser.xpath(xpath2)[0]

        try:
            date = re.search(r'[A-Z][a-z][a-z] [0-9]?[0-9], [0-9][0-9][0-9][0-9]',
                    text1).group(0)
            date = datetime.strptime(date, '%b %d, %Y').strftime('%m-%d-%Y')
        except:
            date='NA'


        estimate = re.search(r'\*', text1)

        end = text2.find(' is ')
        company_name = text2[:end].strip()

        bmo = re.search('before market open', text2)
        amc = re.search('after market close', text2)

        # estimate or confirmed?
#        if estimate:
#            date += '*'
        # before market open or after market close
        if bmo:
            timing = 'bmo'
        elif amc:
            timing = 'amc'
        else:
            timing = 'NA'

        # zacks doesn't have info on this ticker
        if company_name[:3] =='Our':
            company_name = t.strip()
            date = 'NA'


        entry = [company_name, t.strip(), date, timing,
                 datetime.today().strftime("%m-%d-%Y"), u, '--']

        return entry

def toExcel(df):

    # sort by earliest earnings date
    df = df.sort_values( by= 'Earnings Date (estimate)' )
    df.reset_index(drop = True)

    # change date format
    df.iloc[:,2] = pd.to_datetime(df.iloc[:,2], format='%m-%d-%Y', errors = 'coerce')
    df.iloc[:,2] = df.iloc[:,2].dt.strftime(date_format='%b %d, %Y')

    # add data
    writer = pd.ExcelWriter('EarningsWatchList.xlsx', engine='xlsxwriter')

    df.iloc[:,:4].to_excel(writer, sheet_name='Sheet1', index=False, startrow=17)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # format columns
    worksheet.set_column('A:A', 42)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 42)

    # nav trading image
    try:
        worksheet.insert_image('A1', 'nav_trad.png', {'x_scale': 0.3, 'y_scale': 0.3})
    except:
        print("Couldn't find nav_trad.png. Show me where it is")
        Tk.withdraw()
        nav_trad = askopenfilename()

    # instructions 
    worksheet.write('A9', "Below are the estimated earnings announcements. Dates and times are subject to change. Please check the company's website for confirmation.")
    worksheet.write('A10', "This sheet will be updated weekly.")

    worksheet.write('A12', 'Please complete our course "How To Trade Options on Earnings for Quick Profits" for earnings announcement strategies.')
    worksheet.write('A13', 'We have added a video module to the course to explain how to use this sheet.')


    workbook.close()
    writer.save()

def startIndex(df):
    for x in df.index:
        if df[x] == 'Symbol':
            index = x
            break
    return x

def findSymbols():

    excelFile = "Desktop/nasdaq_scraper/EarningsWatchList.xlsx"

    try:
        # symbols in middle of file
        symbols = pd.read_excel(excelFile, header = None)
        symbols = symbols.iloc[:,1]
        index = startIndex(symbols)
        symbols = symbols.loc[index+1:]
    except:
        try:
            # prompt for files; symbols in middle 
            print("Couldn't find symbols in %s " %excelFile)
            Tk().withdraw()
            print("Open the file that  has the list of symbols needed")
            symbolsFile= askopenfilename()
            print('-'*30)
            print(symbolsFile)
            print('-'*30)
            symbols = pd.read_excel(symbolsFile, header = None)
            symbols = symbols.iloc[:,1]
            index = startIndex(symbols)
            symbols = symbols.loc[index+1:]
        except:
            print("Couldn't extract the symbols needed from the Excel File. Try modifying the file so the 2nd column has a heading 'Symbol' and all the symbols required and retry.")
            sys.exit(0)
    return symbols

if __name__  == '__main__':

    symbols = findSymbols()
    tickers = removeDups(symbols)
    data = pd.DataFrame(columns = ['Company Name', 'Symbol',
                                   'Earnings Date (estimate)',
                                   'Before Market Open/After Market Close', 'Updated',
                                   'URL', "Errors"])

    base = "https://www.nasdaq.com/earnings/report/"

    for i, ticker in enumerate(tickers):
        url = base + ticker.lower().strip()
        try:
            raw_data = getData(url, ticker)
        except Exception as e:
            raw_data = [ticker.strip(),ticker.strip(),'Failed',ticker.strip(),
                        datetime.today().strftime("%m-%d-%Y"),
                        ticker.strip(), url, e]
        data.loc[i] = raw_data

        print(data.iloc[:,:4])
        time.sleep(random.randint(1,3))

    toExcel(data)
