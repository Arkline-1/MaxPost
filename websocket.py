from aiohttp import ClientSession, WSMsgType
from dataclasses import dataclass, asdict
from collections.abc import Callable, Awaitable
from enum import IntEnum
import asyncio
import json
import uuid


class Opcode(IntEnum):
    ACK = 1
    INIT = 6
    AUTHORIZE = 19
    GET_CHAT_MESSAGES = 49


@dataclass
class InitUserAgent:
    deviceType: str
    locale: str
    deviceLocale: str
    osVersion: str
    headerUserAgent: str
    appVersion: str
    screen: str
    timezone: str


@dataclass
class InitPayload:
    userAgent: InitUserAgent
    deviceId: str


@dataclass
class AuthPayload:
    token: str
    chatCounts: int
    interactive: bool
    chatSync: int
    contactsSync: int
    presenceSync: int
    draftsSync: int


@dataclass
class GetChatMessagesPayload:
    chatId: str
    at: int
    forward: int
    backward: int
    getMessages = True


@dataclass
class Message:
    sender: int
    id: str
    time: int
    text: str
    type: str
    cid: int
    attaches: list[dict]
    reactionInfo: dict | None = None


@dataclass
class GetChatMessagesResponse:
    messages: list[Message]

    def __post_init__(self):
        if self.messages and isinstance(self.messages[0], dict):
            self.messages = [Message(**x) for x in self.messages]


type Payload = InitPayload | AuthPayload | GetChatMessagesResponse


@dataclass
class MaxEvent:
    ver: int
    cmd: int
    seq: int
    opcode: Opcode
    payload: dict | None


MAX_WEBSOCKET_URL = "wss://ws-api.oneme.ru/websocket"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"
TOKEN = "An_Sx6HQ9HDiyzXOY-CJ7rHpTLyltqMnzfrLMbQKu0cAEezF3TC7e56PeuOU4nuy5rDovpVsBoKRspXVNt1cqwy2wudXg7UFhBZimgC641eCJGo7IPE3ijL6-jLyUNkOdOd7i8BrM0jk7Fhy_KHBE6EB6BFQEtnKnUlOXUvIvX4f_sEHnmbv-RUGDe1zp7l-zPkzGbyshPNp2qnCUQ_vdv39dZQ_IUxYtqIceMKJgsHntcWWG88Dl7z4V7ml17i5xXelxF_KwLVkvab5f0EPW1A8YC2uxI4H1cclQs_3h6MnqHhfXNfbRQHT5RbTrr180bLrq1n_aMHjxPxlFGXTBjp2APsbuqzCtADtgstywGvU5UbSZ2VqNqP9Unpj4AE2cwITafGMAohE_4UASXq03L8Io0XviceM6V2h-08oEHichd9cqHHVtIGjB5Lq3W3AULNzBrvMxz3eiy9AVcBOIm_SjkF3K8kkzttJyc6XiXhEm8PGpw7oGf7LtwTnbigtDDDxS4ZPB0D6a7ujOPd0t-QlPVOOR80NnnSzuDsW1IKWOefccHyGFvmYyZugJnodu6U8UZGghHUqaOtfIr1Voxoi1Y_LiX5D4D5EBYUiZmJGymwXvfRxeA3QrLGYOLUmEOV7vK2yUfCAiZ0X89w-9BnRVmkwNb67QDVmKqKcq7rl6dSQi30wJwO_rrs4Z_SRxkIFPmA"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "en-US",
    "Origin": "https://web.max.ru",
    "DNT": "1",
    "Sec-GPC": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

INIT_PAYLOAD = InitPayload(
    InitUserAgent(
        "WEB",
        "ru",
        "ru",
        "Linux",
        USER_AGENT,
        "26.3.9",
        "1440x2560 1.0x",
        "Asia/Aqtobe",
    ),
    str(uuid.uuid4()),
)

AUTH_PAYLOAD = AuthPayload(TOKEN, 40, True, 0, 0, 0, 0)


def create_init_obj() -> dict:
    return asdict(MaxEvent(11, 0, 0, int(Opcode.INIT), payload=INIT_PAYLOAD))


def create_auth_obj() -> dict:
    return asdict(MaxEvent(11, 0, 1, int(Opcode.AUTHORIZE), payload=AUTH_PAYLOAD))


def create_ack_obj(seq: int) -> dict:
    return asdict(
        MaxEvent(11, 0, seq, int(Opcode.ACK), payload={"interactive": True})
    )


def create_fetch_chat_messages_obj(
    chat_id: str, at: int, before: int = 0, after: int = 0
) -> dict:
    d = asdict(
        MaxEvent(
            11, 0, -1, int(Opcode.GET_CHAT_MESSAGES),
            payload=GetChatMessagesPayload(chat_id, at, after, before),
        )
    )
    d["payload"]["from"] = d["payload"].pop("at")

    return d


class MaxClient:
    def __init__(self, injection: dict | None = None):
        self.seq = 0
        self.session = None
        self.ws = None
        self._hb = None
        self.inj = injection
        self.handlers: dict[int, Callable[[MaxEvent, dict | None], Awaitable[None]]] = (
            dict()
        )

    def add_listener(
        self,
        opcode: Opcode,
        callback: Callable[[MaxEvent, dict | None], Awaitable[None]],
    ) -> None:
        self.handlers[int(opcode)] = callback

    async def send(self, data: dict):
        if not self.ws:
            raise ValueError("Client is not running")

        data["seq"] = self.seq
        await self.ws.send_json(data)
        self.seq += 1

    async def _send_ack(self):
        await self.ws.send_json(create_ack_obj(self.seq))

    async def _heartbeat_loop(self):
        while not self.ws.closed:
            await self.send_ack(self.seq)
            self.seq += 1

            await asyncio.sleep(25)

    async def close(self):
        if self._hb:
            self._hb.cancel()

        if self.ws:
            await self.ws.close()

        if self.session:
            await self.session.close()

    async def connect(self) -> None:
        self.session = ClientSession()

        try:
            self.ws = await self.session.ws_connect(
                MAX_WEBSOCKET_URL, headers=HEADERS
            )
            self._hb = asyncio.create_task(self._heartbeat_loop())
        except Exception as e:
            self.close()
            raise e

    async def run(self) -> None:
        await self.connect()

        await self.send(create_init_obj())
        await asyncio.sleep(0.5)
        await self.send(create_auth_obj())

        try:
            async for msg in self.ws:
                if msg.type == WSMsgType.TEXT:
                    event = MaxEvent(**json.loads(msg.data))
                    callback = self.handlers.get(event.opcode)

                    if callback:
                        await callback(event, self.inj)
                    else:
                        print(event)

                elif msg.type == WSMsgType.ERROR:
                    print(f"Some shit happend: {self.ws.exception()}")
                    break
        finally:
            await self.close()
