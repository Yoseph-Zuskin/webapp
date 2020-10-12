# -*- coding: utf-8 -*-
'''
Streamlit web application for exploring Bank of Canada public data.
'''
import requests
from io import BytesIO
import pandas as pd
import streamlit as st
import plotly.express as px
from pyvalet import ValetInterpreter
__version__ = '0.0.1'
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
    'Explorer Proof of Concept')

st.header('**Developer:** [Yoseph Zuskin](https://linkedin.com/in/Yoseph-Zuskin)'
    ', **Source Code:** [GitHub](https://github.com/Yoseph-Zuskin/webapp)'
    f', **Version:** {__version__}')

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
    df.id = pd.to_datetime(df.id, format='%Y-%m-%d')
    df = df.set_index(df.id.rename('Date'))
    df = df.label.rename('Value')
    return meta, df 
meta, df = get_time_serie(chosen_series)

st.markdown(f'You have selected ***{meta.label}:*** '
    f'*{meta.description}*:')

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

fig = px.line(df[start_date:end_date])
fig.update_layout(showlegend=False)
plot.plotly_chart(fig)

series.subheader('The actual time series data:')
series.dataframe(
    df[start_date:end_date].to_frame().set_index(
        df[start_date:end_date].index.strftime('%Y-%m-%d')))