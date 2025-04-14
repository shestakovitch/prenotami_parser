import requests
from config import BOT_TOKEN, CHAT_ID


def _post_to_telegram(method, data=None, files=None):
    """
    Универсальная функция для отправки запросов в Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    res = requests.post(url, data=data, files=files)

    if res.status_code == 200:
        print("✅ Успешно отправлено")
    else:
        print(f"❌ Ошибка: {res.status_code}, {res.text}")

    return res


def send_message(message):
    """
    Отправляет текстовое сообщение в Telegram.
    """
    return _post_to_telegram("sendMessage", data={
        "chat_id": CHAT_ID,
        "text": message
    })


def send_pic(pic_path):
    """
    Отправляет фото в Telegram.
    """
    with open(pic_path, "rb") as photo:
        return _post_to_telegram("sendPhoto", data={
            "chat_id": CHAT_ID
        }, files={
            "photo": photo
        })
