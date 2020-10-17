# -*- coding: utf-8 -*-
'''
Custom functions used within the main web application code

Author: Yoseph Zuskin
Last Update: 2020/10/17
'''
import pandas as pd
from base64 import b64encode
from streamlit import cache
# -------------------------------------------------------------------------------
def download_link(object_to_download, download_filename, download_link_text):
    r'''
    Generates a link to download the given object_to_download.
    Author: Chad Mitchell (modified by Yoseph Zuskin)
    Source: https://discuss.streamlit.io/t/4052
    
    Parameters:
    -----------
    object_to_download : pandas.DataFrame
        The object to be downloaded
    download_filename : str
        Filename and extension of file (e.g. mydata.csv, some_txt_output.txt)
    download_link_text : str
        Text to display for download link
        
    Returns:
    --------
    html_link : str
        HTML download link with specified file name and link text
    
    Examples:
    download_link(df, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(code_str, 'YOUR_CODE.py', 'Click here to download code!')
    '''
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv()
    b64 = b64encode(object_to_download.encode()).decode()
    html_link = (f'<a href="data:file/txt;base64,{b64}" '
        f'download="{download_filename}">{download_link_text}</a>')
    return html_link
# -------------------------------------------------------------------------------
@cache
def load_time_series(chosen_series, group_series, api):
    r'''
    Retrieve metadata and data for the chosen time series
    
    Parameters:
    -----------
    chosen_series : list
        List of the time series selected from the chosen data group
    group_series : pandas.DataFrame
        Tabular data contain names, labels, and descriptions of the time series
    api : pyvalet.ValetInterpreter
        Bank of Canada open data API client instance
    
    Returns:
    --------
    data : pandas.DataFrame
        Tabular data containing the selected time series
    
    Examples:
    load_time_series(['Weekly BCPI Total - v52673503'])
    load_time_series(['USD/CAD','EUR/CAD','JPY/CAD'])
    '''
    data = pd.DataFrame()
    for series in chosen_series:
        selection = group_series[group_series.label==series].name.values[0]
        meta, df = api.get_series_observations(
            selection,
            response_format='csv'
        )
        contains_digit = lambda s: any(i.isdigit() for i in s)
        df = df[df.id.apply(contains_digit)] # Filter out non-date index values
        df = df[df.label.apply(contains_digit)] # Filter out non-numeric values
        
        try:
            df.id = pd.to_datetime(
                df.id,
                format='%Y-%m-%d'
            )
        except:
            df.id = pd.to_datetime(df.id)
        
        df = df.set_index(df.id)
        df = df.label.rename(meta.label)
        
        data = pd.concat(
            [data, df],
            axis=1
        )
    data = data.set_index(pd.to_datetime(data.index.rename('Date')))
    data.index.freq = pd.infer_freq(data.index)
    return data
# -------------------------------------------------------------------------------