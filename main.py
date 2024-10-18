import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatType
from aiogram.filters import Command
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)

# Инициализация диспетчера
dp = Dispatcher()

# Клавиатура с кнопками "Старт" и "Выбрать источник"
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")],
        [KeyboardButton(text="Выбрать источник")]
    ],
    resize_keyboard=True
)

# Клавиатура для выбора источника удаления
source_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Удалять отсюда")],  # Изменение текста кнопки
        [KeyboardButton(text="Удалять из группы")]
    ],
    resize_keyboard=True
)

# Переменная для хранения выбранного источника
user_source_choice = {}

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Нажми 'Старт', чтобы начать или выбери источник для удаления сообщений.",
        reply_markup=start_keyboard
    )

# Обработчик нажатия кнопки "Старт"
@dp.message(lambda message: message.text == "Старт")
async def handle_start_button(message: Message):
    await message.answer("Ты нажал на кнопку 'Старт'. Теперь можно выполнить команду /deleteAll.")

# Обработчик нажатия кнопки "Выбрать источник"
@dp.message(lambda message: message.text == "Выбрать источник")
async def handle_source_button(message: Message):
    await message.answer("Выбери источник для удаления сообщений:", reply_markup=source_keyboard)

# Обработчик выбора источника удаления
@dp.message(lambda message: message.text in ["Удалять отсюда", "Удалять из группы"])
async def handle_source_choice(message: Message):
    if message.text == "Удалять отсюда":
        choice = message.chat.type
    else:
        choice = "group"
    user_source_choice[message.from_user.id] = choice
    await message.answer(f"Источник установлен: {message.text}. Теперь можно выполнить команду /deleteAll.")

# Обработчик команды /deleteAll
@dp.message(Command("deleteAll"))
async def delete_all_messages(message: Message):
    source = user_source_choice.get(message.from_user.id)

    if not source:
        await message.answer("Сначала выбери источник для удаления сообщений.")
        return

    chat_type = message.chat.type
    # Проверка соответствия источника и типа чата
    if (source == ChatType.PRIVATE and chat_type != ChatType.PRIVATE) or \
       (source == "group" and chat_type not in {ChatType.GROUP, ChatType.SUPERGROUP}) or \
       (source == ChatType.CHANNEL and chat_type != ChatType.CHANNEL):
        await message.answer("Команда должна быть вызвана в соответствующем чате.")
        return

    await message.answer(f"Удаляю сообщения из: {source}")

    try:
        reply_message = await message.answer("Начинаю удаление сообщений...")
        deleted_count = 0  # Счетчик удаленных сообщений

        for message_id in range(reply_message.message_id, 0, -1):
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
                deleted_count += 1  # Увеличиваем счетчик при успешном удалении
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения {message_id}: {e}")
            await asyncio.sleep(config.DELETION_PAUSE / 1000.0)

        await message.answer(f"Удаление завершено. Удалено сообщений: {deleted_count}.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка выполнения команды /deleteAll: {e}")

async def main():
    # Запуск polling с диспетчером и ботом
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
