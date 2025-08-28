import asyncio
import logging
import os
import re
from io import BytesIO

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.formatting import Text
from PIL.JpegPresets import presets

from src.avatar import generate_avatar
from src.color import pick_stable_random
from src.parse_chat_name import get_course_name, get_semester

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not API_TOKEN:
    raise ValueError("TELEGRAM_API_TOKEN is not set")


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


@dp.message(F.left_chat_member.is_not(None) | F.new_chat_members.is_not(None) | F.new_chat_photo.is_not(None))
async def handle_message_with_deletable_actions(message: types.Message):
    await message.delete()
    logging.info(f"Message deleted: {message.chat.id=} message.message_id={message.message_id}")


@dp.message(Command("start"))
async def handle_start_command(message: types.Message, bot: Bot):
    text = (
        "Привет 👋\n\n"
        "Я бот от команды @one_zero_eight, удаляю уведомления о входе и выходе участников в чатах. "
        "Также я умею генерировать аватарку для чата (/set_image).\n\n"
        "Для того, чтобы я мог удалять уведомления о входе и выходе участников, назначьте меня администратором.\n"
        'Чтобы я сразу стал администратором в группе, нажмите на кнопку ниже, или добавьте меня в чат через "Информацию о боте" сверху (там где моё имя).'
    )
    me = await bot.me()
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить меня в группу", url=f"https://t.me/{me.username}?startgroup=new")]
            ]
        ),
    )


