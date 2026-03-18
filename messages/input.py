from logger import logger
from messages.output import handle_message


async def start_polling(session, bot):
    marker = None
    while True:
        params = {"marker": marker} if marker else {}

        async with session.get("/updates", params=params) as response:
            data = await response.json()

        marker = data["marker"]

        for update in data["updates"]:
            if update["update_type"] == "message_created":
                logger.info(f"Получено обновление: {update['update_type']}")
                await handle_message(session, bot, update)
