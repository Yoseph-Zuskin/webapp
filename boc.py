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
* Pandas ([website]{}, [documentation]{}) for time series data handling
* Streamlit ([website]{}, [documentation]{}) for the front-end GUI
* Plotly ([website]{}, [documentation]{}) for interactive plotting

### :pray: Thank you for checking out this application:grey_exclamation: 
'''.format(
    '(https://github.com/tylercroberts/pyvalet)',
    '(https://www.heroku.com/)',
    '(https://pandas.pydata.org/)',
    '(https://pandas.pydata.org/docs/)',
    '(https://www.streamlit.io/)',
    '(https://docs.streamlit.io/en/stable/)',
    '(https://plotly.com/)',
    '(https://plotly.com/python/)'
)
import requests
from io import BytesIO
from base64 import b64encode
import pandas as pd
import streamlit as st
import plotly.express as px
from pyvalet import ValetInterpreter
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
@st.cache
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