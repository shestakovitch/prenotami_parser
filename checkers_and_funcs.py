import time
import random
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL, LOGIN, PASSWORD, USER_NAME
from telegram_sender import send_message, send_pic
from logger_config import setup_logger

logger = setup_logger(__name__)


def random_sleep(min_seconds=1, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))


def login(driver):
    logger.info("Открываем сайт и выполняем логин")
    driver.get(url=BASE_URL)

    try:
        email_element = driver.find_element(By.ID, value="login-email")
        email_element.clear()
        email_element.send_keys(LOGIN)
        random_sleep()

        password_element = driver.find_element(By.ID, value="login-password")
        password_element.clear()
        password_element.send_keys(PASSWORD)
        password_element.send_keys(Keys.RETURN)
        random_sleep()
        logger.info("Логин выполнен")
    except Exception as e:
        logger.error(f"Ошибка при логине: {e}")


def check_unavailable(driver):
    try:
        if "unavailable" in driver.page_source.lower():
            driver.save_screenshot("unavailable.png")
            logger.warning("⚠️ Страница недоступна (unavailable)")
            driver.quit()
            return True
    except Exception as e:
        logger.error(f"Ошибка при проверке доступности страницы: {e}")
    return False


def check_login(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//figure[@class='main-nav__avatar']//figcaption[contains(text(), '{USER_NAME}')]"))
        )
        logger.info("✅ Успешный вход в систему!")
        return True
    except NoSuchElementException:
        logger.warning("⚠️ Не удалось найти имя пользователя.")
        return False
    except TimeoutException:
        logger.warning("⏱️ Истекло время ожидания появления элемента логина.")
        return False


def check_popup(driver, timeout=10):
    random_sleep()
    try:
        # Ждём появления текста во всплывающем окне
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'Sorry, all appointments for this service are currently booked')]"
            ))
        )
        logger.info("⚠️ Всплывающее окно найдено: %s", popup.text)

        # Ждём появления и кликабельности кнопки OK
        ok_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='ok']"))
        )
        ok_button.click()
        return True

    except TimeoutException:
        driver.save_screenshot("slot.png")
        logger.info("✅ Всплывающее окно не появилось.")
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке всплывающего окна: {e}")
        return False


def check_salter(driver, param, timeout=5):
    try:
        logger.info(f"Проверка слота {param}...")
        selector = f'a[href="/Services/Booking/{param}"]'
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.send_keys(Keys.ENTER)
        random_sleep()

        if not check_popup(driver):
            logger.info("🟢 Возможно, появился слот!")
            driver.save_screenshot("slot.png")
            send_message(f"Возможно появился слот по этой ссылке {BASE_URL}/Services/Booking/{param}")
            send_pic("slot.png")
    except TimeoutException:
        logger.warning(f"⏱️ Элемент {param} не найден за {timeout} секунд.")
    except Exception as e:
        logger.error(f"Ошибка при проверке слота {param}: {e}")
