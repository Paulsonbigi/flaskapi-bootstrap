
from sqlalchemy import String, Integer, Column
from app.database import Base


class Questions(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
