from flask import Flask, render_template, request, send_file
import requests
from datetime import datetime
import yt_dlp  # Replace pytube import with this
from pydub import AudioSegment
import os
import tempfile
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
API_KEY = 'c06a804573909e9420ac69cb7136c477'

def get_recommendation(weather_condition):
    if 'clear' in weather_condition:
        return "It's sunny today, a great day for a picnic!"
    elif 'clouds' in weather_condition:
        return "It's cloudy. How about visiting a cozy café?"
    elif 'rain' in weather_condition:
        return "It's going to rain. Don't forget an umbrella!"
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

def get_video_id(url):
    # Extract video ID from URL
    video_id = None
    if 'youtube.com' in url:
        video_id = re.search(r'v=([^&]*)', url).group(1)
    elif 'youtu.be' in url:
        video_id = url.split('/')[-1]
    return video_id

@app.route('/convert-audio', methods=['POST'])
def convert_audio():
    try:
        youtube_url = request.json.get('url')
        if not youtube_url:
            return {'error': 'No URL provided'}, 400

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'restrictfilenames': True  # This prevents special characters in filenames
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                title = info['title']
                # Create safe filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_path = os.path.join(temp_dir, f"{safe_title}.mp3")
                
                if not os.path.exists(output_path):
                    # Try to find the file with similar name
                    files = os.listdir(temp_dir)
                    mp3_files = [f for f in files if f.endswith('.mp3')]
                    if mp3_files:
                        output_path = os.path.join(temp_dir, mp3_files[0])
                
                print(f"File path: {output_path}")  # Debug print
                
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=f"{safe_title}.mp3",
                    mimetype="audio/mpeg"
                )

    except Exception as e:
        print(f"Error details: {str(e)}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
