from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = 6531829050  # ← Твой Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Память: user_id → выбранная роль
pending_roles = {}

# Кнопки ролей
role_links = {
    "Офф": [("📦 Набор ссылок для Офф", "https://t.me/addlist/6XIB_me1UYlhMDNk")],
    "Дефф": [("🛡 Набор ссылок для Дефф", "https://t.me/addlist/uv1ZpnRg1_JkYTg8")],
    "Разведка": [("🕵 Набор ссылок для Разведки", "https://t.me/addlist/7iU3qTh6dSVmNmVk")],
    "Технический аккаунт": [("🔧 Набор ссылок для Тех. аккаунтов", "https://t.me/addlist/hv9Lf2yT9m1kZjRk")],
    "Только общий доступ": [("🔗 Общие ссылки (только для просмотра)", "https://t.me/addlist/4vn6JsYqmLtjZDJk")]
}

role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(
    KeyboardButton("Офф"),
    KeyboardButton("Дефф"),
    KeyboardButton("Разведка"),
    KeyboardButton("Технический аккаунт"),
    KeyboardButton("Только общий доступ")
)

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("👋 Привет! Выбери свою роль в альянсе:", reply_markup=role_keyboard)

# Обработка выбора роли
@dp.message_handler(lambda message: message.text in role_links)
async def ask_nickname(message: types.Message):
    role = message.text
    user_id_str = str(message.from_user.id)

    # Проверка, не выбрал ли уже
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

    # Сохраняем выбранную роль во временное хранилище
    pending_roles[message.from_user.id] = role
    await message.reply("🧩 Введи, пожалуйста, свой **игровой никнейм**:")

# Обработка игрового никнейма
@dp.message_handler(lambda message: message.from_user.id in pending_roles)
async def receive_nickname(message: types.Message):
    user_id = message.from_user.id
    role = pending_roles[user_id]
    nickname = message.text.strip()

    # Подключение к таблице
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Travian Logs").sheet1

    # Запись
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        now,
        str(user_id),
        message.from_user.username or "",
        message.from_user.full_name,
        role,
        nickname
    ])

    # Отправка ссылок
    links = role_links[role]
    text = f"🔗 Ссылки для роли *{role}*:\n\n"
    for name, url in links:
        text += f"{name}: [перейти]({url})\n"
    await message.reply(text, parse_mode="Markdown")

    # Очистка из временного хранилища
    del pending_roles[user_id]

# Команда /reset (только админ)
@dp.message_handler(commands=['reset'])
async def reset_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ У тебя нет прав на выполнение этой команды.")
        return

    username_to_remove = message.get_args().strip().lstrip('@')
    if not username_to_remove:
        await message.reply("✏️ Укажи username: /reset @username")
        return

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Travian Logs").sheet1

    usernames = sheet.col_values(3)
    if username_to_remove not in usernames:
        await message.reply(f"⚠️ Пользователь @{username_to_remove} не найден в таблице.")
        return

    index = usernames.index(username_to_remove) + 1
    sheet.delete_rows(index)
    await message.reply(f"✅ Пользователь @{username_to_remove} успешно сброшен.")

# Ответ по умолчанию
@dp.message_handler()
async def fallback(message: types.Message):
    await message.reply("❗ Пожалуйста, выбери роль, используя кнопки ниже.")

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
