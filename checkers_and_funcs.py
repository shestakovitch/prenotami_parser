import time
import random
from datetime import datetime
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, LOGIN, PASSWORD
from telegram_sender import send_message, send_pic


def random_sleep(min_seconds=1, max_seconds=5):
    """
    Делает паузу на случайное количество секунд между действиями.
    Используется для имитации поведения пользователя и обхода антибот-защиты.
    :param min_seconds: минимальное количество секунд ожидания
    :param max_seconds: максимальное количество секунд ожидания
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def login(driver):
    """
    Выполняет вход на сайт с использованием логина и пароля из .env.
    Вводит email и пароль, затем имитирует нажатие Enter.
    :param driver: экземпляр Selenium WebDriver
    """
    driver.get(url=BASE_URL)

    # Находим и заполняем поле логина
    email_element = driver.find_element(By.ID, value="login-email")
    email_element.clear()
    email_element.send_keys(LOGIN)
    random_sleep()

    # Находим и заполняем поле пароля
    password_element = driver.find_element(By.ID, value="login-password")
    password_element.clear()
    password_element.send_keys(PASSWORD)
    password_element.send_keys(Keys.RETURN)  # Имитируем нажатие Enter
    random_sleep()


def check_unavailable(driver):
    """
    Проверяет наличие текста 'unavailable' на странице (индикатор недоступности сервиса).
    Если страница недоступна, делает скриншот и завершает работу драйвера.
    :param driver: экземпляр Selenium WebDriver
    :return: True — если страница недоступна, False — если всё в порядке
    """
    try:
        if "unavailable" in driver.page_source.lower():
            driver.save_screenshot(f"unavailable.png")
            print("⚠️ Страница недоступна (unavailable).")
            driver.quit()
            return True
    except Exception as e:
        print(f"Ошибка при проверке страницы: {e}")
    return False


def check_login(driver):
    """
    Проверяет, успешно ли выполнен вход в систему по наличию имени пользователя на странице.
    :param driver: экземпляр Selenium WebDriver
    :return: True — если вход успешен, False — если имя пользователя не найдено
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//figure[@class='main-nav__avatar']//figcaption[contains(text(), 'Anna Morozyuk')]"))
        )
        print("Успешный вход в систему!")
        return True
    except NoSuchElementException:
        print("Не удалось найти имя пользователя. Возможно, вход не был выполнен.")
        return False


def check_popup(driver):
    """
    Проверяет, появилось ли всплывающее окно с сообщением об отсутствии слотов.
    Если окно найдено — выводит текст, нажимает кнопку OK и возвращает True.
    Если окно не найдено — делает скриншот страницы и возвращает False.
    :param driver: экземпляр Selenium WebDriver
    :return: True — если окно найдено, False — если его нет
    """
    random_sleep()

    try:
        popup = driver.find_element(By.XPATH,
                                    "//*[contains(text(), 'Sorry, all appointments for this service are currently booked')]")
        print("⚠️ Всплывающее окно найдено:")
        print(popup.text)

        ok_button = driver.find_element(By.XPATH, "//button[text()='ok']")
        ok_button.click()
        return True
    except NoSuchElementException:
        driver.save_screenshot(f"slot.png")
        print("✅ Всплывающее окно не появилось.")
        return False


def check_salter(driver, param, timeout=5):
    """
    Проверяет наличие слота для записи по заданному идентификатору (1151, 1258 и т.д.).
    Переходит по ссылке и вызывает проверку всплывающего окна.
    :param driver: экземпляр Selenium WebDriver
    :param param: числовой идентификатор слота (например 1151)
    :param timeout: время ожидания появления элемента на странице
    """
    try:
        selector = f'a[href="/Services/Booking/{param}"]'
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.send_keys(Keys.ENTER)
        random_sleep()

        popup_found = check_popup(driver)
        if not popup_found:
            # Если всплывающее окно не найдено — возможно, появился слот!
            print("Возможно, появился слот!")
            send_message(f"Возможно появился слот по этой ссылке {BASE_URL}/Services/Booking/{param}")
            send_pic()

    except TimeoutException:
        print(f"Сайт не отвечает или элемент {param} не найден в течение {timeout} секунд.")
