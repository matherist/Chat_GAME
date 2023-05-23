from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    succeeded = Column(Boolean, default=False)
    telegram_id = Column(Integer)


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    answers = relationship("Answer", back_populates="question")

    def __str__(self):
        return f"{self.text[:50]}"

        
class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    correct = Column(Boolean, default=False)
    text = Column(String)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship("Question", back_populates="answers")

    def __str__(self):
        return self.text[:50]

Base.metadata.create_all(engine)

