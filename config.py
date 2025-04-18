import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (логин, пароль)
load_dotenv()

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USER_NAME = os.getenv("USER_NAME")

BASE_URL = "https://prenotami.esteri.it"
COOKIES_FILE = "cookies.json"

