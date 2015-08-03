
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


'''

#single line comments are initiated with #
#most of the computational investing code relies on the QSToolKit software framework
#http://wiki.quantsoftware.org/index.php?title=QuantSoftware_ToolKit
#we are going to import it here
#importing modules in Python is easily done with the import command
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da #pull historical data from Yahoo!
import pandas as pd #data analysis toolkit
import datetime as dt
import matplotlib.pyplot as plt #matlab like plotting commands! :)
import sys #interact with the system
import OptimizePortfolioAllocations
import calcStats
import pickle #serialization module

class Equities(object):
    def __init__(self):
        self.symbols = []
        self.allocations = []
        
    def __len__(self): #allows len(Equities) to be called, returns the number of symbols
        return len(list(self.symbols))
        
    def PromptUsr(self): #ask the user to fill the equities object
        def PromptNum(): #ask the user how many equities we should be comparing
            print "How Many Equities should we get?\n"
            #make sure we got the right data type!
            while 1: #1 is faster then true
                numTotal = input("Please Enter an integer: ") #can't handle strings?
                if isinstance(numTotal, int): #quit the while loop only if it is an integer
                    break
            return numTotal
              
        def PromptSymbols(numTotal): #Ask the command line which equities we want to get, returns a list of strings
            symbols = []
            for symbol_counter in range(0, numTotal):
                print "Enter Equity symbol number",symbol_counter+1
                equity_symbol = raw_input(": ") #use raw input for strings
                symbols.append(equity_symbol) #append is pythons built in function to add to lists
            return symbols
            
        def PromptAllocations(numTotal):
            allocations = []
            for equity_counter in range(0, numTotal):
                print "Enter allocation percentage for equity symbol ",self.symbols[equity_counter]
                equity_percent = eval(raw_input(": "))
                allocations.append(equity_percent)
            return allocations
        numTotal = PromptNum()
        self.symbols = PromptSymbols(numTotal)
        self.allocations = PromptAllocations(numTotal) 
        
equities = Equities()

def PromptUsrTimeFrame():
    print "Please enter the start date"
    while 1:
        year_start = input("YYYY:")
        if  1950 < year_start < dt.date.today().year: #make sure we are grabbing reasonable stock dates
            break
    while 1:
        month_start = int(raw_input("MM:"))
        if 1 <= month_start <= 12: #There are only 12 months!
            break
    while 1:
        day_start = int(raw_input("DD:"))
        if 1 <= day_start <= 31: #hopefully this is a 31 day month...
            break
    start_date = dt.datetime(year_start,month_start,day_start)

    print "Please enter the End date"
    while 1:
        year_end = int(raw_input("YYYY:"))
        if  year_start <= year_end < dt.date.today().year: #make sure we are grabbing reasonable stock dates
            break
    while 1:
        month_end = int(raw_input("MM:"))
        if 1 <= month_end <= 12: #There are only 12 months!
            break
    while 1:
        day_end = int(raw_input("DD:"))
        if 1 <= day_end <= 31: #hopefully this month has 31 days...
            break
    end_date = dt.datetime(year_end, month_end, day_end)
    return (start_date, end_date)


def TimeStamps(start_date, end_date, time):
    '''
Generates closing timestamps for each date in the timeframe
@param start_date: a datetime object (YYYY,MM,DD)
@param end_date:   a datetime object (YYYY,MM,DD)
@param time: What hour of day in 24 hour format? e.g. closing time (16)
@return: a tuple with the timestamps and the closing time used
'''
    dt_timeofday = dt.timedelta(hours=time)   # initialize daily timestamp: closing prices,
                                            # exchange closes at 4, so 16 hundred hours
    ldt_timestamps = du.getNYSEdays(start_date,end_date, dt_timeofday)
    return (ldt_timestamps,dt_timeofday)

def GenEquityDataDict(provider, ls_symbols, ldt_timestamps, ls_keys): #how can we make this more absract?
    '''
@summary: pull stock performance data from the web
@param provider: Website name to obtain data. Yahoo has been tested so far
@param ls_symbols: The list of NYSE symbols for the companies we are pulling data. e.g. ['GOOG', 'AAPL', 'GLD', $SPX]
@param ldt_timestamps: The time of day at which the price will be read.
@param ls_keys: The type of data we are pulling. e.g. ['open', 'high', 'low', 'close', 'volume', 'actual_close']
@return: dictionary linking symbols to their respective data dictionaries. 
                        e.g. {'open' : {'GOOG' : {'2010-01-01 16:00' : (open_price),
                                                  '2010-01-02 16:00' : (open_price)},
                                        'AAPL' : {'2010-01-01 16:00' : (open_price),
                                                  '2010-01-02 16:00' : (open_price)}}}
'''
    c_dataobj = da.DataAccess(provider) #Create an object of the QSTK-dataaccess class with provider as the source (QSTK)
    #Read the data and map it to ls_keys via dict() (i.e. Hash Table structure)
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    return d_data



def HomeWork1Main():
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    DateThreshold = PromptUsrTimeFrame()
    ls_ClosingTimeStamps = TimeStamps(DateThreshold[0], DateThreshold[1], 16)
    TimeFrame = ls_ClosingTimeStamps[0]
    equities.PromptUsr()
    d_data = GenEquityDataDict('Yahoo', equities.symbols, TimeFrame, ls_keys)
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    lf_Stats = calcStats.PastPortfolioPerformance(d_data, DateThreshold[0], DateThreshold[1], equities.symbols, equities.allocations)
    OptimizePortfolioAllocations.optimizePortfolioAllocations(d_data, DateThreshold[0], DateThreshold[1], TimeFrame, equities.symbols, equities.allocations, True)
    plt.clf()
    plt.plot(TimeFrame, na_price)
    plt.legend(equities.symbols)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')
    na_normalized_price = na_price / na_price[0, :]
    na_rets = na_normalized_price.copy()
    plt.clf()
    plt.plot(TimeFrame,tsu.returnize0(na_rets))
    plt.legend(equities.symbols)
    plt.ylabel('Daily_Return')
    plt.xlabel('Date')
    plt.savefig('Daily_Return.pdf',format='pdf')
    plt.clf()
    plt.plot(TimeFrame,lf_Stats[3])
    plt.legend(equities.symbols)
    plt.ylabel('DailyCumReturn')
    plt.xlabel('Date')
    plt.savefig('DailyCumReturn.pdf',format='pdf')
HomeWork1Main()

