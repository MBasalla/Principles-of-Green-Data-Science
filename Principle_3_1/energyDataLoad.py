import pandas as pd
from datetime import datetime
import os


def load_raw_data(directory):
    """
    Returns a pandas DataFrame containing the raw data used for computing the energy cost savings.
    If file is not found in the directory it is fetched from a remote source.
    The data can be downloaded from https://doi.org/10.25832/time_series/2018-06-30.
    :param directory: string of the directory the data is saved locally
    :return: DataFrame of hourly energy prices of several european countries
    """
    if os.path.isfile(directory + "/time_series_60min_singleindex.csv"):
        df = pd.read_csv(directory + "/time_series_60min_singleindex.csv")
    else:
        url = "https://data.open-power-system-data.org/time_series/2018-06-30/time_series_60min_singleindex.csv"
        df = pd.read_csv(url)
        print("Finished loading remote data.")
    return df


def load_data_germany2017(directory):
    """
        Returns a pandas DataFrame containing the preprocessed and cleaned data used for computing the energy cost
        savings.
        If file is not found in the directory it is fetched from a remote source.
        This is the data as used for the paper.
        The data can be downloaded from https://doi.org/10.25832/time_series/2018-06-30.
        :param directory: string of the directory the data is saved locally
        :return: DataFrame of hourly energy prices of several european countries
    """
    # is data already locally available
    if os.path.isfile(directory + "/germany2017.csv"):
        germany_2017 = pd.read_csv(directory + "/germany2017.csv", infer_datetime_format=True,separator=";")
        germany_2017['utc_timestamp'] = germany_2017['utc_timestamp'].apply(lambda x: parse(x))
    # process raw data
    else:
        raw_data = load_raw_data(directory)
        # extract all column names
        columns = list(raw_data.columns)
        # extract all columns containing price information
        price_columns = []
        for c_name in columns:
            if 'price' in c_name:
                price_columns.append(c_name)
        # only keep columns containing price data
        price_data = raw_data[['utc_timestamp', 'cet_cest_timestamp'] + price_columns].dropna(axis=0, how='all')
        # remove all columns containing missing values
        price_data = price_data.dropna(axis=1, how='any')
        # transform time stamps into datetime format
        price_data['utc_timestamp'] = price_data['utc_timestamp'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
        price_data['cet_cest_timestamp'] = price_data['cet_cest_timestamp'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z'))
        # extract data for germany 2017 (with two months of 2016 for average prices of previous two months
        germany_2017 = price_data[datetime(2016, 11, 1) <= price_data["utc_timestamp"]]
        germany_2017 = germany_2017[germany_2017["utc_timestamp"] < datetime(2018, 1, 1)]
        germany_2017 = germany_2017[["utc_timestamp", "DE_price_day_ahead"]]

        # remove outliers (data below 1% and below 99% quantile
        lower = price_data["DE_price_day_ahead"].quantile(.01)
        upper = price_data["DE_price_day_ahead"].quantile(.99)
        germany_2017["DE_price_day_ahead"] = germany_2017["DE_price_day_ahead"].clip(lower,upper)
        germany_2017.rename(index=str, columns={"DE_price_day_ahead": "price"}, inplace=True)
    if os.path.isdir(directory):
        germany_2017.to_csv(directory + "/germany2017.csv")
    return germany_2017


