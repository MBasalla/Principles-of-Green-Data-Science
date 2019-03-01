import numpy as np
from datetime import timedelta

def get_price_data(data, timepoint):
    """
    Access price data column
    :param data: Pandas DataFrame
    :param timepoint: datetime in range covered by the dataset
    :return: hourly energy price for a certain point in time
    """
    return data[data['utc_timestamp'] == timepoint]['price'].values[0]


def get_avg_price(data, start, end):
    """

    :param data: Pandas DataFrame
    :param start: datetime in range covered by the dataset
    :param end: datetime in range covered by the dataset
    :return: average hourly energy price for a certain time window
    """

    temp_data = data[data["utc_timestamp"] >= start]
    temp_data = temp_data[temp_data['utc_timestamp'] < end]
    return temp_data.mean().values[0]


def average_scheduling_rule(price, avg_price, percentage=1.):
    """
    Implements rule bz which average scheduler decides to execute one hour of the scheduled computation.
    :param price: current hourly price as float
    :param avg_price: average hourly price as float
    :param percentage: only execute when price below this percentage of average price (default 100%)
    :return: boolean
    """
    return price < avg_price * percentage


def average_scheduler(net_computing_time, slack, data, start_time, percentage = 1):
    """
    Applies the average scheduling scheme described in the paper using the average price of the last 61 days
    (about two months) as a baseline for the decision
    :param net_computing_time:  timedelta
    :param slack: float
    :param data: pandas.DataFrame
    :param start_time: datetime
    :param percentage float
    :return: (float, float)
    """
    # in the beginning the remaining computing time is teh net computing time
    remaining_time = net_computing_time
    estimated_end = start_time + remaining_time
    # the latest possible end is defined by the net computing time and the amount of slack
    latest_end = start_time + net_computing_time * (1 + slack)
    payed = 0
    # time window to calculate average past price
    time_window = timedelta(days=61)
    avg_price = get_avg_price(data, start_time - time_window, start_time)
    now = start_time
    # while still computing time remaining (i.e. while computation not finished)
    while remaining_time > timedelta(days=0, hours=0):
        # get current hourly price

        current_price = get_price_data(data, now)
        # if there is still slack left
        if estimated_end < latest_end:
            # if current price below limit given by rule
            if average_scheduling_rule(current_price, avg_price,percentage):
                # add current price to amount payed
                payed += current_price
                # reduce remaining time by one hour (i.e. compute for one hour)
                remaining_time -= timedelta(hours=1)
            else:
                # else advance estimated end for one hour (i.e. process idle for one hour)
                estimated_end = estimated_end + timedelta(hours=1)
        else:
            # if no slack: advance computation and pay price
            payed += current_price
            remaining_time -= timedelta(hours=1)
        # advance one hour
        now += timedelta(hours=1)

    end = now

    return payed, end - start_time


def optimal_scheduler(net_computing_time,slack,data,start_time):
    """
    Calculates an ideal energy cost saving using slack, given the prices are known in advance.
        :param net_computing_time:  timedelta
        :param slack: float
        :param data: pandas.DataFrame
        :param start_time: datetime
        :return: (float, float)
        """
    # calculate maximum time window
    latest_end = start_time + net_computing_time * (1 + slack)
    # extract price data of maximum time window
    data = data[data["utc_timestamp"] >= start_time]
    data = data[data["utc_timestamp"] < latest_end.replace(microsecond=0, second=0, minute=0)]
    # sort data by price
    sorted = data.sort_values(by="price")
    prices = np.asarray(sorted["price"].values)
    process_duration = int(np.floor(net_computing_time.total_seconds() / 3600))
    # sum n lowest prices where n is the net computation time
    price = np.sum(prices[:process_duration])
    end = sorted["utc_timestamp"].iloc[:process_duration].max()
    return price, end - start_time
