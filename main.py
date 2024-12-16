import asyncio
import logging
import sys
import aiohttp
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "7776430508:AAFrx_63g1wJjM9hiyXqxM90KCX1E81heyA"
dp = Dispatcher()


async def send_event_by_api(name, date, time, place, description):
    url = "http://localhost:8000/api-app/create-event/"
    event_data = {
        "name": name,
        "date": date,
        "time": time,
        "place": place,
        "description": description
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=event_data) as response:
            if response.status in (200, 201):
                print("Новость успешно отправлена в API")
                result = await response.json()
            else:
                print(f"Ошибка при отправке новости в API: {response.status}")
                error_message = await response.text()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [types.InlineKeyboardButton(text="Создать мероприятие", callback_data='create_event')],
        [types.InlineKeyboardButton(text="Опубликовать новость", callback_data='create_new')],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=keyboard)


class EventState(StatesGroup):
    name = State()
    date = State()
    time = State()
    place = State()
    description = State()


@dp.callback_query(F.data == "create_event")
async def about_me_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Напишите название мероприятия")
    await state.set_state(EventState.name)

    # await send_event_by_api(name, date, time, place, description)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
