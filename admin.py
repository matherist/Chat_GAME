from fastapi import FastAPI
from sqladmin import Admin, ModelView
from models import engine, SessionLocal, User, Question, Answer
from bot import dp


app = FastAPI()
admin = Admin(app, engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]

class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.text]
    # inline_models = [(Answer, dict(
    #     form_columns = ["id", "text"]
    # ))]

class AnswerAdmin(ModelView, model=Answer):
    column_list = [Answer.id, Answer.text]
    
admin.add_view(UserAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(AnswerAdmin)
