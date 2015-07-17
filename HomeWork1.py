
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
import time
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

'''
Generates closing timestamps for each date in the timeframe
@param start_date: a datetime object (YYYY,MM,DD)
@param end_date:   a datetime object (YYYY,MM,DD) 
@return: a tuple with the timestamps and the closing time used
'''
def ClosingTimeStamps(start_date, end_date):
    dt_timeofday = dt.timedelta(hours=16)   # initialize daily timestamp: closing prices,
                                            # exchange closes at 4, so 16 hundred hours
    ldt_timestamps = du.getNYSEdays(start_date,end_date, dt_timeofday)
    return (ldt_timestamps,dt_timeofday)
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
def GenEquityDataDict(provider, ls_symbols, ldt_timestamps, ls_keys): #how can we make this more absract?
    c_dataobj = da.DataAccess(provider) #Create an object of the QSTK-dataaccess class with provider as the source (QSTK)
    #Read the data and map it to ls_keys via dict() (i.e. Hash Table structure)
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    return d_data

'''
 Assess historical performance of multi-stock portfolio
 @param d_data:         hash table linking symbol keys and stock prices
 @param dt_start:   start date in list structure: [year,month,day] e.g. [2012,1,28]
 @param dt_end:     end date in list structure: [year,month,day] e.g. [2012,12,31]
 @param ls_symbols:     list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
 @param lf_allocations: list of allocations: e.g. [0.2,0.3,0.4,0.1]
 @param b_print:        print results (True/False)
 @return: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
'''
def PastPortfolioPerformance(d_data, dt_start, dt_end, ls_symbols, lf_allocations, b_print): 
    start = time.time()
    
    #Check if equities.symbols and lf_allocations have same length
    if len(ls_symbols) != len(lf_allocations):
        print "ERROR: Make sure symbol and allocation lists have same number of elements."
        return;
    #make sure lf_allocations allocate exactly 100%
    sumAllocations = 0
    for x in lf_allocations:
        sumAllocations += x
    if sumAllocations != 1:
        print "ERROR: Make sure allocations add up to 1."
        return
 
    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values
 
    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:]
 
    lf_Stats = calcStats.CalcStats(na_normalized_price, lf_allocations)
 
    #Print results
    if b_print:
        print "Start Date: ", dt_start
        print "End Date: ", dt_end
        print "Symbols: ", ls_symbols
        print "Volatility (stdev daily returns): " , lf_Stats[0]
        print "Average daily returns: " , lf_Stats[1]
        print "Sharpe ratio: " , lf_Stats[2]
        print "Cumulative daily return: " , lf_Stats[3]
 
        print "Run in: " , (time.time() - start) , " seconds."
 
    #Return list: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
    return lf_Stats[0:3]


def HomeWork1Main():
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    DateThreshold = PromptUsrTimeFrame()
    ls_ClosingTimeStamps = ClosingTimeStamps(DateThreshold[0], DateThreshold[1])
    TimeFrame = ls_ClosingTimeStamps[0]
    #equities.PromptUsr()
    #d_data = GenEquityDataDict('Yahoo', equities.symbols, TimeFrame, ls_keys)
    d_data = GenEquityDataDict('Yahoo', ['GOOG', 'AAPL'], TimeFrame, ls_keys)
    print d_data['close']
    print d_data['close']['GOOG']
    dataFile = open('dataFile.txt', 'r+')
    pickle.dump(d_data,dataFile) #serialized, but not human readable!
    na_price = d_data['close'].values
    lf_Stats = PastPortfolioPerformance(d_data, DateThreshold[0], DateThreshold[1], equities.symbols, equities.allocations, True)
    OptimizePortfolioAllocations.optimizePortfolioAllocations(d_data, DateThreshold[0], DateThreshold[1], equities.symbols)
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

