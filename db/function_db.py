from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from translate import Translator
from db.create_db import User, Word, UserWord, engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user(message):
   with SessionLocal() as session:
       user = session.query(User.id).filter_by(id=message.from_user.id).first()
       if user:
           return True
       new_user = User(id=message.from_user.id)
       session.add(new_user)
       session.commit()
       return False

def check_user_dict(message):
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=message.from_user.id).first()
        user_word = session.query(UserWord).filter_by(user_id=user.id).all()
        print(f'user: {user}, user_word: {user_word}')
        if user and user_word:
            return True
        return False

def add_word(user_id, words):
    for word in words:
        word_ru = word
        translator = Translator(from_lang="ru", to_lang="en")
        word_en = translator.translate(word_ru)
        with SessionLocal() as session:
            word = Word(lang_ru=word_ru, lang_en=word_en)
            user = session.query(User).filter_by(id=user_id).first()
            session.add(word)
            session.commit()
            user_word = UserWord(user_id=user_id, word_id=word.id)
            session.add(user_word)
            session.commit()
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        user_words = user.user_words
        all_words_count = len(user_words)
    result = f'Новые слова добавлены, всего слов в словаре: {all_words_count}'

    return result

def get_words_from_db(user_id):
    with SessionLocal() as session:
        words = session.query(Word.lang_en, Word.lang_ru) \
        .join(UserWord, isouter=True) \
        .where(UserWord.user_id.in_([user_id, None])) \
        .order_by(func.random()) \
        .limit(4) \
        .all()
        target_word = words.pop()
        return words, target_word


def delete_word_from_db(message):
    print(f'word: {message.text}, user_id: {message.from_user.id}')
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=message.from_user.id).first()
        word = session.query(Word).filter_by(lang_ru=message.text).first()
        user_word = session.query(UserWord).filter_by(user_id=message.from_user.id, word_id=word.id).first()
        session.delete(user_word)
        session.commit()
        return f'Слово {word.lang_ru} удалено из словаря'