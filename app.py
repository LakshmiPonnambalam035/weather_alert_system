from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Define constants (you should have these defined somewhere in your code)
API_KEY = '89a622addbbfc57dcfd9b829f5467b74'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# In-memory storage for alerts (replace with a database for persistence)
user_alerts = {}

# Route to render setup_alert.html
@app.route('/')
def index():
    return 'Welcome to Weather Alert System'

@app.route('/current_alerts/<user_id>')
def current_alerts(user_id):
    if user_id not in user_alerts:
        return 'No alerts set up for this user.'

    alert = user_alerts[user_id]
    response = requests.get(BASE_URL, params={
        'q': alert['city'],
        'appid': API_KEY
    })

    if response.status_code != 200:
        return f'Error fetching weather data: {response.status_code}'

    try:
        data = response.json()

        # Check if 'weather' key exists in the API response
        if 'weather' not in data or not data['weather']:
            return 'Weather data not available for this city.'

        weather_condition = data['weather'][0]['main']
        temp = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius

        # Check if the current conditions match the alert criteria
        alert_triggered = False
        if alert['condition'] == 'temperature' and temp >= float(alert['threshold']):
            alert_triggered = True
        elif alert['condition'].lower() == weather_condition.lower():
            alert_triggered = True

        return render_template('current_alerts.html', alert=alert, alert_triggered=alert_triggered, weather=data)

    except KeyError as e:
        return f'KeyError: {str(e)}'

    except Exception as e:
        return f'Error: {str(e)}'


# Route to render setup_alerts.html
@app.route('/setup_alert', methods=['GET', 'POST'])
def setup_alert():
    if request.method == 'GET':
        # Handle GET request logic (render setup_alert.html template)
        return render_template('setup_alert.html')
    
    elif request.method == 'POST':
        # Handle POST request logic (process form submission)
        # Example: Store alert data in user_alerts dictionary
        user_id = request.form['user_id']
        city = request.form['city']
        condition = request.form['condition']
        threshold = request.form['threshold']

        user_alerts[user_id] = {
            'city': city,
            'condition': condition,
            'threshold': threshold
        }

        return 'Alert set up successfully!'


if __name__ == '__main__':
    app.run(debug=True)
