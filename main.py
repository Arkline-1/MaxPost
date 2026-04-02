import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from setup import TG_TOKEN
from websocket import MaxClient


async def main():
    bot = Bot(
        token=TG_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    client = MaxClient({"bot": bot})

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
