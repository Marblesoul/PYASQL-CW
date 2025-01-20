import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = sq.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True, index=True)

    user_words = relationship("UserWord", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id})"

class Word(Base):
    __tablename__ = "words"

    id = sq.Column(sq.Integer, primary_key=True, index=True)
    lang_ru = sq.Column(sq.String, unique=True)
    lang_en = sq.Column(sq.String, unique=True)

    user_words = relationship("UserWord", back_populates="word")

    def __repr__(self):
        return f"Word(id={self.id}, lang_ru={self.lang_ru}, lang_en={self.lang_en})"

class UserWord(Base):
    __tablename__ = "user_words"

    id = sq.Column(sq.Integer, primary_key=True, index=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"))
    word_id = sq.Column(sq.Integer, sq.ForeignKey("words.id"))
    user = relationship("User", back_populates="user_words")
    word = relationship("Word", back_populates="user_words")

    def __repr__(self):
        return f"UserWord(id={self.id}, word_id={self.word_id})"


def create_db_and_tables():
    print('Creating database...')
    Base.metadata.create_all(bind=engine)