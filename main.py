import asyncio
from datetime import datetime as dt

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from setup import TG_TOKEN, MAX_CHAT_ID
from ws import MaxClient, MaxEvent, GetChatMessagesResponse, Opcode, create_fetch_chat_messages_obj


async def get_messages(client: MaxClient):
    d = create_fetch_chat_messages_obj(
        MAX_CHAT_ID, dt.now().timestamp() * 1000, before=10)

    await client.send(d)


async def on_message(event: MaxEvent, injection: dict):
    pass


async def main():
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    client = MaxClient({"bot": bot})

    client.add_loop_task(300, get_messages)
    client.add_listener(Opcode.GET_CHAT_MESSAGES, on_message)

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
