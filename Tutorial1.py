
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
import numpy as np
import pandas as pd #data analysis toolkit
import datetime as dt
import matplotlib.pyplot as plt #matlab like plotting commands! :)
import sys #interact with the system
import time
from scipy.optimize import minimize

def PromptUsrNumEquities(): #ask the user how many equities we should be comparing
    print "How Many Equities should we get?\n"
    #make sure we got the right data type!
    while 1: #1 is faster then true
        NumUsrSpEquities = input("Please Enter an integer: ") #can't handle strings?
        if isinstance(NumUsrSpEquities, int): #quit the while loop only if it is an integer
            break
    return NumUsrSpEquities

def PromptUsrEquities(NumUsrSpEquities): #Ask the command line which equities we want to get, returns a list of strings
    ls_symbols = [] #create an empty list to hold stock symbols
    for symbol_counter in range(0, NumUsrSpEquities):
        print "Enter Equity symbol number",symbol_counter+1
        equity_symbol = raw_input(": ") #use raw input for strings
        ls_symbols.append(equity_symbol) #append is pythons built in function to add to lists
    return ls_symbols

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

def GenClosingTimeStamps(start_date, end_date): #creates a list of timestamps 1 a day at close for every day in the timeframe
    dt_timeofday = dt.timedelta(hours=16) #initialize daily timestamp: closing prices, exchange closes at 4, so 16 hundred hours
    ldt_timestamps = du.getNYSEdays(start_date,end_date, dt_timeofday)
    return ldt_timestamps

def GenEquityDataDict(provider, ls_symbols, ldt_timestamps, ls_keys): #how can we make this more absract?
    c_dataobj = da.DataAccess(provider) #Create an object of the QSTK-dataaccess class with provider as the source (QSTK)
    #Read the data and map it to ls_keys via dict() (i.e. Hash Table structure)
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    return d_data

'''
' Calculate Portfolio Statistics 
' @param na_normalized_price: NumPy Array for normalized prices (starts at 1)
' @param lf_allocations: allocation list
' @return list of statistics:
' (Volatility, Average Return, Sharpe, Cumulative Return)
'''
def calcStats(na_normalized_price, lf_allocations):
    #Calculate cumulative daily portfolio value
    #row-wise multiplication by weights
    na_weighted_price = na_normalized_price * lf_allocations;
    #row-wise sum
    na_portf_value = na_weighted_price.copy().sum(axis=1);
 
    #Calculate daily returns on portfolio
    na_portf_rets = na_portf_value.copy()
    tsu.returnize0(na_portf_rets);
 
    #Calculate volatility (stdev) of daily returns of portfolio
    f_portf_volatility = np.std(na_portf_rets); 
 
    #Calculate average daily returns of portfolio
    f_portf_avgret = np.mean(na_portf_rets);
 
    #Calculate portfolio sharpe ratio (avg portfolio return / portfolio stdev) * sqrt(252)
    f_portf_sharpe = (f_portf_avgret / f_portf_volatility) * np.sqrt(250);
 
    #Calculate cumulative daily return
    #...using recursive function
    def cumret(t, lf_returns):
        #base-case
        if t==0:
            return (1 + lf_returns[0]);
        #continuation
        return (cumret(t-1, lf_returns) * (1 + lf_returns[t]));
    f_portf_cumrets = cumret(na_portf_rets.size - 1, na_portf_rets);
 
    return [f_portf_volatility, f_portf_avgret, f_portf_sharpe, f_portf_cumrets, na_portf_value];

'''
' Simulate and assess performance of multi-stock portfolio
' @param li_startDate:    start date in list structure: [year,month,day] e.g. [2012,1,28]
' @param li_endDate:    end date in list structure: [year,month,day] e.g. [2012,12,31]
' @param ls_symbols:    list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @param lf_allocations:    list of allocations: e.g. [0.2,0.3,0.4,0.1]
' @param b_print:       print results (True/False)
'''
def simulate(li_startDate, li_endDate, ls_symbols, lf_allocations, b_print):
 
    start = time.time();
    
    #Check if ls_symbols and lf_allocations have same length
    if len(ls_symbols) != len(lf_allocations):
        print "ERROR: Make sure symbol and allocation lists have same number of elements.";
        return;
    #Check if lf_allocations adds up to 1
    sumAllocations = 0;
    for x in lf_allocations:
        sumAllocations += x;
    if sumAllocations != 1:
        print "ERROR: Make sure allocations add up to 1.";
        return;
 
    #Prepare data for statistics
    d_data = readData(li_startDate, li_endDate, ls_symbols)[0];
 
    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;
 
    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];
 
    lf_Stats = calcStats(na_normalized_price, lf_allocations);
 
    #Print results
    if b_print:
        print "Start Date: ", li_startDate;
        print "End Date: ", li_endDate;
        print "Symbols: ", ls_symbols;
        print "Volatility (stdev daily returns): " , lf_Stats[0];
        print "Average daily returns: " , lf_Stats[1];
        print "Sharpe ratio: " , lf_Stats[2];
        print "Cumulative daily return: " , lf_Stats[3];
 
        print "Run in: " , (time.time() - start) , " seconds.";
 
    #Return list: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
    return lf_Stats[0:3]; 

