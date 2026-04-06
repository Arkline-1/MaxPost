import asyncio
from aiogram import Bot
from setup import TG_TOKEN, MAX_CHAT_ID
from ws import MaxClient, Opcode, create_fetch_chat_messages_obj, MaxEvent, GetChatMessagesResponse, Message
from tg_bot import send_to_telegram


async def universal_handler(event: MaxEvent, injection: dict | None):
    bot: Bot = injection.get("bot")

    raw_messages = []

    if event.opcode == Opcode.GET_CHAT_MESSAGES:
        raw_messages = event.payload.get("messages", [])

    elif event.opcode == Opcode.MESSAGE_CREATE:
        single_msg = event.payload.get("message")
        if single_msg:
            raw_messages = [single_msg]

    if not raw_messages:
        return

    processed = []
    for m_data in raw_messages:
        msg = Message(**m_data)

        links = [d.get("baseUrl") for d in msg.attaches]

        processed.append({
            "sender": msg.sender,
            "time": msg.time,
            "text": msg.text,
            "attaches": [link for link in links if link]
        })

    await send_to_telegram(bot, processed)


async def main():
    bot = Bot(token=TG_TOKEN)
    client = MaxClient(injection={"bot": bot})

    client.add_listener(Opcode.GET_CHAT_MESSAGES, universal_handler)
    client.add_listener(Opcode.MESSAGE_CREATE, universal_handler)

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
