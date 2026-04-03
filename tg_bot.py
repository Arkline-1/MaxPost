import datetime

from aiogram import Bot
from setup import TG_CHAT_ID


async def send_to_telegram(bot: Bot, data_list: list[dict]):
    for item in data_list:
        ts = item['time'] / 1000
        readable_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        caption = f"[{item['sender']}] - ({readable_time})\n\n{item['text']}"

        try:
            if not item["attaches"]:
                await bot.send_message(TG_CHAT_ID, caption)
            else:
                await bot.send_photo(
                    TG_CHAT_ID, photo=item["attaches"][0], caption=caption
                )
        except Exception as e:
            print(f"Some shit happend: {e}")
