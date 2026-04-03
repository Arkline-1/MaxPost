from aiogram import Bot
from setup import TG_CHAT_ID


async def send_to_telegram(bot: Bot, data_list: list[dict]):
    for item in data_list:
        caption = f"[{item['sender']}] - ({item['time']})\n\n{item['text']}"
        
        if not item['attaches']:
            await bot.send_message(TG_CHAT_ID, caption)
        else:
            await bot.send_photo(TG_CHAT_ID, photo=item['attaches'][0], caption=caption)