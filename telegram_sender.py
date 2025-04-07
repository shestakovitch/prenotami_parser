import os
import requests
from dotenv import load_dotenv

# Читаем переменные окружения
load_dotenv()

def send_message(message):
    """
    Отправляет сообщение о том что на сайте нет ошибки
    """
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    params = {
        'chat_id': CHAT_ID,
        'text': message
    }

    res = requests.post(url, params=params)

    if res.status_code == 200:
        print("Сообщение отправлено")
    else:
        print(f"Error: {res.status_code}, {res.text}")

    return res

send_message("Привет! Аня")