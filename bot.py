import os
import threading
from flask import Flask
import discord
from discord.ext import commands

# 1. Створення веб-сервера для Render Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Основна логіка Discord-бота
MY_DISCORD_ID = 1307739772785135636
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

ALLOWED_WORDS = [
    "ноль", "нулина", "нуб", "бот", "рак", "слитый", "слабый", "анскил",
    "нефор", "позорище", "лох", "дурак", "дурень", "бездарь", "лоускил",
    "руинер", "чушпан", "тюфяк", "шляпа", "тормоз", "воздухан", "чайник",
    "сопляк", "трус"
]

BAD_KEYWORDS = [
    "маму", "маме", "мамы", "папу", "отца", "родных", "мать", "родню",
    "http://", "https://", "join", "connect", "t.me/", "vk.com/",
    "сервер говно", "админ даун", "модер лох",
    "я админ", "я модератор", "я хелпер",
    "хохол", "москаль", "z", "v", "слава украине", "слава россии"
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успішно запущений у Web Service!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    text = message.content
    lower_text = text.lower()

    for allowed in ALLOWED_WORDS:
        if lower_text == allowed or f" {allowed} " in lower_text:
            await bot.process_commands(message)
            return

    reason = None
    default_time = "1h"

    if is_caps_violation(text):
        reason = "3.2 Капс (>70%)"
        default_time = "30m"
    else:
        for keyword in BAD_KEYWORDS:
            if keyword in lower_text:
                reason = f"Триггер: {keyword}"
                if any(k in keyword for k in ["маму", "родных"]):
                    default_time = "3d"
                elif any(k in keyword for k in ["http", "t.me"]):
                    default_time = "14d"
                break

    if reason:
        alert_text = (
            f"<@{MY_DISCORD_ID}> ⚠️ **Обнаружено нарушение правил!**\n"
            f"**Пользователь:** {message.author.mention}\n"
            f"**Канал:** {message.channel.mention}\n"
            f"**Причина:** `{reason}`\n"
            f"**Сообщение:** `{message.content}`\n"
            f"**Команда для мута:** `/tempmute {message.author.name} {default_time} {reason}`"
        )
        await message.channel.send(alert_text)

    await bot.process_commands(message)

def is_caps_violation(text: str) -> bool:
    if len(text) < 6:
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    uppercase_letters = [c for c in letters if c.isupper()]
    return (len(uppercase_letters) / len(letters)) >= 0.7

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Ошибка: Переменная DISCORD_TOKEN не найдена!")
    else:
        # Запускаємо веб-сервер в окремому потоці
        threading.Thread(target=run_web_server, daemon=True).start()
        # Запускаємо бота
        bot.run(BOT_TOKEN)
