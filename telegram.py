import datetime

from aiogram import Bot
from setup import TG_CHAT_ID


async def forward_message_to_telegram(bot: Bot, time: int, sender_id: int, text: str, attaches: list[str]):
    caption = f"[{sender_id}]\n\n{text}"

    try:
        if not attaches and text:
            await bot.send_message(TG_CHAT_ID, caption)
        else:
            for photo in attaches:
                await bot.send_photo(
                    TG_CHAT_ID, photo=photo, caption=caption
                )
    except Exception as e:
        print(f"Some shit happend: {e}")
