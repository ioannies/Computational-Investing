





'''
 @summary Optimize portfolio allocations  to maximise Sharpe ratio
 @param d_data:        hash table linking symbol keys and stock prices
 @param dt_start:      start date in list structure: [year,month,day] e.g. [2012,1,28]
 @param dt_end:        end date in list structure: [year,month,day] e.g. [2012,12,31]
 @param dt_timeofday:  what time the stock data was taken
 @param ls_symbols:    list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
 @param non_linear:   true - precise optimization; false - 10% increments & positive weights
 @return: optimized list of allocations by percentage
'''

import time
import matplotlib.pyplot as plt
import CalcStats

def optimizePortfolioAllocations(d_data, dt_start, dt_end, dt_timeofday,
                                  ldt_timestamps, ls_symbols, non_linear):
    ld_alldata = [d_data, dt_start, dt_end, dt_timeofday, ldt_timestamps]
    start = time.time();
    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;
 
    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];
    
    
    if non_linear:
        #Precise optimization:
        
        #Define objective function (sharpe ratio)
        def objective_sharpe():
            (x)
            # allocations by calling scipy's optimize? simulate(dt_start, dt_end, ls_symbols, x)[2];
            return lf_allocations
 
        #Work on this later...
        
    else:
        
        #Imprecise optimization (required in Homework 1)
 
        #Using backtracking and permutation
        #Permutation function
        def permCalc(elements):
            if len(elements) <=1:
                yield elements;
            else:
                for perm in permCalc(elements[1:]):
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
                    li_valid.extend(list(permCalc(li_sol)));
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
            t_Stats = CalcStats(na_normalized_price, allocation);
            if t_Stats[2] > f_CurrMaxSharpe:
                lf_CurrStats = t_Stats
                f_CurrMaxSharpe = t_Stats[2];
                lf_CurrEffAllocation = allocation;
        optimalAllocations = lf_CurrEffAllocation
 
        #Plot portfolio daily values over time period
        #Obtain benchmark $SPX data
        d_spx = d_data['$SPX'].values;
        na_spxprice = d_spx['close'].values;
        na_spxnormalized_price = na_spxprice / na_spxprice[0,:];
        lf_spxStats = CalcStats(na_spxnormalized_price, [1]);
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
        print "Start Date: ", dt_start;
        print "End Date: ", dt_end;
        print "Symbols: ", ls_symbols;
        print "Optimal Allocations: ", optimalAllocations;
        print "Volatility (stdev daily returns): " , lf_CurrStats[0];
        print "Average daily returns: " , lf_CurrStats[1];
        print "Sharpe ratio: " , lf_CurrStats[2];
        print "Cumulative daily return: " , lf_CurrStats[3]; 
        print "Run in: " , (time.time() - start) , " seconds.";
    return optimalAllocations;