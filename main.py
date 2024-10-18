import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)

# Инициализация диспетчера
dp = Dispatcher()

# Клавиатура с кнопкой "Старт"
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Нажми 'Старт', чтобы начать.", reply_markup=start_keyboard)

# Обработчик нажатия кнопки "Старт"
@dp.message(lambda message: message.text == "Старт")
async def handle_start_button(message: Message):
    await message.answer("Ты нажал на кнопку 'Старт'. Теперь можно выполнить команду /deleteAll.")

# Обработчик команды /deleteAll
@dp.message(Command("deleteAll"))
async def delete_all_messages(message: Message):
    try:
        reply_message = await message.answer("Начинаю удаление сообщений...")
        for message_id in range(reply_message.message_id, 0, -1):
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения {message_id}: {e}")
            await asyncio.sleep(config.DELETION_PAUSE / 1000.0)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка выполнения команды /deleteAll: {e}")

async def main():
    # Запуск polling с диспетчером и ботом
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
