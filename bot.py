from aiogram import Bot, Dispatcher, types, F
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import constants

bot = Bot(token=constants.TG_API_KEY)
dp = Dispatcher()

user_data = {}


@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот для получения прогноза погоды.\n"
        "Вы можете использовать следующие команды:\n"
        "/help - получить справку по командам\n"
        "/weather - узнать погоду на маршруте между двумя городами."
    )


@dp.message(F.text == "/help")
async def help_handler(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - начать взаимодействие с ботом\n"
        "/help - получить справку по командам\n"
        "/weather - запросить прогноз погоды на маршруте между двумя городами.\n"
        "Следуйте инструкциям, чтобы получить нужную информацию."
    )


@dp.message(F.text == "/weather")
async def weather_handler(message: types.Message):
    user_data[message.from_user.id] = {"step": "city1"}
    await message.answer("Введите город отправления:")


@dp.message(lambda message: message.from_user.id in user_data)
async def handle_city_input(message: types.Message):
    user_id = message.from_user.id
    user_step = user_data[user_id]["step"]

    if user_step == "city1":
        user_data[user_id]["city1"] = message.text
        user_data[user_id]["step"] = "city2"
        await message.answer("Введите город назначения:")

    elif user_step == "city2":
        user_data[user_id]["city2"] = message.text
        user_data[user_id]["step"] = "choice"

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="Прогноз на 1 день", callback_data="1")
        keyboard_builder.button(text="Прогноз на 3 дня", callback_data="3")
        keyboard_builder.button(text="Прогноз на 5 дней", callback_data="5")
        keyboard_builder.button(text="Прогноз на 7 дней", callback_data="7")
        keyboard = keyboard_builder.as_markup()

        await message.answer("Выберите временной интервал прогноза:", reply_markup=keyboard)


@dp.callback_query(lambda callback_query: callback_query.data in ["1", "3", "5", "7"])
async def handle_city_choice(call: types.CallbackQuery):
    user_id = call.from_user.id
    duration = call.data

    city1 = user_data[user_id]["city1"]
    city2 = user_data[user_id]["city2"]

    async with aiohttp.ClientSession() as session:
        try:
            # Получение геоданных для первого города
            async with session.get(constants.GEOCODING_MOCK_URL + f'?q={city1}') as response:
                geo_info_city1 = await response.json()
                if not geo_info_city1:
                    await call.message.answer(f"Не удалось найти город '{city1}'.")
                    return

            # Получение геоданных для второго города
            async with session.get(constants.GEOCODING_MOCK_URL + f'?q={city2}') as response:
                geo_info_city2 = await response.json()
                if not geo_info_city2:
                    await call.message.answer(f"Не удалось найти город '{city2}'.")
                    return

            # Получение данных о погоде для первого города
            lat1, lon1 = geo_info_city1[0]['lat'], geo_info_city1[0]['lon']
            async with session.get(constants.OPEN_WEATHER_MOCK_URL + f'?lat={lat1}&lon={lon1}&days={duration}') as response:
                weather_info_city1 = await response.json()
                if 'daily' not in weather_info_city1:
                    await call.message.answer(f"Не удалось получить данные о погоде для города '{city1}'.")
                    return

            # Получение данных о погоде для второго города
            lat2, lon2 = geo_info_city2[0]['lat'], geo_info_city2[0]['lon']
            async with session.get(constants.OPEN_WEATHER_MOCK_URL + f'?lat={lat2}&lon={lon2}&days={duration}') as response:
                weather_info_city2 = await response.json()
                if 'daily' not in weather_info_city2:
                    await call.message.answer(f"Не удалось получить данные о погоде для города '{city2}'.")
                    return

            # Форматирование ответа для пользователя
            weather_text = f"Города: {city1} и {city2}\nПогода на {duration} дней:\n"

            for day_number in range(int(duration)):
                day_weather_1 = weather_info_city1['daily'][day_number]
                day_weather_2 = weather_info_city2['daily'][day_number]

                weather_text += (f"\n--- День {day_number + 1} ---\n"
                                 f"{city1}:\n"
                                 f"Температура: {day_weather_1['temp']['day']}°C\n"
                                 f"Скорость ветра: {day_weather_1['wind_speed']} м/с\n"
                                 f"Влажность: {day_weather_1['humidity']}%\n"
                                 f"Дождь: {day_weather_1.get('rain', 0)} мм\n\n"
                                 f"{city2}:\n"
                                 f"Температура: {day_weather_2['temp']['day']}°C\n"
                                 f"Скорость ветра: {day_weather_2['wind_speed']} м/с\n"
                                 f"Влажность: {day_weather_2['humidity']}%\n"
                                 f"Дождь: {day_weather_2.get('rain', 0)} мм\n")

            await call.message.answer(weather_text)

        except Exception as e:
            await call.message.answer(f"Произошла ошибка при получении данных: {str(e)}")

    user_data.pop(user_id)
    await call.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())