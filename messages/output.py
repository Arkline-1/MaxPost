from logger import logger
from messages.download import download_file
from tg_bot import send_document, send_photo, send_text


async def handle_message(session, bot, update):
    message = update["message"]
    attachments = message.get("attachments", [])
    logger.info(f"Обработка сообщения, вложений: {len(attachments)}")

    if not attachments:
        await send_text(bot, message["body"]["text"])
    else:
        for attachment in attachments:
            if attachment["type"] == "image":
                path = await download_file(
                    session, attachment["payload"]["url"], "photo.jpg"
                )
                await send_photo(bot, path)
            elif attachment["type"] == "file":
                path = await download_file(
                    session, attachment["payload"]["url"], attachment["payload"]["name"]
                )
                await send_document(bot, path)
