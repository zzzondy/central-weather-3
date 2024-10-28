import unittest
from app import evaluate_weather


class EvaluateWeatherTests(unittest.TestCase):

    def test_no_data(self):
        """Тест для отсутствия данных о погоде"""
        result = evaluate_weather(None)
        self.assertEqual(result, "Нет данных о погоде")

    def test_missing_parameters(self):
        """Тест для отсутствующих необходимых параметров"""
        weather_data = {
            'main': {
                'temp': 25,
                'humidity': 50
            },
            'wind': {
                'speed': 10
            }
            # Отсутствуют другие параметры
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Ошибка: отсутствуют необходимые данные о погоде.")

    def test_bad_weather_conditions(self):
        """Тест для неблагоприятных погодных условий"""
        weather_data = {
            'main': {
                'temp': 40,  # Высокая температура
                'humidity': 50,
                'pressure': 1015
            },
            'wind': {
                'speed': 10
            },
            'rain': {
                '1h': 0.2  # Дождь
            }
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Ой-ой, погода плохая")

    def test_good_weather_conditions(self):
        """Тест для хороших погодных условий"""
        weather_data = {
            'main': {
                'temp': 20,
                'humidity': 40,
                'pressure': 1015
            },
            'wind': {
                'speed': 5
            },
            'rain': {
                '1h': 0.0  # Без дождя
            }
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Погода супер")


if __name__ == '__main__':
    unittest.main()
