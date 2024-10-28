import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import requests
import dash_bootstrap_components as dbc

# Создание экземпляра приложения Dash с использованием Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# API-ключ и URL для OpenWeatherMap
API_KEY = '68c4ca0a645546bec6731515ecf4677a'
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# Макет приложения с использованием компонентов Bootstrap
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Визуализация погодных данных"), className="text-center mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Input(id='city1-input', type='text', placeholder='Введите название первого города',
                          className='form-control'), width=6),
        dbc.Col(dcc.Input(id='city2-input', type='text', placeholder='Введите название второго города',
                          className='form-control'), width=6),
    ]),
    dbc.Row([
        dbc.Col(html.Button('Получить погоду', id='submit-button', n_clicks=0, className='btn btn-primary btn-block'),
                width=12, style={'margin-top': '20px'})
    ]),
    html.H2(id='travel-text', style={'margin-top': '20px', 'text-align': 'center'}),
    dcc.Graph(id='weather-graph'),
    html.Div(id='output-container')
], fluid=True)


@app.callback(
    Output('weather-graph', 'figure'),
    Output('output-container', 'children'),
    Output('travel-text', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('city1-input', 'value'),
    Input('city2-input', 'value')
)
def update_graph(n_clicks, city1, city2):
    if n_clicks > 0:
        figure_data = []
        messages = []

        # Проверка на ввод городов
        if city1:
            # Получение координат первого города
            response = requests.get(GEOCODING_URL, params={'q': city1, 'appid': API_KEY})
            location_data = response.json()

            if location_data:
                lat1 = location_data[0]['lat']
                lon1 = location_data[0]['lon']

                # Получение данных о погоде для первого города
                weather_response = requests.get(WEATHER_URL,
                                                params={'lat': lat1, 'lon': lon1, 'appid': API_KEY, 'units': 'metric'})
                weather_data1 = weather_response.json()

                # Извлечение данных о погоде для первого города
                temperature1 = weather_data1['main']['temp']
                wind_speed1 = weather_data1['wind']['speed']
                humidity1 = weather_data1['main']['humidity']
                rain_volume1 = weather_data1.get('rain', {}).get('1h', 0)

                messages.append(f"Данные о погоде для {city1} успешно получены.")
            else:
                messages.append(f"Город {city1} не найден.")
                temperature1 = wind_speed1 = humidity1 = rain_volume1 = None
        else:
            messages.append("Введите название первого города.")
            temperature1 = wind_speed1 = humidity1 = rain_volume1 = None

        if city2:
            # Получение координат второго города
            response = requests.get(GEOCODING_URL, params={'q': city2, 'appid': API_KEY})
            location_data = response.json()

            if location_data:
                lat2 = location_data[0]['lat']
                lon2 = location_data[0]['lon']

                # Получение данных о погоде для второго города
                weather_response = requests.get(WEATHER_URL,
                                                params={'lat': lat2, 'lon': lon2, 'appid': API_KEY, 'units': 'metric'})
                weather_data2 = weather_response.json()

                # Извлечение данных о погоде для второго города
                temperature2 = weather_data2['main']['temp']
                wind_speed2 = weather_data2['wind']['speed']
                humidity2 = weather_data2['main']['humidity']
                rain_volume2 = weather_data2.get('rain', {}).get('1h', 0)

                messages.append(f"Данные о погоде для {city2} успешно получены.")
            else:
                messages.append(f"Город {city2} не найден.")
                temperature2 = wind_speed2 = humidity2 = rain_volume2 = None
        else:
            messages.append("Введите название второго города.")
            temperature2 = wind_speed2 = humidity2 = rain_volume2 = None

        # Добавление данных для графика
        if temperature1 is not None and temperature2 is not None:
            figure_data.append(go.Scatter(x=[city1, city2], y=[temperature1, temperature2], mode='lines+markers',
                                          name='Температура (°C)'))
        if wind_speed1 is not None and wind_speed2 is not None:
            figure_data.append(go.Scatter(x=[city1, city2], y=[wind_speed1, wind_speed2], mode='lines+markers',
                                          name='Скорость ветра (км/ч)'))
        if humidity1 is not None and humidity2 is not None:
            figure_data.append(
                go.Scatter(x=[city1, city2], y=[humidity1, humidity2], mode='lines+markers', name='Влажность (%)'))
        if rain_volume1 is not None and rain_volume2 is not None:
            figure_data.append(
                go.Scatter(x=[city1, city2], y=[rain_volume1, rain_volume2], mode='lines+markers', name='Осадки (мм)'))

        # Построение графиков
        figure = {
            'data': figure_data,
            'layout': go.Layout(
                title='Погодные данные',
                xaxis_title='Города',
                yaxis_title='Значения',
                legend=dict(x=0.5, y=1.0)
            )
        }

        travel_text_content = f"Путешествие из {city1} в {city2}" if city1 and city2 else ""

        return figure, " ".join(messages), travel_text_content

    return {}, "", ""


if __name__ == '__main__':
    app.run_server(debug=True)