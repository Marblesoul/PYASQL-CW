import random
from sqlalchemy.orm import sessionmaker
from translate import Translator
from db.create_db import User, Word, UserWord, engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user(message):
   with SessionLocal() as session:
       try:
           user = session.query(User.user_id).filter_by(user_id=message.from_user.id).first()
           if user:
               return True
           new_user = User(user_id=message.from_user.id)
           session.add(new_user)
           session.commit()
           return False
       except Exception as e:
           print(f'Error: {e}')
           return False

def check_user_dict(message):
    with SessionLocal() as session:
        try:
            user = session.query(User).filter_by(user_id=message.from_user.id).first()
            user_word = session.query(UserWord).filter_by(user_id=user.id).all()
            print(f'user: {user}, user_word: {user_word}')
            if user and user_word:
                return True
            return False
        except Exception as e:
            print(f'Error: {e}')
            return False

def add_word(user_id, words):
    result = 'Результаты добавления слов:\n\n'
    for word in words:
        lang_ru = word
        try:
            translator = Translator(from_lang="ru", to_lang="en")
            lang_en = translator.translate(lang_ru)
            with SessionLocal() as session:
                word = Word(lang_ru=lang_ru, lang_en=lang_en)
                user = session.query(User).filter_by(user_id=user_id).first()
                session.add(word)
                session.commit()
                user_word = UserWord(user_id=user.id, word_id=word.id)
                session.add(user_word)
                session.commit()
                result += f'Слово {lang_ru} добавлено в словарь с переводом {lang_en}\n'
        except Exception as e:
            print(f'Error: {e}')
            result += f'Ошибка при добавлении слова: {e}\n'
    with SessionLocal() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        user_words = user.user_words
        all_words_count = len(user_words)
    result += f'\nВсего слов в словаре: {all_words_count}'

    return result

def get_words_from_db(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        user_words = user.user_words
        all_words = [(word.word.lang_en, word.word.lang_ru) for word in user_words]
        random.shuffle(all_words)
        words = all_words[:4]
        target_word = random.choice(words)
        return words, target_word


def delete_word_from_db(user_id, word):
    print(f'user_id: {user_id}, word: {word}')
    with SessionLocal() as session:
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            word = session.query(Word).filter_by(lang_en=word).first()
            user_word = session.query(UserWord).filter_by(user_id=user.id, word_id=word.id).first()
            session.delete(user_word)
            session.commit()
            return f'Слово {word.lang_ru} удалено из словаря'
        except Exception as e:
            print(f'Error: {e}')
            return f'Ошибка при удалении слова: {e}'