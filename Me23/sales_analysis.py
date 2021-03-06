'''
This script is for analyzing some data for an interview at 23andMe
Written on March 23, 2014 by
Ryan Applegate
'''
from __future__ import division, print_function

import glob as glob
import datetime as dt
import numpy as np

# Plotting imports
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import brewer2mpl
bmap = brewer2mpl.get_map('Set2', 'qualitative', 7)
matplotlib.rcParams['axes.color_cycle'] = bmap.mpl_colors

def daily_sales_accum(file_paths):
    '''
    Parameters
    ----------
    file_paths:     list of file paths to the data

    Returns
    -------
    dates:          ndarray, shape=(N_days)
    sales_male:     ndarray, shape=(N_days)
    sales_female:   ndarray, shape=(N_days)
    sales_quartile: ndarray, shape=(N_days,4)
    dayIdx:         dict, date: array_index
    '''

    # 1st pass: get all the unique dates in the data
    dates = set([])
    for fpath in file_paths:
         with open(fpath) as csvfobj:
            headers = csvfobj.readline()
            for line in csvfobj:
                date_time, gender = line.split(',')
                dateObj = dt.datetime.strptime(date_time.strip() \
                                              ,"%Y-%m-%d %H:%M:%S")
                # Put the date in the set, minus the time piece
                dates.add(dateObj.date())

    # Order the unique dates and build a index mapping for array indexing
    dates = sorted(dates)
    indexes = range(len(dates))
    dayIdx = dict(zip(dates, indexes))

    # Initialize the arrays for male, female, part of the day sales
    N_days = len(dates)    
    sales_male = np.zeros(N_days)
    sales_female = np.zeros(N_days)
    sales_quartile = np.zeros( shape=(N_days,4) )

    # 2nd pass: populate the arrays using the dayIdx mapping
    for fpath in file_paths:
         with open(fpath) as csvfobj:
            headers = csvfobj.readline()
            for line in csvfobj:
                date_time, gender = line.split(',')
                dateObj = dt.datetime.strptime(date_time.strip() \
                                              ,"%Y-%m-%d %H:%M:%S")
                if gender.strip() == 'male':
                    sales_male[dayIdx[dateObj.date()]] += 1
                else:
                    sales_female[dayIdx[dateObj.date()]] += 1
                quartileIdx = dateObj.hour // 6
                sales_quartile[dayIdx[dateObj.date()]][quartileIdx] += 1

    return dates, sales_male, sales_female, sales_quartile, dayIdx

def pie_sales_plot(sales_time):
    '''
    Parameters
    ----------
    sales_time:         ndarray, shape=(days,4)
    '''
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    labels = ['night', 'morning', 'afternoon', 'evening']
        
    answer = np.sum(sales_time, axis=0)
    total = np.sum(answer)
    print(answer, total)
    fracs = answer / total
    explode = (0, 0, 0.05, 0)
    ax.pie(fracs, explode=explode, labels=labels, \
           autopct='%1.1f%%', startangle=90, colors=bmap.mpl_colors,shadow=True)
    ax.set_title("Sales Time of Day for 50 Weeks")

    plt.savefig('TimeOfDaySales.pdf', transparent=True)
        
def plot_daily_sales(x, y):
    '''
    Parameters
    ----------
    x:          ndarray of datetime objects
    y:          ndarray of sales numbers
    '''
    months = mdates.MonthLocator()
    monthsFmt = mdates.DateFormatter('%b-%y')

    fig, ax = plt.subplots()
    ax.scatter(x, y, c='k', label="All Sales", edgecolors='none', alpha=0.7)

    # Set the major x-axis to show months
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.set_ylabel("Daily Product Sales (Number)")

    legend = ax.legend(loc='lower right', shadow=True)
    fig.autofmt_xdate()

    plt.savefig("DailySalesNumbersFINAL.pdf", transparent=True)

def plot_daily_components(dates, y, y_male, y_female):
    '''
    x:          ndarray of datetime objects
    y:          ndarray of sales numbers
    y_male:     ndarray of sales numbers to male customers
    y_female:   ndarray of sales numbers to female customers
    '''
    months = mdates.MonthLocator()
    monthsFmt = mdates.DateFormatter('%b-%y')

    fig, ax = plt.subplots()
    ax.scatter(dates, y, c='k', label='All Sales',edgecolors='none', alpha=0.7)

    # Set the major x-axis to show months
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.set_ylabel("Daily Product Sales (Number)")

    # Add the component data
    ax.scatter(dates, y_male, c='r', marker='s', s=20,
               label='Sales to Males', edgecolors='none', alpha=0.7)
    ax.scatter(dates, y_female, c='b', marker='^', s=24,
               label='Sales to Females', edgecolors='none', alpha=0.7)

    legend = ax.legend(loc='upper left', shadow=True)
    fig.autofmt_xdate()

    plt.savefig("DailySalesComponentsFINAL.pdf", transparent=True)

