
''' In Python, multi-line commenting is initiated with three '
Homework 1.

Inputs to the function include:
Start date
End date
Symbols for for equities (e.g., GOOG, AAPL, GLD, XOM)
Allocations to the equities at the beginning of the simulation (e.g., 0.2, 0.3, 0.4, 0.1)
The function should return:
Standard deviation of daily returns of the total portfolio
Average daily return of the total portfolio
Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
Cumulative return of the total portfolio
An example of how you might call the function in your program:
vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, ['GOOG','AAPL','GLD','XOM'], [0.2,0.3,0.4,0.1])

test
'''

#single line comments are initiated with #
#most of the computational investing code relies on the QSToolKit software framework
#http://wiki.quantsoftware.org/index.php?title=QuantSoftware_ToolKit
#we are going to import it here
#importing modules in Python is easily done with the import command
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da #pull historical data from Yahoo!


import datetime as dt
import matplotlib.pyplot as plt #matlab like commands! :)
import pandas as pd #data analysis toolkit
import sys #interact with the system

def NumUsrSpEquities(): #User Specified
    MaxNumEquities = 20 #how many equities can we handle? arbitrarily chose 20?
    #Ask the command line which equities we want to get, returns a list of strings
    print "How Many Equities should we get?\n"
    #make sure we got the right data type!
    while 1: #1 is faster then true
        print "Please Enter an integer between 1 and "
        print MaxNumEquities
        NumUsrSpEquities = input(": ") 
        if isinstance(NumUsrSpEquities, int) and 1 <= NumUsrSpEquities <= MaxNumEquities: #quit the while loop only if it is an integer
            break
    return NumUsrSpEquities

def UsrSpEquities(NumUsrSpEquities):
    ls_symbols = [] #create an empty list to hold stock symbols
    for symbol_counter in range(0, NumUsrSpEquities):
        print "Enter Equity symbol number",symbol_counter+1
        equity_symbol = raw_input(": ") #use raw input for strings
        ls_symbols.append(equity_symbol) #append is pythons built in function to add to lists
    return ls_symbols

def UsrSpTimeFrame():
    print "Please enter the start date"
    while 1:
        year_start = input("YYYY:")
        if  1950 < year_start < dt.date.today().year: #make sure we are grabbing reasonable stock dates
            break
    while 1:
        month_start = input("MM:")
        if 1 <= month_start <= 12: #There are only 12 months!
            break
    while 1:
        day_start = input("DD:")
        if 1 <= day_start <= 31: #hopefully this month has 31 days...
            break
    start_date = dt.datetime(year_start,month_start,day_start)

    print "Please enter the End date"
    while 1:
        year_end = input("YYYY:")
        if  year_start <= year_end < dt.date.today().year: #make sure we are grabbing reasonable stock dates
            break
    while 1:
        month_end = input("MM:")
        if  1 <= month_end <= 12: #There are only 12 months!
            break
    while 1:
        day_end = input("DD:")
        if 1 <= day_end <= 31: #hopefully this month has 31 days...
            break
    end_date = dt.datetime(year_end, month_end, day_end)
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date,end_date, dt_timeofday)
    return ldt_timestamps
def GenEquityDataDict(provider, ls_symbols, ldt_timestamps, ls_keys): #how can we make this more absract?
    c_dataobj = da.DataAccess(provider)
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    return d_data
def tutorial_1_main():
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    TimeFrame = UsrSpTimeFrame()
    ls_symbols = UsrSpEquities(NumUsrSpEquities())
    d_data = GenEquityDataDict('Yahoo', ls_symbols, TimeFrame, ls_keys)
    na_price = d_data['close'].values
    plt.clf()
    plt.plot(TimeFrame, na_price)
    plt.legend(ls_symbols)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')
    na_normalized_price = na_price / na_price[0, :]
    na_rets = na_normalized_price.copy()
    plt.clf()
    plt.plot(TimeFrame,tsu.returnize0(na_rets))
    plt.legend(ls_symbols)
    plt.ylabel('Daily_Return')
    plt.xlabel('Date')
    plt.savefig('Daily_Return.pdf',format='pdf')
tutorial_1_main()
