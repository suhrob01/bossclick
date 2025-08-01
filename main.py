import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8290424201:AAHV40siIjqm_hWytET8uBZI5X5HvUft9HI"
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
db = sqlite3.connect("boss_coin.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    lang TEXT DEFAULT 'ru'
)
""")
db.commit()

lang_data = {
    "ru": {
        "start": "\u041f\u0440\u0438\u0432\u0435\u0442! \u042d\u0442\u043e <b>BOSS COIN</b>! \u041d\u0430\u0436\u0438\u043c\u0430\u0439 \u043a\u043d\u043e\u043f\u043a\u0443 \u0438 \u0437\u0430\u0440\u0430\u0431\u0430\u0442\u044b\u0432\u0430\u0439 \u043c\u043e\u043d\u0435\u0442\u044b!",
        "earn": "Заработать 💰",
        "balance": "💰 У тебя <b>{}</b> монет",
        "choose_lang": "\ud83c\udf10 \u0412\u044b\u0431\u0435\u0440\u0438 \u044f\u0437\u044b\u043a:",
        "set_lang": "\ud83d\udd04 \u042f\u0437\u044b\u043a \u0441\u043c\u0435\u043d\u0451\u043d."
    },
    "en": {
        "start": "Welcome to <b>BOSS COIN</b>! Tap the button to earn coins!",
        "earn": "Earn \ud83d\udcb0",
        "balance": "\ud83d\udcb0 You have <b>{}</b> coins",
        "choose_lang": "\ud83c\udf10 Choose language:",
        "set_lang": "\ud83d\udd04 Language changed."
    }
}

def get_user(user_id):
    cursor.execute("SELECT coins, lang FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        db.commit()
        return 0, 'ru'
    return result

def update_coins(user_id, amount):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    db.commit()

def set_language(user_id, lang):
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
    db.commit()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    coins, lang = get_user(user_id)
    text = lang_data[lang]["start"]
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=lang_data[lang]["earn"], callback_data="earn")
    ]])
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "earn")
async def earn_coins(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    coins, lang = get_user(user_id)
    update_coins(user_id, 1)
    await callback.answer(lang_data[lang]["balance"].format(coins + 1), show_alert=True)

@dp.message(Command("balance"))
async def check_balance(message: Message):
    user_id = message.from_user.id
    coins, lang = get_user(user_id)
    await message.answer(lang_data[lang]["balance"].format(coins))

@dp.message(Command("language"))
async def change_language(message: Message):
    user_id = message.from_user.id
    coins, lang = get_user(user_id)
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Русский", callback_data="set_lang_ru"),
        InlineKeyboardButton(text="English", callback_data="set_lang_en")
    )
    await message.answer(lang_data[lang]["choose_lang"], reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_lang(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.replace("set_lang_", "")
    set_language(user_id, lang_code)
    await callback.answer(lang_data[lang_code]["set_lang"], show_alert=True)
    await callback.message.delete()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
