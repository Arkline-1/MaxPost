import asyncio
from connection import create_max_session, create_tg_bot
from messages.input import start_polling


async def main():
    async with create_max_session() as session:
        tg_bot = create_tg_bot()
        await start_polling(session, tg_bot)


if __name__ == "__main__":
    asyncio.run(main())
