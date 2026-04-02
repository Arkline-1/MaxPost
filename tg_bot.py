from aiogram import Bot
from setup import TG_CHAT_ID


async def send_text(bot: Bot, text: str) -> None:
    await bot.send_message(chat_id=TG_CHAT_ID, text=text)


async def send_photo(bot: Bot, photo_url: str) -> None:
    await bot.send_photo(chat_id=TG_CHAT_ID, photo=photo_url)


async def send_document(bot: Bot, file_url: str) -> None:
    await bot.send_document(chat_id=TG_CHAT_ID, document=file_url)
