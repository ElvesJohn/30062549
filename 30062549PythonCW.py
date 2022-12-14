import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
#from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
st.title('Analysis of Crime Data in South Wales, UK')
st.markdown('For period Jan - Sep 2022')
st.sidebar.title('Analysis Options')
st.sidebar.markdown('Please follow the instructions below to access the three analysis sections.')

path = os.path.dirname(__file__)
data_url =  os.path.join(path, 'south-wales-street.csv')  

@st.cache(persist=True)
def load_data():
    data = pd.read_csv(data_url)
    data['Month'] = pd.to_datetime(data['Month'] ) 
    print(data.head())
    return data

data = load_data()
data = data[(data['Latitude'].notnull())&(data['Longitude'].notnull())]
data = data[(data['Longitude']<-2.744003)]
data = data[(data['Latitude']<51.918541)]
data['Month']=pd.to_datetime(data['Month'])
data['year'] = pd.DatetimeIndex(data['Month']).year
data['month_real'] = pd.DatetimeIndex(data['Month']).month
data['region'] = data['LSOA name'].str.split().str.get(0)
data.reset_index(inplace = True)
data.drop(['index','Unnamed: 0','Falls within','Reported by','Last outcome category','latitude','longitude','Crime ID','Context','Month','LSOA code','LSOA name'], axis = 1, inplace = True)
data = data.rename(columns={'Latitude': 'lat', 'Longitude':'lon'})
st.sidebar.header('The crime map by month')
month  = st.sidebar.number_input('Month', 1, 9)
map_data_num_crime = data.query('month_real == @month')['lon'].count()
if not st.sidebar.checkbox('Close', True, key = '1'):
    st.markdown('### Crime locations by month')
    st.map(data.query('month_real == @month'))
    st.markdown('%i crimes in month %i' %(map_data_num_crime,month))
    if st.sidebar.checkbox('Show raw data', False):
        st.write(data.query('month_real == @month'))
#st.write(data)