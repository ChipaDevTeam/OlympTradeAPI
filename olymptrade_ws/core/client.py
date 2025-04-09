import asyncio
import websockets
import json
from typing import Callable, Dict, Any


class OlympWebSocketClient:
    # Add to the class __init__
    def __init__(self, url: str, headers: dict = None):
        self.url = url
        self.headers = headers or {}
        self.ws = None
        self.event_handlers = {}
        self.listen_task = None

    # Modify connect() to use headers
    async def connect(self):
        self.ws = await websockets.connect(self.url, extra_headers=self.headers)
        print("[CONNECTED] WebSocket connection established.")
        self.listen_task = asyncio.create_task(self._receive_loop())


    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        if self.listen_task:
            self.listen_task.cancel()
        print("[DISCONNECTED] WebSocket closed.")

    async def send(self, message: list):
        if self.ws:
            raw = json.dumps(message)
            await self.ws.send(raw)
            print("[SENT]", raw)
        else:
            raise RuntimeError("WebSocket not connected.")

    async def _receive_loop(self):
        try:
            while True:
                raw = await self.ws.recv()
                try:
                    messages = json.loads(raw)
                    if isinstance(messages, list):
                        for message in messages:
                            await self._handle_message(message)
                    else:
                        await self._handle_message(messages)
                except json.JSONDecodeError:
                    print("[ERROR] Failed to decode JSON:", raw)
        except websockets.ConnectionClosed:
            print("[CLOSED] WebSocket connection lost.")

    async def _handle_message(self, message: dict):
        event_code = message.get("e")
        if event_code is not None and event_code in self.event_handlers:
            await self.event_handlers[event_code](message)
        else:
            print("[RECEIVED - UNHANDLED]", message)

    def on_event(self, event_code: int, handler: Callable[[dict], Any]):
        self.event_handlers[event_code] = handler
