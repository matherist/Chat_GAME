import asyncio
# from aiogram import executor
# from fastapi import FastAPI
# from uvicorn import Config, Server
# from sqlalchemy.orm import Session
# from sqladmin import Admin, ModelView
# from models import engine, SessionLocal, User, Question, Answer
from bot import dp
from admin import app
from handlers import register_hadlers, set_default_commands



# Run Aiogram bot as a background task
async def run_bot():
    await set_default_commands(dp)
    register_hadlers(dp)
    await dp.start_polling()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())


@app.get("/")
async def read_root():
    return {"Hello": "World"}
