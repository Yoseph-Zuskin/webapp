# -*- coding: utf-8 -*-
app_details = '''
Welcome to the unofficial Bank of Canada open data explorer. This website is an
interactive environment for discovering the data which the Bank of Canada makes
available to the public and downloading the selected data. In the future, this
application will contain built-in forecasting tools, which are currently under
developement. This application was developed using Streamlit and Plotly, and is
hosted for free using Heroku apps. Thanks you for checking out this application! 
Please click above this text to collapse it for a less crowded view :smiley:
'''

import requests
from io import BytesIO
from base64 import b64encode
import pandas as pd
import streamlit as st
import plotly.express as px
from pyvalet import ValetInterpreter
# -------------------------------------------------------------------------------
@st.cache
def load_time_series(chosen_series):
    r'''
    Retrieve metadata and data for the chosen time series
    '''
    data = pd.DataFrame()
    for series in chosen_series:
        selection = group_series[group_series.label==series].name.values[0]
        meta, df = boc.get_series_observations(selection, response_format='csv')
        containsdigit = lambda s: any(i.isdigit() for i in s)
        df = df[df.id.apply(containsdigit)] # Filter out non-date index values
        df = df[df.label.apply(containsdigit)] # Filter out non-numeric values
        try:
            df.id = pd.to_datetime(df.id, format='%Y-%m-%d')
        except:
            df.id = pd.to_datetime(df.id)
        df = df.set_index(df.id.rename('Date'))
        df = df.label.rename(meta.label)
        data = pd.concat([data, df], axis=1)
    return data.set_index(pd.to_datetime(data.index.rename('date')))

def download_link(object_to_download, download_filename, download_link_text):
    r'''
    Generates a link to download the given object_to_download.
    Author: Chad Mitchell (modified by Yoseph Zuskin)
    Source: https://discuss.streamlit.io/t/4052

    object_to_download : str, pd.DataFrame
        The object to be downloaded
    download_filename : str
        Filename and extension of file (e.g. mydata.csv, some_txt_output.txt)
    download_link_text : str
        Text to display for download link

    Examples:
    download_link(df, 'YOUR_DF.csv', 'Click here to download data!')
    download_link('str', 'YOUR_STRING.txt', 'Click here to download your text!')

    '''
    if isinstance(object_to_download, (pd.DataFrame, pd.Series)):
        object_to_download = object_to_download.to_csv()

    # some strings <-> bytes conversions necessary here
    b64 = b64encode(object_to_download.encode()).decode()
    
    link = (f'<a href="data:file/txt;base64,{b64}" '
        f'download="{download_filename}">{download_link_text}</a>')

    return link

# Create client for retrieving data using the Bank of Canada's PyValet API
boc = ValetInterpreter()

st.beta_set_page_config(
    page_title='Bank of Canada Open Data Explorer',
    page_icon=':bank:',
    layout='wide',
    initial_sidebar_state='expanded')

boc_logo = requests.get('https://logos-download.com/wp-content/uploads/'
    '2016/03/Bank_of_Canada_logo.png')
boc_logo = BytesIO(boc_logo.content)
st.sidebar.image(boc_logo, use_column_width=True)

st.title(':bank: Bank of Canada :maple_leaf: [Open Data]'
    '(https://github.com/tylercroberts/pyvalet) Explorer :mag:')

with st.beta_expander(label='Application details', expanded=True):
    st.header(
        '**Developer:** [Yoseph Zuskin](https://linkedin.com/in/Yoseph-Zuskin)'
        ', **Source Code:** [GitHub](https://github.com/Yoseph-Zuskin/webapp)')
    st.markdown(app_details)

groups = boc.list_groups()
group_options = groups.label[groups.label != 'delete']

chosen_group = st.sidebar.selectbox(
    label='Pick a group from which to select a time series:',
    options=['Click here to select...'] + group_options.tolist(),
    key='chosen_group'
)
if chosen_group == 'Click here to select...':
    st.warning('A Bank of Canada data group must be selected to proceed')
    st.stop()

# Retrieve metadata and data on the chosen data group
group_details, group_series = boc.get_group_detail(
    groups[groups.label == chosen_group].name.values[0],
    response_format='csv')

series_options = group_series.set_index(group_series.name).label.tolist()
with st.beta_expander(label='Select time series from group', expanded=True):
    chosen_series = st.multiselect(
        label='Pick a time series from the selected data group:',
        options=series_options,
        key='chosen_series')
    if chosen_series == []:
        st.warning('A specific time series must be selected to proceed')
        st.stop()
    df = load_time_series(chosen_series)

invalid_date_range = False
min_streamlit_date = pd.Timestamp.today() - pd.DateOffset(years=10)
start_date = st.sidebar.date_input('Start date:', min_streamlit_date)
if start_date < df.index[0] or start_date > df.index[-1]:
    st.sidebar.error('Error: Start date must be within the time series range of '
        f'{df.index[0].date()} to {df.index[-1].date()}')
    invalid_date_range = True
end_date = st.sidebar.date_input('End date:', df.index[-1])
if end_date < df.index[0] or end_date > df.index[-1]:
    st.sidebar.error('Error: End date must be within the time series range of '
        f'{df.index[0].date()} to {df.index[-1].date()}')
    invalid_date_range = True
if invalid_date_range:
    st.warning('Valid start and end dates must be chosen to proceed')
    st.stop()

if st.sidebar.button('Download Selection as CSV'):
    tmp_download_link = download_link(
        df[start_date:end_date],
        f'{chosen_group.replace(" ", "_")}.csv',
        'Click here to download the data within the time range you selected!')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)

if st.sidebar.button('Download Entire Series as CSV'):
    tmp_download_link = download_link(
        df,
        f'{chosen_group.replace(" ", "_")}.csv',
        'Click here to download the entire series you selected!')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)

with st.beta_expander(label=f'Display selected time series', expanded=False):
    st.dataframe(df[start_date:end_date].set_index(
            df[start_date:end_date].index.strftime('%Y/%m/%d')))

with st.beta_expander(label=f'Plot selected time series', expanded=True):
    toggle_smoothing = st.checkbox(
        label='Toggle spline smoothing of the plot',
        key='toggle_smoothing')
        
    try:
        fig = px.line(df[start_date:end_date],
            line_shape='spline' if toggle_smoothing else 'linear')
    except:
        fig = px.line(df[start_date:end_date],
            line_shape='hv' if toggle_smoothing else 'linear')
    st.plotly_chart(fig, use_container_width=True)