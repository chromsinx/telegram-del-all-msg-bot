import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import MessageToDeleteNotFound, BadRequest
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from config import API_TOKEN, ADMIN_CHAT_ID

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)  # Правильная инициализация диспетчера с передачей объекта бота

dp.middleware.setup(LoggingMiddleware())  # Подключаем middleware через setup()

# Обработчик команды /start
@dp.message_handler(commands=['start'])  # Используем правильный декоратор
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для удаления сообщений.")

# Функция для удаления одного сообщения с обработкой ошибок
async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
        logger.info(f"Сообщение {message_id} успешно удалено.")
    except MessageToDeleteNotFound:
        logger.error(f"Сообщение {message_id} уже не существует.")
    except BadRequest as e:
        logger.error(f"Ошибка при удалении сообщения {message_id}: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при удалении сообщения {message_id}: {e}")

# Основная функция для удаления нескольких сообщений
async def delete_messages(chat_id, message_ids):
    for message_id in message_ids:
        await delete_message(chat_id, message_id)
    # Отправляем сообщение администратору о завершении процесса
    await bot.send_message(ADMIN_CHAT_ID, "Удаление сообщений завершено.")

# Функция для проверки прав администратора
async def check_admin_rights(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]  # Правильная проверка статуса
    except Exception as e:
        logger.error(f"Ошибка при проверке прав администратора: {e}")
        return False

# Функция для получения списка сообщений и их удаления
@dp.message_handler(Text(equals="delete", ignore_case=True), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP, types.ChatType.CHANNEL])
async def handle_delete_command(message: types.Message):
    chat_id = message.chat.id
    message_ids = [msg_id for msg_id in range(message.message_id - 10, message.message_id)]  # пример списка ID

    # Проверяем, что бот является администратором
    if await check_admin_rights(chat_id, bot.id):
        logger.info(f"Бот является администратором в чате {chat_id}. Начинаем удаление сообщений.")
        await delete_messages(chat_id, message_ids)
    else:
        logger.warning(f"Бот не имеет прав администратора в чате {chat_id}.")
        await message.reply("У меня нет прав для удаления сообщений!")

# Глобальная обработка ошибок
@dp.errors_handler()  # Используем правильный декоратор для обработки ошибок
async def global_error_handler(update, exception):
    logger.error(f"Произошла ошибка: {exception}")
    return True  # Продолжаем работу, не прерываем выполнение

# Основная функция запуска
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
