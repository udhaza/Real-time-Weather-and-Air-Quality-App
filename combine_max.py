import requests
import time
from datetime import datetime, timedelta
import streamlit as st

TOMORROW_API_KEY = "q2dAvzwcyQgGkvHImEEUigS2I7oLr0RC"
WEATHERBIT_API_KEY = "077acd0592bb4f3aae5179ecf99b6111"
LOCATION = "Chennai"

def fetch_tomorrow_weather(api_key, location):
    url = f"https://api.tomorrow.io/v4/timelines?location={location}&fields=temperature,weatherCode,precipitationProbability,windSpeed&units=metric&timesteps=current&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data from Tomorrow.io: {e}")
        return None

def fetch_weatherbit_data(api_key, city, start_date, end_date):
    historical_url = f"https://api.weatherbit.io/v2.0/history/hourly?city={city}&start_date={start_date}&end_date={end_date}&key={api_key}"
    try:
        response = requests.get(historical_url)
        response.raise_for_status()  
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical weather data from Weatherbit: {e}")
        return []

def fetch_current_air_quality(api_key, city):
    url = f"https://api.weatherbit.io/v2.0/current/airquality?city={city}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        return data['data'][0]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching current air quality data from Weatherbit: {e}")
        return {}

def plot_weather(historical_data, tomorrow_data):
    if historical_data:
        
        historical_temperatures = [entry['temp'] for entry in historical_data]
        historical_timestamps = [entry['timestamp_local'] for entry in historical_data]

        st.subheader('Historical Temperature Data ')
        st.line_chart(historical_temperatures, use_container_width=True)

        
        historical_humidities = [entry['rh'] for entry in historical_data]

        st.subheader('Historical Humidity Data ')
        st.line_chart(historical_humidities, use_container_width=True)

    if tomorrow_data:
        current_weather = tomorrow_data["data"]["timelines"][0]["intervals"][0]["values"]
        temperature = current_weather["temperature"]
        weather_code = current_weather["weatherCode"]
        precipitation_probability = current_weather["precipitationProbability"]
        wind_speed = current_weather["windSpeed"]

        st.subheader("Current Weather (Tomorrow.io)")
        st.write(f"Temperature: {temperature}°C")
        st.write(f"Weather Code: {weather_code}")
        st.write(f"Precipitation Probability: {precipitation_probability}%")
        st.write(f"Wind Speed: {wind_speed} m/s")
    else:
        st.error("No weather data available from Tomorrow.io.")

def main():
    st.title("Real-time Weather and Air Quality App")
    
    
    tomorrow_weather_data = fetch_tomorrow_weather(TOMORROW_API_KEY, LOCATION)
    end_date = datetime.utcnow().strftime('%Y-%m-%d')  
    start_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')  
    historical_weather_data = fetch_weatherbit_data(WEATHERBIT_API_KEY, LOCATION, start_date, end_date)

    
    plot_weather(historical_weather_data, tomorrow_weather_data)

    st.title('Real-time Weather Data Graph')
    
    temperature_values = []
    timestamps = []

    chart = st.line_chart(temperature_values)
    temperature_text = st.empty()  

    while True:
        url = f"https://api.weatherbit.io/v2.0/current?city={LOCATION}&key={WEATHERBIT_API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            temperature = data['data'][0]['temp']
            timestamp = time.strftime('%H:%M:%S')

            temperature_values.append(temperature)
            timestamps.append(timestamp)

            chart.line_chart(temperature_values)  
            temperature_text.text(f"Temperature: {temperature} °C")  

        else:
            st.error("Failed to fetch weather data.")

        air_quality_data = fetch_current_air_quality(WEATHERBIT_API_KEY, LOCATION)
        if air_quality_data:
            aqi = air_quality_data.get('aqi')
            st.subheader("Current Air Quality (Weatherbit)")
            st.write(f"AQI (Air Quality Index): {aqi}")
        else:
            st.error("No air quality data available.")

        time.sleep(10) 

if __name__ == "__main__":
    main()
