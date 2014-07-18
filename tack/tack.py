from __future__ import division, print_function

import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

import datetime as datetime
from collections import defaultdict

class Invite():
    """
    Each invite is associated with a request.
    Each quote is associated with an invite.
    Only requests have location and category info and only quotes
    have info on whether or not the invite received a response.

    class Invite gathers these external fields for easy access
    given only the invite itself.
    """

    def __init__(self, invite_id, request_id, sent_time,
                    category_id, location_id, quote_response):
        self.invite_id = invite_id
        self.request_id = request_id
        self.sent_time = datetime.datetime.strptime(
                    sent_time, "%Y-%m-%d %H:%M:%S.%f")
        self.category_id = category_id
        self.location_id = location_id
        self.response = quote_response
        
    def __str__(self):
        string = "invite_id = {0}:\n\trequest_id = {1}\n\tsent_time = {2}\n" \
                 .format(self.invite_id, self.request_id, self.sent_time) \
                 + "\tcategory_id = {0}\n\tlocation_id = {1}\n" \
                .format(self.category_id, self.location_id)
        return string

def daily_response_dataframe(invite_list):
    '''
    Parameters
    ----------
    invite_list

    Returns
    -------
    df          
    '''
    ts_quotes = defaultdict(int)
    ts_invites = defaultdict(int)

    for inv in invite_list:
        bin_id = inv.sent_time.date()
        ts_quotes[bin_id] += inv.response
        ts_invites[bin_id] += 1

    ydata = []
    xdata = []
    for day in ts_quotes:
         ydata.append(100*ts_quotes[day] / ts_invites[day])
         xdata.append(day)
    data = sorted( zip(xdata,ydata), key=lambda t: t[0])
    df = pd.DataFrame(data)
    df.columns = ['sent_time', 'response']

    return df

def weekly_response_dataframe(invite_list):
    '''
    Parameters
    ----------
    invite_list

    Returns
    -------
    df          
    '''
    ts_quotes = defaultdict(int)
    ts_invites = defaultdict(int)

    for inv in invite_list:
        bin_id = to_weeks(inv.sent_time)
        ts_quotes[bin_id] += inv.response
        ts_invites[bin_id] += 1

    ydata = []
    xdata = []
    for day in ts_quotes:
         ydata.append(100*ts_quotes[day] / ts_invites[day])
         xdata.append(day)
    data = sorted( zip(xdata,ydata), key=lambda t: t[0])
    df = pd.DataFrame(data)
    df.columns = ['sent_time', 'response']

    return df

def to_weeks(datetime_obj):
    '''
    Parameters
    ----------
    datetime_obj:      datetime object

    Returns
    -------
    The day number of the year. (0-365)
    '''
    ywd = datetime_obj.isocalendar()
    
    return ywd[1]

def to_days(datetime_obj):
    '''
    Parameters
    ----------
    datetime_obj:      datetime object

    Returns
    -------
    The day number of the year. (0-365)
    '''
    ywd = datetime_obj.isocalendar()
    
    return ywd[1] * 7 + ywd[2]

def daily_trend_line(df, show=False,
            save=False, fname="default_trend_plot.pdf", title=None):
    '''
    
    Returns
    -------
    params
    '''
    x = np.array([to_days(x) for x in df['sent_time']])
    y = df['response']

    params = stats.linregress(x, y)
    y_hat = x * params[0] + params[1]

    fig, ax = plt.subplots()
    ax.plot(df['sent_time'], y_hat, '--k')
    
    dateFmt = mdates.DateFormatter('%b-%d')
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_ylabel("% of Invites Quoted")
    ax.set_ylim([-1,101])
    
    if title is not None:
        ax.set_title(title)

    #fig.autofmt_xdate()
    
    df.plot(x='sent_time', y='response')

    if save:
        plt.savefig(fname)    
    if show:
        plt.show()
    plt.close()
    return params

def weekly_trend_line(df, show=False,
            save=False, fname="default_trend_plot.pdf", title=None):
    '''
    
    Returns
    -------
    params
    '''
    x = df['sent_time']
    y = df['response']

    params = stats.linregress(x, y)
    y_hat = x * params[0] + params[1]

    fig, ax = plt.subplots()
    ax.plot(df['sent_time'], y_hat, '--k')
    
    ax.set_xlabel("sent time (week of year)")
    ax.set_ylabel("% of Invites Quoted")
    ax.set_ylim([-1,101])
    
    if title is not None:
        ax.set_title(title)

    #fig.autofmt_xdate()
    
    df.plot(x='sent_time', y='response')

    if save:
        plt.savefig(fname)    
    if show:
        plt.show()
    plt.close()
    return params

