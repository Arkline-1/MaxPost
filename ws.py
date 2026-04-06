from aiohttp import ClientSession, WSMsgType
from collections.abc import Callable, Awaitable
from dataclasses import dataclass, asdict
from setup import MAX_TOKEN
from enum import IntEnum
import asyncio
import json
import uuid


class Opcode(IntEnum):
    ACK = 1
    INIT = 6
    AUTHORIZE = 19
    GET_CHAT_HISTORY = 49
    MESSAGE_CREATE = 128
    AUTH_TRACKING = 289


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
    getMessages: bool = True


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
    link: dict | None = None


@dataclass
class GetChatMessagesResponse:
    messages: list[Message]

    def __post_init__(self):
        if self.messages and isinstance(self.messages[0], dict):
            self.messages = [Message(**x) for x in self.messages]


@dataclass
class NewMessage:
    chatId: int
    unread: int
    message: Message
    ttl: bool
    mark: int
    prevMessageId: str


@dataclass
class MaxEvent:
    ver: int
    cmd: int
    seq: int
    opcode: Opcode
    payload: dict | None


MAX_WEBSOCKET_URL = "wss://ws-api.oneme.ru/websocket"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0"


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

AUTH_PAYLOAD = AuthPayload(MAX_TOKEN, 40, True, 0, 0, 0, 0)


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
            11, 0, -1, int(Opcode.GET_CHAT_HISTORY),
            payload=GetChatMessagesPayload(
                int(chat_id), int(at), after, before),
        )
    )
    d["payload"]["from"] = d["payload"].pop("at")

    return d


class MaxClient:
    def __init__(self, **kwargs):
        self.seq = 0
        self.session = None
        self.ws = None
        self.inj = kwargs
        self.handlers: dict[int, Callable[[MaxEvent, dict | None], Awaitable[None]]] = (
            dict()
        )
        self.tasks: list[asyncio.Task] = list()

    def add_loop_task(self, interval: float, callback: Callable) -> None:
        async def wrapper():
            try:
                while True:
                    await asyncio.sleep(interval)

                    if hasattr(callback, "__self__"):
                        await callback()
                    else:
                        await callback(self)

            except Exception as e:
                print(f"{callback.__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc()

        task = asyncio.create_task(wrapper())
        self.tasks.append(task)

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
        await self._send_ack()
        self.seq += 1

    async def close(self):
        for task in self.tasks:
            task.cancel()

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

            self.add_loop_task(20, self._heartbeat_loop)
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

                    print(event, "\n")

                    if callback:
                        await callback(event, **self.inj)

                elif msg.type == WSMsgType.ERROR:
                    print(f"Some shit happend: {self.ws.exception()}")
                    break
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED):
                    print(f"Some cripples closed WS with: {
                          self.ws.close_code}")
                    break
        finally:
            await self.close()
