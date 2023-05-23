from aiogram import Dispatcher, types
# from dotenv import load_dotenv
# import os
# import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.middlewares import BaseMiddleware
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from models import User, Question, Answer, SessionLocal
# from middlewares import SQLAlchemySessionManager
from sqlalchemy import and_
from config import dp


        
class Quiz(StatesGroup):
    q_number = State()


# @dp.message_handler(commands=["Start"])
async def start_cmd(message: types.Message):
    db_session = message.conf['db_session']
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        # user does not exist yet, lets create one
        user = User(name=message.from_user.username, telegram_id=message.from_user.id)
        db_session.add(user)
        db_session.commit()
    await message.answer("Привет! Для участия в квизе введи `/quiz` или выбери пункт меню")


# @dp.message_handler(commands=["quiz"])
async def quiz_cmd(message: types.Message):
    db_session = message.conf['db_session']
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user and user.succeeded:
        await message.answer("Спасибо за активность, но вы уже участвовали")
    else:
        await Quiz.q_number.set()
        question = db_session.query(Question).first()
        await message.answer(f"Первый вопрос: {question}")



def check_answer(answer: str, question_number: int, db_session):
    correct_answer = db_session.query(Answer).filter_by(
        question_id=question_number, 
        correct=True).first()
    return correct_answer if correct_answer.text.lower() == answer else None    


async def send_question(message: types.Message, question: str, retry = False):
    if retry:
        question = f"К сожалению неправильно. Попробуйте еще раз. {question}"
    await message.answer(question)


async def process_answer(message: types.Message, state: FSMContext):
    db_session = message.conf['db_session']
    question_number = await state.get_data()
    question_number = question_number.get('q_number', 1)
    current_question = db_session.query(Question).filter(Question.id == question_number).first()
    length = db_session.query(Question.id).count()
    answer = message.text.strip().lower()
    if question_number < length:
        if check_answer(answer, question_number, db_session):
            next_question = db_session.query(Question).filter(Question.id > question_number).first()
            await send_question(message, next_question.text)
            await state.update_data(q_number = next_question.id)
        else:
            await send_question(message, current_question.text, True)
    else:
        # last question answered
        if check_answer(answer, question_number, db_session):
            await message.answer("Cool, your flag is {SUCCESS}")
            the_user = db_session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if the_user:
                the_user.succeeded = True
                db_session.commit()
            await state.finish()
        else:
            await send_question(message, current_question.text)



async def cancel_quiz(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Спасибо за участие. До встреч!")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("quiz", "Запустить квиз"),
        types.BotCommand("cancel", "Остановить квиз"),
    ])


def register_hadlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(quiz_cmd, commands=["quiz"])
    dp.register_message_handler(cancel_quiz, commands=["cancel"], state="*")    
    dp.register_message_handler(process_answer, state=Quiz.q_number)
