from contextlib import asynccontextmanager
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from models import SessionLocal


@asynccontextmanager
async def create_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

class SQLAlchemySessionManager(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        message.conf['db_session'] = SessionLocal()

    async def on_post_process_message(self, message: types.Message, data: dict, result):
        message.conf['db_session'].close()
