import streamlit as st
import pandas as pd
import numpy as np
import statsmodels as sm
import plotly.express as px
import seaborn as sns
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

#data processing and aggregation
data = load_data()
data = data[(data['Latitude'].notnull())&(data['Longitude'].notnull())]
data = data[(data['Longitude']<-2.744003)]
data = data[(data['Latitude']<51.918541)]
data['Month']=pd.to_datetime(data['Month'])
data['year'] = pd.DatetimeIndex(data['Month']).year
data['month_real'] = pd.DatetimeIndex(data['Month']).month
data['region'] = data['LSOA name'].str.split().str.get(0)
data.reset_index(inplace = True)
data.drop(['index','Unnamed: 0','Falls within','Reported by','Last outcome category','Crime ID','Context','Month','LSOA code','LSOA name'], axis = 1, inplace = True)
data = data.rename(columns={'Latitude': 'lat', 'Longitude':'lon'})

data = data.dropna(subset=['region'])

grouped_month = data.groupby('month_real')['lon'].size().reset_index(name='Counts')
grouped_month = grouped_month.rename(columns={'month_real': 'Month'})

grouped_region = data.groupby('region')['lon'].size().reset_index(name='Counts')

grouped_crime = data.groupby('Crime type')['lon'].size().reset_index(name='Counts')

#Summary plots
st.sidebar.header('Summary analysis of the data sets')
if not st.sidebar.checkbox('Close', True, key = '01'):
    plt.figure()
    fig1, ax = plt.subplots(1, 2, figsize = (12,6))
    sizes_month = grouped_month['Counts']
    labels_month = grouped_month['Month']
    ax[0].pie(sizes_month, labels=labels_month, autopct='%1.1f%%', startangle=90)
    ax[0].set_title("Percentage of crime counts by month")
    
    sizes_region= grouped_region['Counts']
    labels_region = grouped_region['region']
    ax[1].pie(sizes_region, labels=labels_region, autopct='%1.1f%%', startangle=90)
    ax[1].set_title("Percentage of crime counts by region")
    st.pyplot(fig1)
    
    plt.figure()
    sizes_crime= grouped_crime['Counts']
    labels_crime = grouped_crime['Crime type']
    plt.pie(sizes_crime, labels=labels_crime, autopct='%1.1f%%', startangle=90)
    plt.title("Percentage of crime counts by crime type")    
    st.pyplot(plt)


#Crime map by month
st.sidebar.header('The crime map by month')
month  = st.sidebar.number_input('Select month', 1, 9)
map_data_num_crime = data.query('month_real == @month')['lon'].count()

if not st.sidebar.checkbox('Close', True, key = '1'):
    st.markdown('### Crime locations by month')
    st.map(data.query('month_real == @month'))
    st.markdown('%i crimes in month %i' %(map_data_num_crime,month))
    if st.sidebar.checkbox('Show raw data', False):
        st.write(data.query('month_real == @month'))


#top crime types by region
st.sidebar.header('Top crime types by regrion')

choice = st.sidebar.multiselect('Select region(s)', ('Bridgend', 'Caerphilly', 'Cardiff', 'Carmarthenshire',
       'Merthyr', 'Monmouthshire', 'Neath', 'Newport', 'Powys',
       'Rhondda', 'Swansea', 'Blaenau',
       'Torfaen'), key ='22')

# Function to plot charts based on certain location search terms.

def location_crime(df,search_field, search_term, Y):

    subset = df[df[search_field].str.contains(search_term)]

    plt.figure(figsize=(9,9))
    sns.countplot(data=subset, y=Y,
    order=subset[Y].value_counts().index[:10])
    Title = 'Crimes Most Committed at ' + search_term
    plt.title(Title, fontsize=15)
    st.pyplot(plt)


if len(choice) >0:
    choice_data = data[data['region'].isin(choice)]

    for search_term in choice:
        location_crime(data,'region', search_term, 'Crime type')

#Time sereis and regression analysis
grouped_df = data.groupby('month_real')['lon'].size().reset_index(name='Counts')
grouped_df = grouped_df.rename(columns={'month_real': 'Month'})

st.sidebar.header('Time series and regression analysis')
if not st.sidebar.checkbox('Close', True, key = '31'):
    #st.markdown('### Time series plot of total crime counts')
    #fig_timeseries = px.histogram(data, x = 'month_real', y = 'lon', histfunc='count')
    #st.plotly_chart(fig_timeseries)
    plt.figure(figsize=(9,9))
    sns.lmplot(x = 'Month', y = 'Counts', data = grouped_df)
    Title2 = 'Time series plot of total crime counts by month' 
    plt.title(Title2, fontsize=12)
    st.pyplot(plt)
    
    #get p values of linear regression
    model = sm.OLS(grouped_df['Counts'], sm.add_constant(grouped_df['Month'])).fit()
    p_value_Month = np.round(model.pvalues[1],2)
    if p_value_Month < 0.05:
        remarks = 'The p value of the x variable (Month) is ' + str(p_value_Month)+'. Since p vlaue is < 0.05, we reject the null hypothesis that there is no significant relationship between month and crime counts.'
    else:
        remarks = 'The p value of the x variable (Month) is ' + str(p_value_Month)+'. Since p vlaue is > 0.05, we fail to reject the null hypothesis that there is no significant relationship between month and crime counts.'
    st.markdown(remarks)