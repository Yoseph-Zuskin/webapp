# -*- coding: utf-8 -*-
app_details = '''
:wave:Welcome to the unofficial Bank of Canada open data exploration (and
forecasting coming soon) web application. Please click on "Application details"
above :point_up: this text to minimize it for a less crowded view :smiley:. If
you want to learn more about this web application, continue reading this section,
otherwise you may begin your exploration by selecting a data group on the sidebar
that you will find on the left :point_left:.

### Website Overview
This website is an interactive environment for discovering the data which the
Bank of Canada [makes available to the public]{}. This application is hosted for
free on [Heroku]{} and was developed using the following Python 3 libraries:
* Requests ([documentation]{}) for retrieving external web assets
* Pandas ([website]{}, [documentation]{}) for time series data handling
* Streamlit ([website]{}, [documentation]{}) for the front-end GUI
* Plotly ([website]{}, [documentation]{}) for interactive plotting

### :pray: Thank you for checking out this application:grey_exclamation: 
'''.format(
    '(https://github.com/tylercroberts/pyvalet)',
    '(https://www.heroku.com/)',
    '(https://requests.readthedocs.io/en/master/)',
    '(https://pandas.pydata.org/)',
    '(https://pandas.pydata.org/docs/)',
    '(https://www.streamlit.io/)',
    '(https://docs.streamlit.io/en/stable/)',
    '(https://plotly.com/)',
    '(https://plotly.com/python/)'
)
import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from io import BytesIO
from pyvalet import ValetInterpreter
from custom import download_link, load_time_series
# -------------------------------------------------------------------------------
st.beta_set_page_config( # Configure page title, icon, layout, and sidebar state
    page_title='Bank of Canada Open Data Explorer',
    page_icon=':bank:',
    layout='wide',
    initial_sidebar_state='expanded')

# Retrieve and display the Bank of Canada's logo on the top of the sidebar
boc_logo = requests.get('https://logos-download.com/wp-content/uploads/'
    '2016/03/Bank_of_Canada_logo.png')
boc_logo = BytesIO(boc_logo.content)
st.sidebar.image(boc_logo, use_column_width=True)

# Define the web application title
st.title(':bank: Bank of Canada :maple_leaf: [Open Data]'
    '(https://github.com/tylercroberts/pyvalet) Explorer :mag:')
# -------------------------------------------------------------------------------
# Introductory expander section covering overall application details
with st.beta_expander(label='Application details', expanded=True):
    st.header(
        '**Developer:** [Yoseph Zuskin](https://linkedin.com/in/Yoseph-Zuskin)'
        ', **Source Code:** [GitHub](https://github.com/Yoseph-Zuskin/webapp)')
    st.markdown(app_details)
# -------------------------------------------------------------------------------
api_client = ValetInterpreter() # API Client for the Bank of Canada's open data
groups = api_client.list_groups() # Retrieve list of available data groups
group_options = groups.label[groups.label != 'delete'] # Filter data groups list

# Enable selection of a specific data group using a selectbox in the sidebar
chosen_group = st.sidebar.selectbox(
    label='Pick a group from which to select a time series:',
    options=['Click here to select...'] + group_options.tolist(),
    key='chosen_group'
)
if chosen_group == 'Click here to select...':
    st.warning('A Bank of Canada data group must be selected to proceed')
    st.stop()

# Retrieve metadata and data on the chosen data group
group_details, group_series = api_client.get_group_detail(
    groups[groups.label == chosen_group].name.values[0],
    response_format='csv'
)
# Parse the list of time series available in the selected data group
series_options = group_series.set_index(group_series.name).label.tolist()
# -------------------------------------------------------------------------------
# Section to select and filter date range of multiple time series in same group
with st.beta_expander(label='Select time series from data group',
                      expanded=True):
    chosen_series = st.multiselect(
        label=f'Time series within the "{chosen_group}" data group:',
        options=series_options,
        key='chosen_series')
    if chosen_series == []:
        st.warning('At least one time series must be selected to proceed')
        st.stop()
    df = load_time_series(chosen_series, group_series, api_client)
    st.write('Please note that Streamlit limits date selection to last 10 years')
    if st.button('So you can click here to enable manual entry of any date'):
        overwrite_start_date = st.sidebar.text_input(
            label='Enter start date manually:',
            value=df.index[0].strftime('%Y/%m/%d'),
            max_chars=10,
            key='overwrite_start_date'
        )
        overwrite_end_date = st.sidebar.text_input(
            label='Enter end date manually:',
            value=df.index[-1].strftime('%Y/%m/%d'),
            max_chars=10,
            key='overwrite_end_date'
        )
    else:
        overwrite_start_date, overwrite_end_date = None, None

# Define and parse start_date and end_date variables from date_input widgets
invalid_date_range = False
min_streamlit_date = pd.Timestamp.today() - pd.DateOffset(years=10)

if overwrite_start_date is None:
    start_date = st.sidebar.date_input('Select start date:',
        df.index[0] if df.index[0] > min_streamlit_date else min_streamlit_date)
elif overwrite_start_date is not None:
    start_date = pd.to_datetime(overwrite_start_date)

if start_date < df.index[0] or start_date > df.index[-1]:
    st.sidebar.error('Error: Start date must be within the time series range of '
        f'{df.index[0].date()} to {df.index[-1].date()}')
    invalid_date_range = True

if overwrite_start_date is None:
    end_date = st.sidebar.date_input('Select end date:', df.index[-1])
elif overwrite_end_date is not None:
    end_date = pd.to_datetime(overwrite_end_date)

if end_date < df.index[0] or end_date > df.index[-1]:
    st.sidebar.error('Error: End date must be within the time series range of '
        f'{df.index[0].date()} to {df.index[-1].date()}')
    invalid_date_range = True

if invalid_date_range:
    st.warning('Valid start and end dates must be chosen to proceed')
    st.stop()
# -------------------------------------------------------------------------------
# Enable downloading of the filtered selection of time series data as CSV files
if st.sidebar.button('Download Filtered Selection as CSV'):
    tmp_download_link = download_link(
        df[start_date:end_date],
        f'{chosen_group.replace(" ", "_")}.csv',
        'Click here to download the data within the time range you selected!'
    )
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)

# Enable downloading of the entire selection of time series data as CSV files
if st.sidebar.button('Download Entire Selection as CSV'):
    tmp_download_link = download_link(
        df,
        f'{chosen_group.replace(" ", "_")}.csv',
        'Click here to download the entire series you selected!'
    )
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
# -------------------------------------------------------------------------------
# Expander section to display the selected time series data in tabular format
with st.beta_expander(label='Display selected time series data'):
    st.dataframe(
        df[start_date:end_date].set_index(
            df[start_date:end_date].index.strftime('%Y/%m/%d')
        )
    )
# Expander section to display the selected time series data as interactive plot
with st.beta_expander(label='Plot selected time series data'):
    toggle_smoothing = st.checkbox(
        label='Toggle spline smoothing',
        key='toggle_smoothing')        
    try: # Spline smoothing option of plots with few observations
        fig = px.line(
            df[start_date:end_date],
            line_shape='spline' if toggle_smoothing else 'linear'
        )
    except: # Spline smoothing option of plots with many observations
        fig = px.line(
            df[start_date:end_date],
            line_shape='hv' if toggle_smoothing else 'linear'
        )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)