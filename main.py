import asyncio
from aiogram import Bot
from setup import TG_TOKEN
from ws import MaxClient, Opcode, MaxEvent, GetChatMessagesResponse, Message, NewMessage
from telegram import forward_message_to_telegram


async def universal_handler(event: MaxEvent, bot: Bot):
    messages: list[Message] = list()

    if event.opcode == Opcode.GET_CHAT_HISTORY:
        messages = GetChatMessagesResponse(**event.payload).messages

    elif event.opcode == Opcode.MESSAGE_CREATE:
        single_msg = NewMessage(**event.payload).message

        if single_msg:
            messages = [single_msg]

    if not messages:
        return

    for msg in messages:
        links = [d.get("baseUrl") for d in msg.attaches]
        attaches = [link for link in links if link]

        await forward_message_to_telegram(bot, msg.time, msg.sender, msg.text, attaches)


async def main():
    bot = Bot(token=TG_TOKEN)
    client = MaxClient(bot=bot)

    client.add_listener(Opcode.GET_CHAT_HISTORY, universal_handler)
    client.add_listener(Opcode.MESSAGE_CREATE, universal_handler)

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
