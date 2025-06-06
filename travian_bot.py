from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Telegram token из переменной среды
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Роли и ссылки
role_links = {
    "Офф": [("📦 Набор ссылок для Офф", "https://t.me/addlist/6XIB_me1UYlhMDNk")],
    "Дефф": [("🛡 Набор ссылок для Дефф", "https://t.me/addlist/uv1ZpnRg1_JkYTg8")],
    "Разведка": [("🕵 Набор ссылок для Разведки", "https://t.me/addlist/7iU3qTh6dSVmNmVk")],
    "Технический аккаунт": [("🔧 Набор ссылок для Тех. аккаунтов", "https://t.me/addlist/hv9Lf2yT9m1kZjRk")],
    "Только общий доступ": [("🔗 Общие ссылки (только для просмотра)", "https://t.me/addlist/4vn6JsYqmLtjZDJk")]
}

# Клавиатура выбора ролей
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
    user_id_str = str(message.from_user.id)

    # Проверка наличия записи в Google Таблице
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Travian Logs").sheet1
    ids = sheet.col_values(2)

    if user_id_str in ids:
        index = ids.index(user_id_str) + 1
        old_role = sheet.cell(index, 5).value
        await message.reply(f"⚠️ Ты уже выбрал роль: *{old_role}*\n\nЕсли нужно изменить — обратись к офицеру.", parse_mode="Markdown")
        return

    # Отправка ссылок
    links = role_links[role]
    text = f"🔗 Ссылки для роли *{role}*:\n\n"
    for name, url in links:
        text += f"{name}: [перейти]({url})\n"
    await message.reply(text, parse_mode="Markdown")

    # Запись в Google Таблицу
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        now,
        user_id_str,
        message.from_user.username or "",
        message.from_user.full_name,
        role
    ])

@dp.message_handler()
async def fallback(message: types.Message):
    await message.reply("❗ Пожалуйста, выбери роль, используя кнопки ниже.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
