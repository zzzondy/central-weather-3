import unittest
from app import evaluate_weather  # Импортируйте вашу функцию


class EvaluateWeatherTests(unittest.TestCase):

    def test_no_data(self):
        """Тест для отсутствия данных о погоде"""
        result = evaluate_weather(None)
        self.assertEqual(result, "Нет данных о погоде")

    def test_missing_parameters(self):
        """Тест для отсутствующих необходимых параметров"""
        weather_data = {
            'Temperature': {'Metric': {'Value': 25}},
            'Wind': {'Speed': {'Metric': {'Value': 10}}},
            # Отсутствуют другие параметры
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Ошибка: отсутствуют необходимые данные о погоде.")

    def test_bad_weather_conditions(self):
        """Тест для неблагоприятных погодных условий"""
        weather_data = {
            'Temperature': {'Metric': {'Value': 40}},  # Высокая температура
            'Wind': {'Speed': {'Metric': {'Value': 10}}},
            'PrecipitationSummary': {'Precipitation': {'Metric': {'Value': 0.2}}},  # Дождь
            'RelativeHumidity': 50,
            'Pressure': {'Metric': {'Value': 1015}},
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Ой-ой, погода плохая")

    def test_good_weather_conditions(self):
        """Тест для хороших погодных условий"""
        weather_data = {
            'Temperature': {'Metric': {'Value': 20}},
            'Wind': {'Speed': {'Metric': {'Value': 5}}},
            'PrecipitationSummary': {'Precipitation': {'Metric': {'Value': 0.0}}},  # Без дождя
            'RelativeHumidity': 40,
            'Pressure': {'Metric': {'Value': 1015}},
        }
        result = evaluate_weather(weather_data)
        self.assertEqual(result, "Погода супер")


if __name__ == '__main__':
    unittest.main()
