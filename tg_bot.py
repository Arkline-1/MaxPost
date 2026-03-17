from aiogram import Bot
from aiogram.types import FSInputFile
from setup import TG_CHAT_ID


async def send_text(bot: Bot, text: str) -> None:
    await bot.send_message(chat_id=TG_CHAT_ID, text=text)


async def send_photo(bot: Bot, photo_path: str) -> None:
    await bot.send_photo(chat_id=TG_CHAT_ID, photo=FSInputFile(photo_path))


async def send_document(bot: Bot, file_path: str) -> None:
    await bot.send_document(chat_id=TG_CHAT_ID, document=FSInputFile(file_path))
