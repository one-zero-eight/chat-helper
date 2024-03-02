import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types=['left_chat_member', 'new_chat_members'])
async def handle_left_member(message: types.Message):
    if message.new_chat_members and message.new_chat_members[0].id == bot.id:
        await message.reply(
            "Привет! Я бот, который помогает управлять уведомлениями о входе и выходе участников в чатах\n"
            "Пожалуйста, назначьте меня администратором, чтобы я мог удалять уведомления о входе и выходе участников.")
    try:
        await message.delete()
        logging.info(f"Message deleted: {message.message_id}")

    except MessageToDeleteNotFound:
        logging.warning(f"Message not found for deletion: {message.message_id}")
    except MessageCantBeDeleted:
        if (await bot.get_chat_member(message.chat.id, bot.id)).is_chat_admin():
            logging.warning(f"Message can't be deleted for unknown reason: {message.message_id}")
        else:
            logging.warning(f"Message can't because bot isn't admin: {message.message_id}")


if __name__ == '__main__':
    logging.info("Starting bot")
    executor.start_polling(dp, skip_updates=True)