def line_area(dates, sales_time):
    '''

    '''
    months = mdates.MonthLocator()
    monthsFmt = mdates.DateFormatter('%b-%y')
    labels = ['night', 'morning', 'afternoon', 'evening']

    fig, ax = plt.subplots()
    stacked = ax.stackplot(dates, sales_time.T)

    # Proxy Artists
    proxy = [plt.Rectangle((0,0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stacked]

    # Set the major x-axis to show months
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.set_ylabel("Daily Product Sales (Number)")

    legend = ax.legend(proxy, labels, loc='upper left', shadow=True)
    fig.autofmt_xdate()

    plt.savefig("DataSalesTimeFilledLines.pdf", transparent=True) 


def find_jump(dates, y_sales):
    '''
    Parameters
    ----------
    dates:          ndarray of all days for which there was a sale
    y_sales:        ndarray of all sales numbers for each day in dates
    '''
    N = len(y_sales)

    all_mu1 = np.zeros(N)
    all_sig1 = np.zeros(N)
    all_mu2 = np.zeros(N)
    all_sig2 = np.zeros(N)

    # Iterate over all possible data splits into 2 sub-arrays
    # for each split, calculate the statistics for both sub-arrays created
    for split in range(3,N-3):
        mu1 = np.mean(y_sales[:split])
        sigma1 = np.std(y_sales[:split])
        mu2 = np.mean(y_sales[split:])
        sigma2 = np.std(y_sales[split:])
        all_mu1[split] = mu1
        all_sig1[split] = sigma1
        all_mu2[split] = mu2
        all_sig2[split] = sigma2

    # Build and minimize over the joint variance of the two sub-arrays
    sigma_prod = all_sig1 ** 2 + all_sig2 ** 2
    loc = 3 + np.argmin(sigma_prod[3:-3])

    mu1_loc = all_mu1[loc]
    sig1_loc = all_sig1[loc]
    mu2_loc = all_mu2[loc]
    sig2_loc = all_sig2[loc]

    # Pick some values near the proposed split and find the p-values
    vals = y_sales[loc-3:loc+3]
    p_vals = p_values(vals, mu1_loc, sig1_loc)

    return dates[loc], p_vals[3], mu1_loc, sig1_loc, mu2_loc, sig2_loc

def p_values(tests, mu, sigma):
    '''
    Parameters
    ----------
    tests:      array-like of test values in the normal distribution
    mu:         the mean of the normal distribution
    sigma:      the std of the normal distribution

    Returns
    -------
    p-value:    the two tailed p-value of all values in tests    
    '''
    from scipy.special import erf

    z_score = abs((tests - mu) / sigma)
    p = 0.5 * (1 + erf(z_score / np.sqrt(2)) )

    return 2 * (1 - p)

def main():

    # Gather all the paths to csv data files
    pathnames = glob.glob('data/sales*')

    # Numpy ndarrays accumulate the sales for each day
    # dates has the dependent axis for most analyses
    # sales_male and sales_female are number of sales per day
    # sales_time has a of 4 entries for the quartile of the day
    # dayIdx maps a datetime object to the index for the array
    dates, sales_male, sales_female, \
                sales_time, dayIdx = daily_sales_accum(pathnames)

    # Combine male and female sales into a total sales array
    sales_total = sales_male + sales_female

    # Plot the total sales data
    plot_daily_sales(dates, sales_total)

    # Find the date for which total sales has a sharp change
    # Also calculate the p-value assuming two normal distributions
    jump_date, p_value, mu1, sig1, mu2, sig2 = find_jump(dates, sales_total)
    jump_idx = dayIdx[jump_date]
    print("Optimal data split found at ", dates[jump_idx])
    print("Calculate the p-value for the first point to the right of the split")
    print("belonging to the left of the split using a normal distribution.")
    print("\nDaily Product Sales at jump is {0}".format(sales_total[jump_idx]))
    print("Normal distribution with mu={0:2.2f},\
                                    sigma={1:2.2f}".format(mu1,sig1))
    print("p-value:", p_value)

    # Plot the sales_male and sales_female separately along with sales_total
    plot_daily_components(dates, sales_total, sales_male, sales_female)

    # Plot the sales_time data by accumulating over all 50 weeks to build
    # the percentages that slice the pie
    pie_sales_plot(sales_time)
    line_area(dates,sales_time)

    # Show the plots
    plt.show()

if __name__ == "__main__":
    main()
