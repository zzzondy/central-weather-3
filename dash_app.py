import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import constants

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Визуализация погодных данных"), className="text-center mb-4")
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Input(id='city-input', type='text', placeholder='Введите название города', className='form-control'),
            width=6),
        dbc.Col(
            html.Button('Добавить город', id='add-city-button', n_clicks=0, className='btn btn-secondary btn-block'),
            width=6),
    ]),
    html.Div(id='city-list', children=[], style={'margin-top': '20px'}),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='forecast-days',
            options=[
                {'label': 'Прогноз на 1 день', 'value': '1'},
                {'label': 'Прогноз на 3 дня', 'value': '3'},
                {'label': 'Прогноз на 5 дней', 'value': '5'},
                {'label': 'Прогноз на 7 дней', 'value': '7'},
            ],
            value='1',
            clearable=False,
            className='form-control'
        ), width=6),
        dbc.Col(html.Button('Получить погоду', id='submit-button', n_clicks=0, className='btn btn-primary btn-block'),
                width=6)
    ]),
    dbc.Row([
        html.H6('Выберите день для отображения информации на карте:', style={'margin-top': '20px'}),
        dbc.Col(dcc.Dropdown(
            id='day-selection',
            options=[{'label': 'День 1', 'value': 0}],
            value=0,
            clearable=False,
            className='form-control'
        ), width=6, style={'margin-top': '20px'}),
    ]),
    html.H2(id='travel-text', style={'margin-top': '20px', 'text-align': 'center'}),
    html.Div(id='cities-not-found', children=[], style={'margin-top': '20px', 'text-align': 'center',}),
    html.Div(id='graphs-container'),
    dl.Map(id='weather-map', style={'height': '50vh'}, center=[55.7558, 37.6173], zoom=6, children=[
        dl.TileLayer()
    ]),
    html.Div(id='output-container')
], fluid=True)

cities = []


@app.callback(
    Output('city-list', 'children'),
    Input('add-city-button', 'n_clicks'),
    State('city-input', 'value'),
)
def update_city_list(n_clicks_add, city_name):
    global cities
    if n_clicks_add > 0 and city_name:
        if city_name not in cities:
            cities.append(city_name)
        return [html.Div(city, className='alert alert-info') for city in cities]

    return [html.Div(city, className='alert alert-info') for city in cities]


@app.callback(
    Output('day-selection', 'options'),
    Input('forecast-days', 'value')
)
def update_day_selection(forecast_days):
    num_days = int(forecast_days)
    return [{'label': f'День {i + 1}', 'value': i} for i in range(num_days)]


