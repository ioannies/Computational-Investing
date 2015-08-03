







import time
import matplotlib.pyplot as plt
import calcStats
import calcPerms
from scipy.optimize import minimize

def optimizePortfolioAllocations(d_data, dt_start, dt_end, ldt_timestamps, ls_symbols, lf_allocations, precision=False):
    '''
@summary Optimize portfolio allocations  to maximise Sharpe ratio
@param d_data:        hash table linking symbol keys and stock prices
@param dt_start:      start date in list structure: [year,month,day] e.g. [2012,1,28]
@param dt_end:        end date in list structure: [year,month,day] e.g. [2012,12,31]
@param ldt_timestamps: list of timestamps corresponding to value
@param ls_symbols:    list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
@param lf_allocations: list of allocations of assets
@param precision:   true - optimization using scipy.optimize; false - 10% increments & positive weights
@return: optimized list of allocations by percentage
'''
    ld_alldata = [d_data, dt_start, dt_end]
    start = time.time();
    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;
 
    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];
    
    
    if precision:
        #Precise optimization:
        # by calling scipy's optimize? 
        
        #Define objective function (sharpe ratio)
        def sharpe(lf_allocations, d_data, dt_start, dt_end, ls_symbols):
            stats = calcStats.PastPortfolioPerformance(d_data, dt_start, dt_end, ls_symbols, lf_allocations)
            return stats[2];
        initialGuess = lf_allocations
        optimal = -minimize(sharpe, initialGuess, (d_data, dt_start, dt_end, ls_symbols), method = 'Nelder-Mead')
        return optimal
        
    else:
        
        #Imprecise optimization (required in Homework 1)
 
        #Using backtracking and permutation
        #Permutation function
        global li_sol, li_valid, i_sum, i_numEls;
        TARGET = 10;
        li_sol = [0] * len(ls_symbols);
        #li_sol = [0] * TARGET;
        li_valid = [];
        i_sum = 0;
        i_numEls = 0;
        def back(lastEl):        #Backtracking function results in list of integers that sum to 10
            global li_sol, li_valid, i_sum, i_numEls;
            #base-case
            if i_numEls >= len(ls_symbols):
                if i_sum == TARGET:
                    li_valid.extend(list(calcPerms.allPerms(li_sol)));
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
        #Convert to float array then sum to 1
        global lf_valid;
        lf_valid = [];
        for i in li_valid:
            lf_valid.append([j/10.0 for j in i]);
 
        #Calculate Sharpe ratio for each valid allocation
        f_CurrMaxSharpe = 0.0;
        for allocation in lf_valid:
            t_Stats = calcStats.CalcStats(na_normalized_price, allocation);
            if t_Stats[2] > f_CurrMaxSharpe:
                lf_CurrStats = t_Stats
                f_CurrMaxSharpe = t_Stats[2];
                lf_CurrEffAllocation = allocation;
                optimalAllocations = lf_CurrEffAllocation
 
        #Plot portfolio daily values over time period
        #Obtain benchmark $SPX data
        #na_spxprice = d_data['close']['$SPX'].values
        #na_spxnormalized_price = na_spxprice / na_spxprice[0]
        #lf_spxStats = calcStats.CalcStats(na_spxnormalized_price, [1])
        #Plot
        plt.clf()
        #plt.plot(ld_alldata[4], lf_spxStats[4])    #SPX
        plt.plot(ldt_timestamps, lf_CurrStats[4])  #Portfolio
        plt.axhline(y=0, color='r')
        plt.legend(['$SPX', 'Portfolio'])
        plt.ylabel('Daily Value')
        plt.xlabel('Date')
        plt.savefig('chart.pdf', format='pdf')
 
        #Print results:
        print "Start Date: ", dt_start
        print "End Date: ", dt_end
        print "Symbols: ", ls_symbols
        print "Optimal Allocations: ", optimalAllocations
        print "Volatility (stdev daily returns): " , lf_CurrStats[0]
        print "Average daily returns: " , lf_CurrStats[1]
        print "Sharpe ratio: " , lf_CurrStats[2]
        print "Cumulative daily return: " , lf_CurrStats[3] 
        print "Run in: " , (time.time() - start) , " seconds."
    return optimalAllocations