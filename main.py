import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config import base_url, salter_1_url, salter_2_url

# Читаем переменные окружения
load_dotenv()
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")


def main():
    """Функция логинится по ссылке base_url"""
    driver = webdriver.Chrome()
    driver.get(url=base_url)

    # Вводим логин
    email_element = driver.find_element(By.ID, value="login-email")
    email_element.clear()
    email_element.send_keys(LOGIN)

    # Вводим пароль
    password_element = driver.find_element(By.ID, value="login-password")
    password_element.clear()
    password_element.send_keys(PASSWORD)
    password_element.send_keys(Keys.RETURN)

    driver.get(url=salter_1_url)

if __name__ == "__main__":
    main()
