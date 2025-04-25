import time
import random
from pathlib import Path
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  # Импортируем для движения мыши

from config import BASE_URL, LOGIN, PASSWORD, USER_NAME
from telegram_sender import send_message, send_pic
from logger_config import setup_logger

logger = setup_logger(__name__)


def random_sleep(min_seconds=1, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))


def scroll_page(driver):
    """Функция для прокрутки страницы до конца"""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_sleep()


def move_mouse(driver):
    """Функция для эмуляции движения мыши"""
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    random_sleep()


def login(driver):
    logger.info("Открываем сайт и выполняем логин")
    driver.get(url=BASE_URL)

    try:
        # Прокручиваем страницу и эмулируем движение мыши
        scroll_page(driver)
        move_mouse(driver)

        email_element = driver.find_element(By.ID, value="login-email")
        email_element.clear()
        email_element.send_keys(LOGIN)
        random_sleep()

        password_element = driver.find_element(By.ID, value="login-password")
        password_element.clear()
        password_element.send_keys(PASSWORD)
        password_element.send_keys(Keys.RETURN)
        random_sleep()
    except Exception as e:
        logger.error(f"Ошибка при логине: {e}")


def check_unavailable(driver):
    try:
        if "unavailable" in driver.page_source.lower():
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
        return True
    except NoSuchElementException:
        return False
    except TimeoutException:
        logger.warning("⏱️ Истекло время ожидания появления элемента логина.")
        return False


def go_to_services(driver):
    try:
        # Прокручиваем страницу и эмулируем движение мыши
        scroll_page(driver)
        move_mouse(driver)

        driver.find_element(By.ID, value="advanced").send_keys(Keys.ENTER)
        logger.info("➡️ Перешли на страницу с записью")

    except Exception as e:
        logger.error(f"❌ Ошибка при переходе: {e}")
        driver.quit()
        return


def check_popup_or_site_down(driver, timeout=10):
    random_sleep()
    try:
        # Проверка на попап с сообщением об отсутствии слотов
        popup = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'Sorry, all appointments for this service are currently booked')]"
            ))
        )
        logger.info("⚠️ Всплывающее окно найдено: %s", popup.text)

        ok_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='ok']"))
        )
        ok_button.click()
        return True

    except TimeoutException:
        # Попап не появился — проверяем, не упал ли сайт
        page_text = driver.page_source.lower()
        for message in ("this site can’t be reached", "this site can't be reached", "runtime error"):
            if message in page_text:
                logger.error("🚫 Сайт недоступен: This site can't be reached")
                driver.quit()
                return True  # Считаем как критическую ошибку, аналогично попапу
        logger.info("✅ Всплывающее окно не появилось и сайт доступен.")
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке всплывающего окна или доступности сайта: {e}")
        return False


def check_salter(driver, param, timeout=5):
    try:
        # Прокручиваем страницу и эмулируем движение мыши
        scroll_page(driver)
        move_mouse(driver)

        logger.info(f"Проверка слота {param}...")
        selector = f'a[href="/Services/Booking/{param}"]'
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.send_keys(Keys.ENTER)
        random_sleep()

        if not check_popup_or_site_down(driver):
            logger.info("🟢 Возможно, появился слот!")
            driver.save_screenshot("slot.png")
            Path("slot.html").write_text(driver.page_source, encoding="utf-8")

            send_message(f"Возможно появился слот по этой ссылке {BASE_URL}/Services/Booking/{param}")
            send_pic("slot.png")
    except TimeoutException:
        logger.warning(f"⏱️ Элемент {param} не найден за {timeout} секунд.")
    except Exception as e:
        logger.error(f"Ошибка при проверке слота {param}: {e}")
