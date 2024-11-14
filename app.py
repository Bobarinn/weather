from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
API_KEY = 'c06a804573909e9420ac69cb7136c477'

def get_recommendation(weather_condition):
    if 'clear' in weather_condition:
        return "It's sunny today, a great day for a picnic!"
    elif 'clouds' in weather_condition:
        return "It's cloudy. How about visiting a cozy café?"
    elif 'rain' in weather_condition:
        return "It's going to rain. Don’t forget an umbrella!"
    elif 'snow' in weather_condition:
        return "Snowy weather! Perfect for building a snowman!"
    elif 'storm' in weather_condition:
        return "Stormy weather. Better to stay indoors."
    else:
        return "Weather's a bit unpredictable today, dress accordingly!"

@app.route('/', methods=['GET', 'POST'])
def index():
    city = request.form.get('city', 'Lagos')  # Default to Lagos if no city is provided
    weather_data = None
    recommendation = None
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp

    # Fetch weather data
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            'city': city,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
        }
        recommendation = get_recommendation(data['weather'][0]['description'].lower())
    else:
        weather_data = {'error': 'City not found. Please enter a valid city name.'}

    return render_template('index.html', weather=weather_data, recommendation=recommendation, timestamp=timestamp)

if __name__ == '__main__':
    app.run(debug=True)
