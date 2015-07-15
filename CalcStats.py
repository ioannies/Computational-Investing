''' 
Calculate Portfolio Statistics 
 @param na_normalized_price: NumPy Array for normalized prices (starts at 1)
 @param lf_allocations:      allocation list
 @return list of statistics:
 @return: (Volatility, Average Return, Sharpe, Cumulative Return)
'''
import numpy as np
import QSTK.qstkutil.tsutil as tsu

def CalcStats(na_normalized_price, lf_allocations):
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