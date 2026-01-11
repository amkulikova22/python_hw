import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pickle

st.title('Weather info')
file = st.file_uploader("Upload a file", type='csv')

if file is not None:
    df = pd.read_csv(file)
    st.dataframe(df)

st.title("Выберите город")

city = st.selectbox(
    "Выберите город:",
    ['New York', 'Tokyo', 'Singapore', 'Mexico City', 'Dubai', 'Berlin',
       'Mumbai', 'Moscow', 'Sydney', 'London', 'Cairo', 'Beijing',
       'Rio de Janeiro', 'Paris', 'Los Angeles']
)

api_key = st.text_input(
    "Введите API-ключ OpenWeatherMap:",
    type="password",
    placeholder="ваш_api_ключ_здесь")

if st.button("Проверить ключ"):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'q': 'London', 'appid': api_key}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get('cod') == 401:
        st.error("Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.")
    elif response.status_code == 200:
        st.success("Ключ работает!")


if file is not None and 'city' in df.columns:
    city_df = df[df['city'] == city]
    city_df = city_df.drop(columns=['Unnamed: 0'])

    if not city_df.empty:
        st.subheader(f"Анализ для {city}")
        st.write(f"**Записей:** {len(city_df)}")
        
        st.write("**Полная статистика:**")
        st.dataframe(city_df.describe(include='all'))


if file is not None and 'timestamp' in df.columns and 'temperature' in df.columns:
    city_df = df[df['city'] == city]
    city_df = city_df.sort_values('timestamp')
    
    if not city_df.empty:
        city_df['avg_temp'] = city_df.groupby(['city', 'season'])['temperature'].transform('mean')
        city_df['temp_std'] = city_df.groupby(['city', 'season'])['temperature'].transform('std')
        city_df['upper_bound'] = city_df['avg_temp'] + 2 * city_df['temp_std']
        city_df['lower_bound'] = city_df['avg_temp'] - 2 * city_df['temp_std']
        city_df['is_anomaly'] = (city_df['temperature'] > city_df['upper_bound']) | (city_df['temperature'] < city_df['lower_bound'])
    
    fig, ax = plt.subplots()
    ax.plot(city_df['timestamp'], city_df['temperature'])
    
    extremes = city_df[city_df['is_anomaly'] == True]
    ax.scatter(extremes['timestamp'], extremes['temperature'], color='red', s=50)
    
    st.pyplot(fig)

    season_stats = city_df.groupby('season')['temperature'].agg(['mean', 'std', 'count']).reset_index()
    st.dataframe(season_stats)

def get_temperature(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        temp = data['main']['temp']
        print(f"Температура в {city}: {temp}°C")
        return temp
    else:
        print(f"Ошибка: {data.get('message', 'Неизвестная ошибка')}")
        return None

if api_key and st.button("Получить текущую погоду"):
    temp = get_temperature(city, api_key)
    
    if temp is not None:
        st.write(f"### Температура в {city}: {temp}°C")
    else:
        st.error("Не удалось получить данные о погоде")