def optimize(li_startDate, li_endDate, ls_symbols, b_precision):
 
    start = time.time();
 
    #Prepare data for statistics
    ld_alldata = readData(li_startDate, li_endDate, ls_symbols);
    d_data = ld_alldata[0];
 
    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;
 
    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];
    
    
    if b_precision:
        #Precise optimization:
        
        #Define objective function (sharpe ratio)
        def objective_sharpe(x):
            return simulate(li_startDate, li_endDate, ls_symbols, x)[2];
 
        #Work on this later...
        
    else:
        
        #Imprecise optimization (required in Homework 1)
 
        #Using backtracking and permutation
        #Permutation function
        def all_perms(elements):
            if len(elements) <=1:
                yield elements;
            else:
                for perm in all_perms(elements[1:]):
                    for i in range(len(elements)):
                        #nb elements[0:1] works in both string and list contexts
                        yield perm[:i] + elements[0:1] + perm[i:];
 
        #Backtracking function results in list of integers that sum to 10
        global li_sol, li_valid, i_sum, i_numEls;
        TARGET = 10;
        li_sol = [0] * len(ls_symbols);
        #li_sol = [0] * TARGET;
        li_valid = [];
        i_sum = 0;
        i_numEls = 0;
        def back(lastEl):
            global li_sol, li_valid, i_sum, i_numEls;
            #base-case
            if i_numEls >= len(ls_symbols):
                if i_sum == TARGET:
                    li_valid.extend(list(all_perms(li_sol)));
                return;
            #continuation
            for i in range(lastEl, TARGET + 1 - i_sum):
                i_sum += i;
                li_sol[i_numEls] = i;
                i_numEls += 1;
                back(i);
                #undo
                i_sum -= i;
                i_numEls -= 1;
            return;
                
        back(0);
        #Convert to float array that sum to 1
        global lf_valid;
        lf_valid = [];
        for i in li_valid:
            lf_valid.append([j/10.0 for j in i]);
 
        #Calculate Sharpe ratio for each valid allocation
        f_CurrMaxSharpe = 0.0;
        for allocation in lf_valid:
            t_Stats = calcStats(na_normalized_price, allocation);
            if t_Stats[2] > f_CurrMaxSharpe:
                lf_CurrStats = t_Stats
                f_CurrMaxSharpe = t_Stats[2];
                lf_CurrEffAllocation = allocation;
 
        #Plot portfolio daily values over time period
        #Obtain benchmark $SPX data
        d_spx = readData(li_startDate, li_endDate, ["$SPX"])[0];
        na_spxprice = d_spx['close'].values;
        na_spxnormalized_price = na_spxprice / na_spxprice[0,:];
        lf_spxStats = calcStats(na_spxnormalized_price, [1]);
        #Plot
        plt.clf();
        plt.plot(ld_alldata[4], lf_spxStats[4]);    #SPX
        plt.plot(ld_alldata[4], lf_CurrStats[4]);  #Portfolio
        plt.axhline(y=0, color='r');
        plt.legend(['$SPX', 'Portfolio']);
        plt.ylabel('Daily Value');
        plt.xlabel('Date');
        plt.savefig('chart.pdf', format='pdf');
 
        #Print results:
        print "Start Date: ", li_startDate;
        print "End Date: ", li_endDate;
        print "Symbols: ", ls_symbols;
        print "Optimal Allocations: ", lf_CurrEffAllocation;
        print "Volatility (stdev daily returns): " , lf_CurrStats[0];
        print "Average daily returns: " , lf_CurrStats[1];
        print "Sharpe ratio: " , lf_CurrStats[2];
        print "Cumulative daily return: " , lf_CurrStats[3];
 
        print "Run in: " , (time.time() - start) , " seconds.";

def tutorial_1_main():
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    DateThreshold = PromptUsrTimeFrame()
    TimeFrame = GenClosingTimeStamps(DateThreshold[0], DateThreshold[1])
    ls_symbols = PromptUsrEquities(PromptUsrNumEquities())
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
    plt.clf()
    plt.plot(TimeFrame,CalcDailyCumRet(tsu.returnize0(na_rets)))
    plt.legend(ls_symbols)
    plt.ylabel('DailyCumReturn')
    plt.xlabel('Date')
    plt.savefig('DailyCumReturn.pdf',format='pdf')
tutorial_1_main()
