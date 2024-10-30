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
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="/help", callback_data="help")
    keyboard_builder.button(text="/weather", callback_data="weather")
    keyboard = keyboard_builder.as_markup()

    await message.answer(
        "Привет! Я бот для получения прогноза погоды.\n"
        "Вы можете использовать следующие команды:", reply_markup=keyboard
    )


@dp.callback_query(lambda call: call.data == "start")
async def start_callback(call: types.CallbackQuery):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="/help", callback_data="help")
    keyboard_builder.button(text="/weather", callback_data="weather")
    keyboard = keyboard_builder.as_markup()

    await call.message.answer(
        "Привет! Я бот для получения прогноза погоды.\n"
        "Вы можете использовать следующие команды:", reply_markup=keyboard
    )


@dp.message(F.text == "/help")
async def help_message(message: types.Message):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="/start", callback_data="start")
    keyboard_builder.button(text="/weather", callback_data="weather")
    keyboard = keyboard_builder.as_markup()

    await message.answer(
        "Доступные команды:\n"
        "/start - начать взаимодействие с ботом\n"
        "/help - получить справку по командам\n"
        "/weather - запросить прогноз погоды на маршруте между несколькими городами.",
        reply_markup=keyboard
    )


@dp.callback_query(lambda call: call.data == "help")
async def help_callback(call: types.CallbackQuery):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="/start", callback_data="start")
    keyboard_builder.button(text="/weather", callback_data="weather")
    keyboard = keyboard_builder.as_markup()

    await call.message.answer(
        "Доступные команды:\n"
        "/start - начать взаимодействие с ботом\n"
        "/help - получить справку по командам\n"
        "/weather - запросить прогноз погоды на маршруте между несколькими городами.",
        reply_markup=keyboard
    )
    await call.answer()  # Убираем уведомление о нажатии кнопки


@dp.callback_query(lambda call: call.data == "weather")
async def weather_callback(call: types.CallbackQuery):
    await call.message.answer("Введите город отправления:")
    user_data[call.from_user.id] = {"cities": [], "step": "city_input"}
    await call.answer()  # Убираем уведомление о нажатии кнопки


@dp.message(F.text == "/weather")
async def weather_handler(message: types.Message):
    user_data[message.from_user.id] = {"cities": [], "step": "city_input"}
    await message.answer("Введите город отправления:")


@dp.message(lambda message: message.from_user.id in user_data)
async def handle_city_input(message: types.Message):
    user_id = message.from_user.id
    user_step = user_data[user_id]["step"]

    if user_step == "city_input":
        city = message.text.strip()

        # Проверка на наличие города
        async with aiohttp.ClientSession() as session:
            async with session.get(constants.GEOCODING_MOCK_URL + f'?q={city}') as response:
                geo_info = await response.json()
                if not geo_info:
                    await message.answer(f"Не удалось найти город '{city}'. Пожалуйста, введите другой город:")
                    return

        # Добавление города в список
        user_data[user_id]["cities"].append(city)
        await message.answer(f"Город '{city}' добавлен.")

        # Создание клавиатуры с кнопкой "Готово"
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="Готово", callback_data="done")
        keyboard = keyboard_builder.as_markup()

        await message.answer("Введите следующий город (или нажмите 'Готово', чтобы завершить):", reply_markup=keyboard)


@dp.callback_query(lambda call: call.data == "done")
async def finish_city_input(call: types.CallbackQuery):
    user_id = call.from_user.id

    if not user_data[user_id]["cities"]:
        await call.message.answer("Вы не ввели ни одного города. Пожалуйста, введите хотя бы один город.")
        return

    user_data[user_id]["step"] = "choice"
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Прогноз на 1 день", callback_data="1")
    keyboard_builder.button(text="Прогноз на 3 дня", callback_data="3")
    keyboard_builder.button(text="Прогноз на 5 дней", callback_data="5")
    keyboard_builder.button(text="Прогноз на 7 дней", callback_data="7")
    keyboard = keyboard_builder.as_markup()

    await call.message.answer("Выберите временной интервал прогноза:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query(lambda callback_query: callback_query.data in ["1", "3", "5", "7"])
async def handle_weather_choice(call: types.CallbackQuery):
    user_id = call.from_user.id
    duration = call.data

    cities = user_data[user_id]["cities"]

    async with aiohttp.ClientSession() as session:
        try:
            weather_text = f"Города: {', '.join(cities)}\nПогода на {duration} дней:\n"

            for city in cities:
                # Получение геоданных для города
                async with session.get(constants.GEOCODING_MOCK_URL + f'?q={city}') as response:
                    geo_info = await response.json()
                    if not geo_info:
                        await call.message.answer(f"Не удалось найти город '{city}'.")
                        return

                # Получение данных о погоде для города
                lat, lon = geo_info[0]['lat'], geo_info[0]['lon']
                async with session.get(
                        constants.OPEN_WEATHER_MOCK_URL + f'?lat={lat}&lon={lon}&days={duration}') as response:
                    weather_info = await response.json()
                    if 'daily' not in weather_info:
                        await call.message.answer(f"Не удалось получить данные о погоде для города '{city}'.")
                        return

                # Форматирование данных о погоде
                for day_number in range(int(duration)):
                    day_weather = weather_info['daily'][day_number]
                    weather_text += (f"\n--- {city} ---\n"
                                     f"День {day_number + 1}:\n"
                                     f"Температура: {day_weather['temp']['day']}°C\n"
                                     f"Скорость ветра: {day_weather['wind_speed']} м/с\n"
                                     f"Влажность: {day_weather['humidity']}%\n"
                                     f"Дождь: {day_weather.get('rain', 0)} мм\n")

            await call.message.answer(weather_text)

        except Exception as e:
            await call.message.answer(f"Произошла ошибка при получении данных: {str(e)}")

    user_data.pop(user_id)
    await call.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
