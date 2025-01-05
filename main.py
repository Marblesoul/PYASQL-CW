import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from db.function_db import check_user, check_user_dict, add_word, get_words_from_db, delete_word_from_db
from config import TELEGRAM_TOKEN


print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = TELEGRAM_TOKEN
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []

basic_words = {
    'Hello': 'Привет',
    'Goodbye': 'Пока',
    'Morning': 'Утро',
    'Evening': 'Вечер',
    'Night': 'Ночь',
    'Good': 'Хорошо',
    'Bad': 'Плохо',
    'Yes': 'Да',
    'No': 'Нет',
    'Thank you': 'Спасибо'}


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if get_user_step(message.from_user.id) == 0:
        if check_user(message) and check_user_dict(message):
            userStep[cid] = 0
            bot.send_message(cid, f"С возвращением {message.from_user.first_name}, продолжим учить слова...")
            words, target_word_from_db = get_words_from_db(message.from_user.id)
            markup = types.ReplyKeyboardMarkup(row_width=2)

            global buttons
            buttons = []
            target_word = target_word_from_db[0]
            translate = target_word_from_db[1]
            target_word_btn = types.KeyboardButton(target_word)
            buttons.append(target_word_btn)
            others = [word[0] for word in words if word[0] != target_word]
            other_words_btns = [types.KeyboardButton(word) for word in others]
            buttons.extend(other_words_btns)
            random.shuffle(buttons)
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD,)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])

            markup.add(*buttons)

            greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
            bot.send_message(message.chat.id, greeting, reply_markup=markup)
            bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['target_word'] = target_word
                data['translate_word'] = translate
                data['other_words'] = others

        else:
            bot.send_message(cid, "Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе. \n\n У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения. Для этого воспрользуйся инструментами: \n\n добавить слово ➕,\nудалить слово 🔙.\n\nНу что, начнём ⬇️")


@bot.message_handler(commands=['get'])
def cmd_get(message):
    words, target_word = get_words_from_db(message.from_user.id)
    text = f'words: {str(words)}\ntarget_word: {str(target_word)}'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def handle_cmd_add_word(message):
    cmd_add_word(message)


@bot.message_handler(commands=['add_word'])
def cmd_add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid, f"Введите слово (или слова списком через пробел) для добавления в словарь:")


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        result = delete_word_from_db(message.from_user.id, data['target_word'])
        bot.reply_to(message, result)
    create_cards(message)


@bot.message_handler(func=lambda message: userStep.get(message.chat.id, 0) == 1, content_types=['text'])
def add_word_to_db(message):
    if " " in message.text:
        words = [word.capitalize() for word in message.text.split()]
    else:
        words = [message.text.capitalize()]
    cid = message.chat.id
    with bot.retrieve_data(message.from_user.id, cid) as data:
        data['target_word'] = message.text
        result = add_word(message.from_user.id, words)
        bot.reply_to(message, result)
    userStep[cid] = 0
    create_cards(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)