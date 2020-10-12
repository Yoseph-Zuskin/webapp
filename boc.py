# -*- coding: utf-8 -*-
'''
Streamlit web application for exploring Bank of Canada public data.
'''
import requests
from io import BytesIO
from base64 import b64encode
import pandas as pd
import streamlit as st
import plotly.express as px
from pyvalet import ValetInterpreter
# -------------------------------------------------------------------------------
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

st.title('Bank of Canada [Open Data](https://github.com/tylercroberts/pyvalet) '
    'Explorer')

st.header('**Developer:** [Yoseph Zuskin](https://linkedin.com/in/Yoseph-Zuskin)'
    ', **Source Code:** [GitHub](https://github.com/Yoseph-Zuskin/webapp)')

groups = boc.list_groups()
group_options = groups.label[groups.label != 'delete']

chosen_group = st.sidebar.selectbox(
    label='Pick a data group from which to select a time series:',
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
chosen_series = st.sidebar.selectbox(
    label='Pick a time series from the selected data group:',
    options=['Click here to select...'] + series_options,
    key='chosen_series')
if chosen_series == 'Click here to select...':
    st.warning('A specific time series must be selected to proceed')
    st.stop()

# Retrieve metadata and data for the chosen time series
@st.cache
def get_time_serie(chosen_series):
    chosen_series = group_series[group_series.label==chosen_series].name.values[0]
    meta, df = boc.get_series_observations(chosen_series, response_format='csv')
    containsdigit = lambda s: any(i.isdigit() for i in s)
    df = df[df.id.apply(containsdigit)] # Filter out non-date index values
    df = df[df.label.apply(containsdigit)] # Filter out non-numeric values
    try:
        df.id = pd.to_datetime(df.id, format='%Y-%m-%d')
    except:
        df.id = pd.to_datetime(df.id)
    df = df.set_index(df.id.rename('Date'))
    df = df.label.rename('Value')
    return meta, df 
meta, df = get_time_serie(chosen_series)

st.markdown(f'You have selected ***{meta.description}***:')

invalid_date_range = False
start_date = st.sidebar.date_input('Start date:', df.index[-min(len(df), 24)])
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

plot, series = st.beta_columns([3, 1])

toggle_smoothing = st.sidebar.select_slider(
    label='Toggle spline smoothing of the plot:',
    options=['no', 'yes'],
    key='toggle_smoothing')
fig = px.line(df[start_date:end_date],
    line_shape='linear' if toggle_smoothing == 'no' else 'spline')
fig.update_layout(showlegend=False)
plot.plotly_chart(fig)

series.subheader('Selected data:')
series.dataframe(
    df[start_date:end_date].to_frame().set_index(
        df[start_date:end_date].index.strftime('%Y/%m/%d')))

def download_link(object_to_download, download_filename, download_link_text):
    """
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

    """
    if isinstance(object_to_download, (pd.DataFrame, pd.Series)):
        object_to_download = object_to_download.to_csv()

    # some strings <-> bytes conversions necessary here
    b64 = b64encode(object_to_download.encode()).decode()
    
    link = (f'<a href="data:file/txt;base64,{b64}" '
        f'download="{download_filename}">{download_link_text}</a>')

    return link

if st.sidebar.button('Download Selection as CSV'):
    tmp_download_link = download_link(
        df[start_date:end_date].rename(meta.label),
        f'{meta.label.replace(" ", "_")}.csv',
        'Click here to download the data within the time range you selected!')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)

if st.sidebar.button('Download Entire Series as CSV'):
    tmp_download_link = download_link(
        df.rename(meta.label),
        f'{meta.label.replace(" ", "_")}.csv',
        'Click here to download the entire series you selected!')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)