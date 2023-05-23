from aiogram import executor 
from dotenv import load_dotenv
import os
import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from models import User, Question, Answer, SessionLocal
from middlewares import SQLAlchemySessionManager
from handlers import register_hadlers
from config import dp


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    register_hadlers(dp)

    
    executor.start_polling(dp)
