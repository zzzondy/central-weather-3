from flask import Flask, render_template, request
import constants
import templates_paths
import requests
from result import Result

app = Flask(__name__)


@app.route('/')
def index():
    return render_template(templates_paths.INDEX)


@app.route('/weather', methods=['POST'])
def weather():
    start_city = request.form['start']
    end_city = request.form['end']

    start_location_key = get_location_key(start_city)
    end_location_key = get_location_key(end_city)

    if start_location_key.message is not None:
        return render_template(templates_paths.ERROR, message=start_location_key.message)

    if end_location_key.message is not None:
        return render_template(templates_paths.ERROR, message=end_location_key.message)

    weather_start = get_weather(start_location_key.data)
    weather_end = get_weather(end_location_key.data)

    if weather_start.data is None:
        return render_template(templates_paths.ERROR, message=weather_start.message)

    if weather_end.data is None:
        return render_template(templates_paths.ERROR, message=weather_end.message)

    result_start = evaluate_weather(weather_start.data)
    result_end = evaluate_weather(weather_end.data)

    return render_template(
        templates_paths.RESULTS,
        start=start_city,
        end=end_city,
        result_start=result_start,
        result_end=result_end,
        weather_start=weather_start.data,
        weather_end=weather_end.data
    )


def get_location_key(city) -> Result:
    try:
        response = requests.get(constants.LOCATION_URL, params={'apikey': constants.API_KEY, 'q': city})
        response.raise_for_status()
        data = response.json()
        if data:
            return Result(data[0]["Key"], None)
        else:
            return Result(None, f"Упс. Город {city} не найден")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return Result(None, f"Произошла ошибка, попробуйте позже")
    except Exception as e:
        print(f"Ошибка получения координат: {e}")
        return Result(None, f"Произошла непредвиденная ошибка")


def get_weather(location_key) -> Result:
    try:
        response = requests.get(constants.CURRENT_CONDITIONS_URL + location_key, params={'apikey': constants.API_KEY})
        response.raise_for_status()
        return Result(response.json()[0], None)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return Result(None, "Ошибка подключения к серверу. Пожалуйста, попробуйте позже.")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return Result(None, "Ошибка подключения к серверу. Проверьте ваше интернет-соединение.")
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return Result(None, "Не удалось получить данные о погоде.")


def evaluate_weather(weather_data):
    if not weather_data:
        return "Нет данных о погоде"

    temperature = weather_data.get('Temperature', {}).get('Metric', {}).get('Value', None)
    wind_speed = weather_data.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', None)
    precipitation_probability = weather_data.get('PrecipitationProbability', None)
    humidity = weather_data.get('RelativeHumidity', None)
    pressure = weather_data.get('Pressure', {}).get('Metric', {}).get('Value', None)

    if (temperature is None or wind_speed is None or
            precipitation_probability is None or humidity is None or pressure is None):
        return "Ошибка: отсутствуют необходимые данные о погоде."

    if (temperature < 0 or temperature > 35 or
            wind_speed > 50 or
            precipitation_probability > 70 or
            humidity > 80 or
            pressure < 1000):
        return "Ой-ой, погода плохая"

    return "Погода супер"


if __name__ == '__main__':
    app.run(debug=True)