def daily_quote_growth(df, fit_params):
    '''
    '''
    min_sent = min(df['sent_time'])
    max_sent = max(df['sent_time'])
    m = fit_params[0]
    y0 = fit_params[1]
    fit = lambda x: m * to_days(x) + y0
    delta_rate = fit(max_sent) - fit(min_sent)

    return delta_rate

def weekly_quote_growth(df, fit_params):
    '''
    '''
    min_sent = min(df['sent_time'])
    max_sent = max(df['sent_time'])
    m = fit_params[0]
    y0 = fit_params[1]
    fit = lambda x: m * x + y0
    delta_rate = fit(max_sent) - fit(min_sent)

    return delta_rate

def by_group(group_dict, groups):
    group_growth = {}
    for group_id in group_dict:
        df_daily = daily_response_dataframe(group_dict[group_id])

        daily_params = daily_trend_line(df_daily)
        print(groups[group_id], len(df_daily), daily_params[3])
        if daily_params[3] > 0.05 or len(df_daily) < 10:
            df_week = weekly_response_dataframe(group_dict[group_id])
            week_params = weekly_trend_line(df_week)
            print("\t", week_params[3])
            if week_params[3] > 0.05 or len(df_week) < 5:
                continue
            else:
                group_growth[group_id] = weekly_quote_growth(df_week, week_params)
        else:
            group_growth[group_id] = daily_quote_growth(df_daily, daily_params)

    group_list = [(groups[x], group_growth[x]) for x in group_growth]
    group_list.sort(key=lambda t: t[1])
    print(group_list)

def main():
    # Connect to the database
    db = sqlite3.connect("invite_dataset.sqlite")
    c = db.cursor()

    # To get the actual names of the categories/locations
    categories = dict(c.execute("SELECT * FROM categories;").fetchall())
    locations = dict(c.execute("SELECT * FROM locations;").fetchall())

    # Collect all the invites in a single list
    all_invites = []
    query_invites = """SELECT invite_id, request_id, sent_time
                       FROM invites;"""
    raw_invites = c.execute(query_invites).fetchall()
    for invite_id, request_id, sent_time in raw_invites:
        # Get the category_id and location_id from the request table
        query_requests = """SELECT category_id, location_id
                            FROM requests
                            WHERE request_id = {0};""".format(request_id)
        category_id, location_id = c.execute(query_requests).fetchone()
    
        # Get the response to each invite from the quotes table
        # quote_response is 0/1 valued.
        query_quotes = """SELECT count(*)
                          FROM quotes
                          WHERE invite_id = {0};""".format(invite_id)
        quote_response = c.execute(query_quotes).fetchone()[0]
    
        # Add the newly processed Invite to the all_invites list.
        all_invites.append(Invite(invite_id, request_id, sent_time,
                                  category_id, location_id, quote_response))

    ### ANALYSIS ###
    # Plot and fit all_invites data using "daily" binning
    df_all = daily_response_dataframe(all_invites)

    all_fit_params = daily_trend_line(df_all, fname="All_Invites_daily.pdf",   
                     title="All Invites (daily bins)", show=True,save=True)
    p_value = all_fit_params[3]
    # Use fit to calculate the quote growth for all invites
    all_growth = daily_quote_growth(df_all, all_fit_params)
    print("All Invite Quote/Invite Percentage Growth(daily): ", all_growth, p_value)

    # Plot and fit all_invites data using "weekly" binning
    df_all = weekly_response_dataframe(all_invites)
    print(df_all)

    all_fit_params = weekly_trend_line(df_all, fname="All_Invites_weekly.pdf",
                     title="All Invites (weekly bins)", show=True,save=True)
    p_value = all_fit_params[3]
    # Use fit to calculate the quote growth for all invites
    all_growth = weekly_quote_growth(df_all, all_fit_params)
    print("All Invite Quote/Invite Percentage Growth(weekly): ",
                all_growth, p_value)

    # Since categories and locations are important,
    # do as above for grouped dicts

    # Break down by the category_id and the location_ids
    by_category = defaultdict(list)
    by_location = defaultdict(list)
    for invite in all_invites:
        by_category[invite.category_id].append(invite)
        by_location[invite.location_id].append(invite)

    # Repeat the above analysis for all_invites for each sublist in
    # by_category and by_location
    # Because there are many categories and locations, there are some
    # sparse invite lists. If the number of days for which there was
    # an invite is less than 30, that category/location is skipped.
    by_group(by_location, locations)
    by_group(by_category, categories)
    

if __name__ == "__main__":
    main()
