from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/geo/1.0/direct', methods=['GET'])
def geocoding():
    city = request.args.get('q')
    if city.lower() == 'москва':
        return jsonify([{'lat': 55.7558, 'lon': 37.6173}])
    elif city.lower() == 'санкт-петербург':
        return jsonify([{'lat': 59.9343, 'lon': 30.3351}])
    elif city.lower() == 'нью-йорк':
        return jsonify([{'lat': 40.7128, 'lon': -74.0060}])
    elif city.lower() == 'лондон':
        return jsonify([{'lat': 51.5074, 'lon': -0.1278}])
    elif city.lower() == 'париж':
        return jsonify([{'lat': 48.8566, 'lon': 2.3522}])
    elif city.lower() == 'токио':
        return jsonify([{'lat': 35.6762, 'lon': 139.6503}])
    elif city.lower() == 'берлин':
        return jsonify([{'lat': 52.5200, 'lon': 13.4050}])
    elif city.lower() == 'мадрид':
        return jsonify([{'lat': 40.4168, 'lon': -3.7038}])
    elif city.lower() == 'рим':
        return jsonify([{'lat': 41.9028, 'lon': 12.4964}])
    else:
        return jsonify([]), 404


@app.route('/data/2.5/onecall', methods=['GET'])
def one_call():
    weather_data = {
        'daily': [
            {
                'temp': {'day': 20},
                'wind_speed': 5,
                'humidity': 60,
                'rain': 0
            },
            {
                'temp': {'day': 22},
                'wind_speed': 7,
                'humidity': 55,
                'rain': 0
            },
            {
                'temp': {'day': 19},
                'wind_speed': 4,
                'humidity': 65,
                'rain': 1
            },
            {
                'temp': {'day': 21},
                'wind_speed': 6,
                'humidity': 50,
                'rain': 0
            },
            {
                'temp': {'day': 23},
                'wind_speed': 8,
                'humidity': 45,
                'rain': 0
            },
            {
                'temp': {'day': 21},
                'wind_speed': 6,
                'humidity': 50,
                'rain': 0
            },
            {
                'temp': {'day': 19},
                'wind_speed': 4,
                'humidity': 65,
                'rain': 1
            },
        ]
    }

    return jsonify(weather_data)


if __name__ == '__main__':
    app.run(port=5001)