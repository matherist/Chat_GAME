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
from sqlalchemy import and_, desc
from config import dp


        
class Quiz(StatesGroup):
    q_number = State()



async def update_q_number(state: FSMContext, num: int):
    await state.update_data(q_number=num)


async def get_current_question_from_state(state: FSMContext):
    question_number = await state.get_data()
    question_number = question_number.get('q_number', 1)
    return question_number

def check_answer(answer: str, question_number: int, db_session):
    correct_answer = db_session.query(Answer).filter_by(
        question_id=question_number, 
        correct=True).first()
    return correct_answer if correct_answer.text.lower() == answer else None   


async def send_question(message: types.Message, question: str, retry = False):
    if retry:
        question = f"К сожалению неправильно. Попробуйте еще раз. {question}"
    await message.answer(question)

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
        state = dp.current_state()
        first_question = db_session.query(Question).first()
        if first_question:
            await update_q_number(state, first_question.id)
            await message.answer(f"Первый вопрос: {first_question}")


async def process_answer(message: types.Message, state: FSMContext):
    db_session = message.conf['db_session']
    answer = message.text.strip().lower()

    q_num = await get_current_question_from_state(state)
    current_question = db_session.query(Question).filter(Question.id == q_num).first()
    length = db_session.query(Question).order_by(desc('id')).first().id

    if q_num < length:
        if check_answer(answer, q_num, db_session):
            # switch to next question if answer was correct
            next_question = db_session.query(Question).filter(Question.id > q_num).first()
            await send_question(message, next_question.text)
            await update_q_number(state, next_question.id)
        else:
            # wrong answer for current question
            await send_question(message, current_question.text, True)
    else:
        # last question answered
        if check_answer(answer, q_num, db_session):
            await message.answer("Cool, your flag is {SUCCESS}")
            the_user = db_session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if the_user:
                the_user.succeeded = True
                db_session.commit()
            await state.finish()
        else:
            await send_question(message, current_question.text, True)



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