@dp.message(Command("set_image"))
async def handle_set_image_command(message: types.Message, command: CommandObject):
    assert message.from_user
    logging.info(
        f'handle_set_image_command: {message.chat.id=} chat.full_name="{message.chat.full_name}" message.from_user.id={message.from_user.id} message.from_user.username={message.from_user.username}'
    )
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id == message.from_user.id and not command.args:
        await message.answer(image_generation_text, reply_to_message_id=message.message_id, parse_mode="HTML")
        return
    if (
        message.chat.id == message.from_user.id
        or chat_member.status == ChatMemberStatus.ADMINISTRATOR
        or chat_member.status == ChatMemberStatus.CREATOR
    ):
        if command.args and len(command.args.splitlines()):
            splitted = command.args.splitlines()
            title, subtitle, color, *_ = (splitted + [None, None, None])[:3]
        else:
            title, subtitle, color = get_course_name(message.chat.full_name), get_semester(message.chat.full_name), None

        if title is None:
            title = get_course_name(message.chat.full_name)
        if subtitle is None:
            subtitle = get_semester(message.chat.full_name)

        if color is not None:
            color = color.lstrip("#")
            try:
                rgb = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            except ValueError:
                await message.answer(
                    "Неверный формат цвета. Пожалуйста, используйте формат #RRGGBB, или не указывайте цвет. Будет использован случайный цвет.",
                    reply_to_message_id=message.message_id,
                )
                rgb = pick_stable_random(title)
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
            buttons.append(
                [InlineKeyboardButton(text="Задать как аватар чата", callback_data=SetPhotoCallbackData().pack())]
            )
            buttons.append(
                [InlineKeyboardButton(text="Удалить это сообщение", callback_data=DeleteCallbackData().pack())]
            )

        await message.reply_photo(
            BufferedInputFile(avatar_bytes, "avatar.jpeg"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
    else:
        logging.info("No way...")


@dp.callback_query(SetPhotoCallbackData.filter())
async def handle_set_image_callback(callback_query: CallbackQuery):
    assert callback_query.message
    logging.info(
        f"handle_set_image_callback: {callback_query.message.chat.id=} [{callback_query.message.chat.full_name}] {callback_query.from_user.id=} [{callback_query.from_user.username}]"
    )

    await callback_query.answer()
    chat_member = await bot.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
    if chat_member.status == ChatMemberStatus.ADMINISTRATOR or chat_member.status == ChatMemberStatus.CREATOR:
        assert isinstance(callback_query.message, types.Message)
        as_html = Text.from_entities(
            callback_query.message.caption or "", callback_query.message.caption_entities or []
        ).as_html()
        first_blockquote = re.search(r"<blockquote>(?P<content>.*?)</blockquote>", as_html, re.DOTALL | re.MULTILINE)
        content = first_blockquote.group("content") if first_blockquote else ""
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
    assert callback_query.message
    logging.info(
        f'handle_delete_message: {callback_query.message.chat.id=} chat.full_name="{callback_query.message.chat.full_name}" callback_query.from_user.id={callback_query.from_user.id} callback_query.from_user.username={callback_query.from_user.username}'
    )

    await callback_query.answer()
    assert callback_query.message
    chat_member = await bot.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
    if chat_member.status == ChatMemberStatus.ADMINISTRATOR or chat_member.status == ChatMemberStatus.CREATOR:
        if not isinstance(callback_query.message, types.InaccessibleMessage):
            await callback_query.message.delete()


@dp.my_chat_member()
async def handle_bot_status_change(my_chat_member: ChatMemberUpdated):
    logging.info(
        f'handle_bot_status_change: {my_chat_member.chat.id=} chat.full_name="{my_chat_member.chat.full_name}" old_status={my_chat_member.old_chat_member.status} new_status={my_chat_member.new_chat_member.status}'
    )

    old_status = my_chat_member.old_chat_member.status
    new_status = my_chat_member.new_chat_member.status

    # Check if bot was promoted to admin (from member, restricted, or left status)
    if (
        old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED, ChatMemberStatus.LEFT]
        and new_status == ChatMemberStatus.ADMINISTRATOR
    ):
        await bot.send_message(my_chat_member.chat.id, "✅ Я администратор, для дальнейшей работы всё уже настроено.")
        chat = await bot.get_chat(my_chat_member.chat.id)

        # Set chat photo if none exists
        if chat.photo is None:
            title, subtitle = (
                get_course_name(my_chat_member.chat.full_name),
                get_semester(my_chat_member.chat.full_name),
            )
            rgb = pick_stable_random(title)
            avatar_bytes = _get_avatar_bytes(title, subtitle, rgb)
            try:
                await bot.set_chat_photo(
                    chat_id=my_chat_member.chat.id,
                    photo=BufferedInputFile(avatar_bytes, "avatar.jpeg"),
                )
                logging.info(f"Chat photo set for {my_chat_member.chat.id} after promotion to admin")
            except TelegramBadRequest as e:
                logging.warning(f"Failed to set chat photo: {e}")


@dp.message(F.new_chat_members.is_not(None) & F.new_chat_members.any(F.id == bot.id))
async def handle_bot_added_to_chat(message: types.Message):
    logging.info(
        f'handle_bot_added_to_chat: {message.chat.id=} chat.full_name="{message.chat.full_name}" message.from_user.id={message.from_user.id if message.from_user else None} message.from_user.username={message.from_user.username if message.from_user else None}'
    )

    text = (
        "Привет 👋\n\n"
        "Я бот от команды @one_zero_eight, удаляю уведомления о входе и выходе участников в чатах. "
        "Также я умею генерировать аватарку для чата (/set_image).\n\n"
    )
    bot_chat_member = await bot.get_chat_member(message.chat.id, bot.id)
    if bot_chat_member.status != ChatMemberStatus.ADMINISTRATOR:
        text += (
            "Пожалуйста, назначьте меня администратором, чтобы я мог удалять уведомления о входе и выходе "
            "участников."
        )
    else:
        text += "✅ Я администратор, для дальнейшей работы всё уже настроено."

    await message.answer(text)
    chat = await bot.get_chat(message.chat.id)

    if chat.photo is None and bot_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        title, subtitle = get_course_name(message.chat.full_name), get_semester(message.chat.full_name)
        rgb = pick_stable_random(title)
        avatar_bytes = _get_avatar_bytes(title, subtitle, rgb)
        await bot.set_chat_photo(
            chat_id=message.chat.id,
            photo=BufferedInputFile(avatar_bytes, "avatar.jpeg"),
        )


async def main() -> None:
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "my_chat_member"])


if __name__ == "__main__":
    asyncio.run(main())
