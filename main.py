import asyncio
import logging
import sys
import aiohttp
from aiogram import Bot, Dispatcher, html, types, F
from aiogram.client import bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

TOKEN = "7776430508:AAFrx_63g1wJjM9hiyXqxM90KCX1E81heyA"
dp = Dispatcher()

IP = "127.0.0.1:8000"



async def send_event_by_api(title, text, image):
    url = "http://localhost:8000/api-app/create-new/"
    event_data = {
        "title": title,
        "text": text,
        "image_telegram": image
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=event_data) as response:
            if response.status in (200, 201):
                print("Новость успешно отправлена в API")
                result = await response.json()

                return result
            else:
                print(f"Ошибка при отправке новости в API: {response.status}")
                error_message = await response.text()


kb_btn = {"send_news": "Опубликовать новость", "get_chat_id": "Получить ID чата"}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [types.KeyboardButton(text=kb_btn["send_news"])],
        [types.KeyboardButton(text=kb_btn["get_chat_id"])],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    # print(f"{message.chat.id}!!!!!!!!!!!!")

    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=keyboard)


class NewsState(StatesGroup):
    title = State()
    text = State()
    image = State()


@dp.message(F.text == kb_btn["get_chat_id"])
async def create_event(message: Message):
    await message.answer(f"Ваш chat_id={message.chat.id}")


@dp.message(F.text == kb_btn["send_news"])
async def create_event(message: Message, state: FSMContext):
    await state.set_state(NewsState.title)  # пользователь находится в этом состоянии
    await message.answer("Введите заголовок")


@dp.message(NewsState.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewsState.text)
    await message.answer("Введите текст")


@dp.message(NewsState.text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(NewsState.image)
    await message.answer("Отправьте изображение")


@dp.message(NewsState.image, F.photo)
async def get_text(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id  # Получаем file_id изображения

    # Получаем путь к файлу через метод get_file
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

    await state.update_data(image_url=file_url)
    data = await state.get_data()

    await message.answer(f"Новость '{data['title']}' опубликована.")

    res = await send_event_by_api(data['title'], data['text'], data['image_url'])

    await message.answer(f"{IP}/admin/api_app/news/{res.get('id')}/change/")
    await state.clear()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
