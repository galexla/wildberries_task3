from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


# class StripMentionMiddleware(BaseMiddleware):
#     def __init__(self, bot_username):
#         self.bot_username = bot_username

#     async def __call__(self, handler, event, data):
#         message = getattr(event, "message", None)
#         # print("###", event)
#         if message and isinstance(message, Message):
#             # print("###", message.text)
#             print("###", f"@{self.bot_username}")
#             if message.text.startswith(f"@{self.bot_username}"):
#                 message.text = message.text.replace(
#                     f"@{self.bot_username}", ""
#                 ).strip()
#                 # print("###", message.text)
#         return await handler(event, data)
