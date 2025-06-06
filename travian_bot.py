from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Ссылки по ролям
role_links = {
    "Офф": [("📦 Набор ссылок для Офф", "https://t.me/addlist/6XIB_me1UYlhMDNk")],
    "Дефф": [("🛡 Набор ссылок для Дефф", "https://t.me/addlist/uv1ZpnRg1_JkYTg8")],
    "Разведка": [("🕵 Набор ссылок для Разведки", "https://t.me/addlist/7iU3qTh6dSVmNmVk")],
    "Технический аккаунт": [("🔧 Набор ссылок для Тех. аккаунтов", "https://t.me/addlist/hv9Lf2yT9m1kZjRk")],
    "Только общий доступ": [("🔗 Общие ссылки (только для просмотра)", "https://t.me/addlist/4vn6JsYqmLtjZDJk")]
}

# Кнопки
role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(
    KeyboardButton("Офф"),
    KeyboardButton("Дефф"),
    KeyboardButton("Разведка"),
    KeyboardButton("Технический аккаунт"),
    KeyboardButton("Только общий доступ")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("👋 Привет! Выбери свою роль в альянсе:", reply_markup=role_keyboard)

@dp.message_handler(lambda message: message.text in role_links)
async def send_links(message: types.Message):
    role = message.text
    links = role_links[role]
    text = f"🔗 Ссылки для роли *{role}*:\n\n"
    for name, url in links:
        text += f"{name}: [перейти]({url})\n"
    await message.reply(text, parse_mode="Markdown")

@dp.message_handler()
async def fallback(message: types.Message):
    await message.reply("❗ Пожалуйста, выбери роль с кнопки ниже.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
