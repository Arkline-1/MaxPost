import aiohttp
from aiogram import Bot

from setup import MAX_API_URL, MAX_TOKEN, TG_TOKEN


def create_max_session() -> aiohttp.ClientSession:
    headers = {"Authorization": MAX_TOKEN}
    return aiohttp.ClientSession(base_url=MAX_API_URL, headers=headers)


def create_tg_bot() -> Bot:
    return Bot(token=TG_TOKEN)