@app.callback(
    Output('graphs-container', 'children'),
    Output('output-container', 'children'),
    Output('travel-text', 'children'),
    Output('weather-map', 'children'),
    Output('cities-not-found', 'children'),
    Input('submit-button', 'n_clicks'),
    Input('forecast-days', 'value'),
    Input('day-selection', 'value'),
    Input('add-city-button', 'n_clicks'),
)
def update_graph(n_clicks, forecast_days, selected_day, n_clicks_add):
    forecast_days = int(forecast_days)

    if n_clicks > 0:
        graphs = []
        messages = []
        markers = []
        cities_not_found = []
        cities_not_found_plain_text = []

        if not cities:
            return [], "Введите хотя бы один город.", "", []

        for city in cities:
            # Получение координат города
            response = requests.get(constants.GEOCODING_MOCK_URL, params={'q': city})
            location_data = response.json()

            if location_data:
                lat = location_data[0]['lat']
                lon = location_data[0]['lon']

                # Получение данных о погоде для города
                weather_response = requests.get(constants.OPEN_WEATHER_MOCK_URL,
                                                params={'lat': lat, 'lon': lon})
                weather_data = weather_response.json()

                # Создание графиков для каждого города
                temp_data = []
                wind_speed_data = []
                humidity_data = []
                rain_data = []

                for day in range(forecast_days):
                    temp_day = weather_data['daily'][day]['temp']['day']
                    wind_speed_day = weather_data['daily'][day]['wind_speed']
                    humidity_day = weather_data['daily'][day]['humidity']
                    rain_volume_day = weather_data['daily'][day].get('rain', 0)

                    temp_data.append(temp_day)
                    wind_speed_data.append(wind_speed_day)
                    humidity_data.append(humidity_day)
                    rain_data.append(rain_volume_day)

                # Создание графиков для температуры
                graphs.append(
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Scatter(x=[f'День {i + 1}' for i in range(forecast_days)], y=temp_data,
                                           mode='lines+markers', name=f'Температура ({city}) (°C)',
                                           hoverinfo='text',
                                           text=[f'День {i + 1}: {temp}°C' for i, temp in enumerate(temp_data)],
                                           line=dict(color='red'))  # Цвет графика температуры
                            ],
                            'layout': go.Layout(
                                title=f'Температура в {city}',
                                xaxis_title='Дни',
                                yaxis_title='Температура (°C)',
                                legend=dict(x=0.5, y=1.0)
                            )
                        }
                    )
                )

                # Создание графиков для скорости ветра
                graphs.append(
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Scatter(x=[f'День {i + 1}' for i in range(forecast_days)], y=wind_speed_data,
                                           mode='lines+markers', name=f'Скорость ветра ({city}) (км/ч)',
                                           hoverinfo='text',
                                           text=[f'День {i + 1}: {wind} км/ч' for i, wind in
                                                 enumerate(wind_speed_data)],
                                           line=dict(color='blue'))  # Цвет графика скорости ветра
                            ],
                            'layout': go.Layout(
                                title=f'Скорость ветра в {city}',
                                xaxis_title='Дни',
                                yaxis_title='Скорость ветра (км/ч)',
                                legend=dict(x=0.5, y=1.0)
                            )
                        }
                    )
                )

                # Создание графиков для влажности
                graphs.append(
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Scatter(x=[f'День {i + 1}' for i in range(forecast_days)], y=humidity_data,
                                           mode='lines+markers', name=f'Влажность ({city}) (%)',
                                           hoverinfo='text',
                                           text=[f'День {i + 1}: {humidity}%' for i, humidity in
                                                 enumerate(humidity_data)],
                                           line=dict(color='green'))  # Цвет графика влажности
                            ],
                            'layout': go.Layout(
                                title=f'Влажность в {city}',
                                xaxis_title='Дни',
                                yaxis_title='Влажность (%)',
                                legend=dict(x=0.5, y=1.0)
                            )
                        }
                    )
                )

                # Создание графиков для осадков
                graphs.append(
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Scatter(x=[f'День {i + 1}' for i in range(forecast_days)], y=rain_data,
                                           mode='lines+markers', name=f'Осадки ({city}) (мм)',
                                           hoverinfo='text',
                                           text=[f'День {i + 1}: {rain} мм' for i, rain in enumerate(rain_data)],
                                           line=dict(color='orange'))  # Цвет графика осадков
                            ],
                            'layout': go.Layout(
                                title=f'Осадки в {city}',
                                xaxis_title='Дни',
                                yaxis_title='Осадки (мм)',
                                legend=dict(x=0.5, y=1.0)
                            )
                        }
                    )
                )

                # Добавление маркера на карту с информацией о выбранном дне
                if selected_day < forecast_days:
                    markers.append(dl.Marker(position=(lat, lon), children=[
                        dl.Tooltip(f'{city}: Температура: {temp_data[selected_day]}°C\n'
                                   f'Скорость ветра: {wind_speed_data[selected_day]} км/ч\n'
                                   f'Влажность: {humidity_data[selected_day]}%\n'
                                   f'Осадки: {rain_data[selected_day]} мм\n'
                                   f'День: {selected_day + 1}')
                    ]))

            else:
                cities_not_found.append(
                    html.H6(f"Город {city} не найден", style={'margin-top': '20px', 'text-align': 'center'})
                )
                cities_not_found_plain_text.append(city)

        travel_text_content = f"Путешествие через: {', '.join(filter_cities(cities, cities_not_found_plain_text))}" if cities else ""

        return graphs, "<br>".join(messages), travel_text_content, [dl.TileLayer()] + markers, cities_not_found

    return [], "", "", [], []


def filter_cities(cities, correct_cities):
    return [city for city in cities if city not in correct_cities]


if __name__ == '__main__':
    app.run_server(debug=True)
