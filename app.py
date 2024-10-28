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

    start_coordinates = get_coordinates(start_city)
    end_coordinates = get_coordinates(end_city)

    if start_coordinates.data is None:
        return render_template(templates_paths.ERROR, message=start_coordinates.message)

    if end_coordinates.data is None:
        return render_template(templates_paths.ERROR, message=end_coordinates.message)

    weather_start = get_weather(start_coordinates.data)
    weather_end = get_weather(end_coordinates.data)

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


def get_coordinates(city) -> Result:
    try:
        response = requests.get(constants.GEOCODING_URL,
                                params={'q': city, 'appid': constants.API_KEY})
        response.raise_for_status()
        data = response.json()

        if response.status_code == 200 and data:
            coordinates = (data[0]['lat'], data[0]['lon'])
            return Result(coordinates, None)
        else:
            return Result(None, f"Упс. Город {city} не найден")

    except requests.exceptions.HTTPError:
        return Result(None, "Ошибка подключения к серверу. Пожалуйста, попробуйте позже.")
    except requests.exceptions.RequestException as e:
        return Result(None, "Ошибка подключения к серверу. Проверьте ваше интернет-соединение.")
    except Exception as ex:
        return Result(None, f"Не удалось получить координаты: {ex}")


def get_weather(coordinates) -> Result:
    lat, lon = coordinates
    try:
        response = requests.get(constants.OPEN_WEATHER_URL,
                                params={'lat': lat, 'lon': lon, 'appid': constants.API_KEY, 'units': 'metric',
                                        'lang': 'ru'})
        response.raise_for_status()
        return Result(response.json(), None)

    except requests.exceptions.HTTPError:
        return Result(None, "Ошибка подключения к серверу. Пожалуйста, попробуйте позже.")
    except requests.exceptions.RequestException as e:
        return Result(None, "Ошибка подключения к серверу. Проверьте ваше интернет-соединение.")
    except Exception as ex:
        return Result(None, f"Не удалось получить данные о погоде: {ex}")


def evaluate_weather(weather_data):
    if not weather_data:
        return "Нет данных о погоде"

    temperature = weather_data.get('main', {}).get('temp', None)
    wind_speed = weather_data.get('wind', {}).get('speed', None)
    precipitation = weather_data.get('rain', {}).get('1h', 0)  # Объём дождя за последний час
    humidity = weather_data.get('main', {}).get('humidity', None)
    pressure = weather_data.get('main', {}).get('pressure', None)

    if (temperature is None or wind_speed is None or
            precipitation is None or humidity is None or pressure is None):
        return "Ошибка: отсутствуют необходимые данные о погоде."

    if (temperature < 0 or temperature > 35 or
            wind_speed > 50 or
            precipitation > 0.1 or
            humidity > 80 or
            pressure < 1000):
        return "Ой-ой, погода плохая"

    return "Погода супер"


if __name__ == '__main__':
    app.run(debug=True)