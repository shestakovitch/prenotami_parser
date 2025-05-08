import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (логин, пароль)
load_dotenv()

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USER_NAME = os.getenv("USER_NAME")
USER_ADDRESS = os.getenv("USER_ADDRESS")

SECOND_PERSON_SURNAME=os.getenv("SECOND_PERSON_SURNAME")
SECOND_PERSON_NAME=os.getenv("SECOND_PERSON_NAME")
SECOND_PERSON_DOB=os.getenv("SECOND_PERSON_DOB")
SECOND_PERSON_ADDRESS=os.getenv("SECOND_PERSON_ADDRESS")
SECOND_PERSON_STATUS=os.getenv("SECOND_PERSON_STATUS")

BASE_URL = "https://prenotami.esteri.it"
COOKIES_FILE = "cookies.json"

