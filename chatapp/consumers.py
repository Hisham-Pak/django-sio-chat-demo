from __future__ import annotations
from typing import Any, Optional
import time

from sio import SocketIOConsumer
from sio.socketio import NamespaceSocket
from sio.consumer import Ack

ROOM_HISTORY: dict[str, list[dict[str, Any]]] = {}

def now_ms() -> int:
    return int(time.time() * 1000)

class ChatConsumer(SocketIOConsumer):
    namespace = "/"

    async def connect(self, socket: NamespaceSocket, auth: Any) -> bool:
        socket.state["username"] = (auth or {}).get("username") or "anon"
        return True

    async def event_join(
        self,
        socket: NamespaceSocket,
        room: str,
        username: Optional[str] = None,
        ack: Ack | None = None,
    ) -> None:
        if username:
            socket.state["username"] = username

        await socket.join(room)

        history = ROOM_HISTORY.get(room, [])[-50:]
        await socket.emit("joined", room, history)

        await socket.server.emit(
            "user-joined",
            room,
            socket.state["username"],
            room=room,
            namespace=self.namespace,
        )

        if ack:
            await ack({"ok": True})

    async def event_message(
        self,
        socket: NamespaceSocket,
        room: str,
        text: str,
        ack: Ack | None = None,
    ) -> None:
        if room not in socket.rooms:
            await socket.emit("error", "Join the room first")
            if ack:
                await ack({"ok": False, "error": "not_in_room"})
            return

        msg = {
            "id": str(now_ms()),
            "ts": now_ms(),
            "user": socket.state["username"],
            "text": text,
        }
        ROOM_HISTORY.setdefault(room, []).append(msg)

        await socket.server.emit(
            "message",
            room,
            msg,
            room=room,
            namespace=self.namespace,
        )

        if ack:
            await ack({"ok": True, "id": msg["id"]})

    async def event_leave(
        self,
        socket: NamespaceSocket,
        room: str,
        ack: Ack | None = None,
    ) -> None:
        await socket.leave(room)

        await socket.server.emit(
            "user-left",
            room,
            socket.state["username"],
            room=room,
            namespace=self.namespace,
        )

        if ack:
            await ack({"ok": True})

    async def event_typing(
        self,
        socket: NamespaceSocket,
        room: str,
        isTyping: bool,
    ) -> None:
        if room not in socket.rooms:
            return

        await socket.server.emit(
            "typing",
            room,
            socket.state["username"],
            bool(isTyping),
            room=room,
            namespace=self.namespace,
        )
