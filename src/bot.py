import asyncio
import logging
import os
import re
from io import BytesIO

from PIL.JpegPresets import presets
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.formatting import Text

from src.avatar import generate_avatar
from src.color import pick_stable_random
from src.parse_chat_name import get_course_name, get_semester

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
image_generation_text = """Для генерации персонализированной аватарки отправьте сообщение:
<pre><code>\
/set_image
<i>Заголовок</i>
<i>Подзаголовок (опционально)</i>
<i>Цвет в формате hex (опционально)</i>\
</code></pre>"""


async def on_startup():
    logging.info("Bot is starting up...")
    await bot.delete_webhook(drop_pending_updates=True)


class SetPhotoCallbackData(CallbackData, prefix="set_photo"):
    pass


class DeleteCallbackData(CallbackData, prefix="delete"):
    pass


def _get_avatar_bytes(title: str, subtitle: str | None, color: tuple[int, int, int]) -> bytes:
    picture = generate_avatar(title, subtitle, color)
    bio = BytesIO()
    picture.save(bio, "jpeg", quality=95, **presets["maximum"])
    bio.seek(0)
    return bio.read()


@dp.message(Command("set_image"))
async def handle_set_image(message: types.Message, command: CommandObject):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id == message.from_user.id and not command.args:
        await message.answer(image_generation_text, reply_to_message_id=message.message_id, parse_mode="HTML")
        return
    if (message.chat.id == message.from_user.id or
            chat_member.status == ChatMemberStatus.ADMINISTRATOR or chat_member.status == ChatMemberStatus.CREATOR):
        if command.args and len(command.args.splitlines()):
            splitted = command.args.splitlines()
            title, subtitle, color, *_ = (splitted + [None, None, None])[:3]
        else:
            title, subtitle, color = get_course_name(message.chat.full_name), get_semester(
                message.chat.full_name), None

        if color is not None:
            color = color.lstrip("#")
            rgb = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        else:
            rgb = pick_stable_random(title)
        caption = f"""Текущие параметры:\
<blockquote>\
<b>{title}</b>
{subtitle or ""}
#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}\
</blockquote>\n
{image_generation_text}"""

        avatar_bytes = _get_avatar_bytes(title, subtitle, rgb)

        buttons = []
        if not message.chat.id == message.from_user.id:
            buttons.extend([InlineKeyboardButton(
                text="Задать как аватар чата",
                callback_data=SetPhotoCallbackData().pack(),
            ),
                InlineKeyboardButton(
                    text="Удалить это сообщение",
                    callback_data=DeleteCallbackData().pack(),
                )
            ])

        await message.reply_photo(
            BufferedInputFile(avatar_bytes, "avatar.jpeg"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[buttons]
            ),
        )
    else:
        logging.info("No way...")


@dp.callback_query(SetPhotoCallbackData.filter())
async def handle_set_image(callback_query: CallbackQuery):
    await callback_query.answer()
    chat_member = await bot.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
    if chat_member.status == ChatMemberStatus.ADMINISTRATOR or chat_member.status == ChatMemberStatus.CREATOR:
        as_html = Text.from_entities(callback_query.message.caption, callback_query.message.caption_entities).as_html()
        first_blockquote = re.search(r"<blockquote>(?P<content>.*?)</blockquote>", as_html, re.DOTALL | re.MULTILINE)
        content = first_blockquote.group("content")
        splitted = content.splitlines()

        title, subtitle, color, *_ = (splitted + [None, None, None])[:3]

        if color is not None:
            color = color.lstrip("#")
            rgb = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        else:
            rgb = pick_stable_random(title)

        avatar_bytes = _get_avatar_bytes(title, subtitle, rgb)
        await bot.set_chat_photo(
            chat_id=callback_query.message.chat.id,
            photo=BufferedInputFile(avatar_bytes, "avatar.jpeg"),
        )
        if callback_query.message.reply_to_message:
            await callback_query.message.reply_to_message.delete()
        await callback_query.message.delete()
    else:
        logging.info("No way...")


@dp.callback_query(DeleteCallbackData.filter())
async def handle_delete_message(callback_query: CallbackQuery):
    await callback_query.answer()
    chat_member = await bot.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
    if chat_member.status == ChatMemberStatus.ADMINISTRATOR or chat_member.status == ChatMemberStatus.CREATOR:
        await callback_query.message.delete()


@dp.message()
async def handle(message: types.Message):
    if message.new_chat_members and message.new_chat_members[0].id == bot.id:
        text = (
            "Привет 👋 Я бот, который удаляет уведомления о входе и выходе участников в чатах. Также я умею "
            "генерировать аватарку для чата (/set_image).\n\n"
        )
        bot_chat_member = await bot.get_chat_member(message.chat.id, bot.id)
        if bot_chat_member.status != ChatMemberStatus.ADMINISTRATOR:
            text += (
                "Пожалуйста, назначьте меня администратором, чтобы я мог удалять уведомления о входе и выходе "
                "участников."
            )
        else:
            text += "✅ Я администратор, для дальнейшей работы всё уже настроено."

        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Удалить это сообщение",
                            callback_data=DeleteCallbackData().pack(),
                        ),
                    ]
                ]
            ),
        )
        chat = await bot.get_chat(message.chat.id)

        if chat.photo is None and bot_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
            title, subtitle = get_course_name(message.chat.full_name), get_semester(message.chat.full_name)
            rgb = pick_stable_random(title)
            avatar_bytes = _get_avatar_bytes(title, subtitle, rgb)
            await bot.set_chat_photo(
                chat_id=message.chat.id,
                photo=BufferedInputFile(avatar_bytes, "avatar.jpeg"),
            )

    if (
            message.left_chat_member is not None
            or message.new_chat_members is not None
            or message.new_chat_photo is not None
    ):
        try:
            await message.delete()
            logging.info(f"Message deleted: {message.message_id}")

        except TelegramBadRequest as e:
            logging.warning(f"Message can't be deleted: {e}")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
