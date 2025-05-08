import time
import random
import threading
import sys
from pathlib import Path
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains  # Импортируем для движения мыши

from config import BASE_URL, LOGIN, PASSWORD, USER_NAME, USER_ADDRESS, SECOND_PERSON_SURNAME, SECOND_PERSON_NAME, \
    SECOND_PERSON_ADDRESS, SECOND_PERSON_DOB, SECOND_PERSON_STATUS
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


def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))


def login(driver):
    logger.info("Открываем сайт и выполняем логин")
    driver.get(url=BASE_URL)

    try:
        scroll_page(driver)
        move_mouse(driver)

        # Клик по полю email мышью
        email_element = driver.find_element(By.ID, value="login-email")
        ActionChains(driver).move_to_element(email_element).click().perform()
        human_typing(email_element, LOGIN)
        random_sleep(1, 2)

        # Клик по полю password мышью
        password_element = driver.find_element(By.ID, value="login-password")
        ActionChains(driver).move_to_element(password_element).click().perform()
        human_typing(password_element, PASSWORD)
        random_sleep(1, 2)

        # Клик по кнопке входа мышью
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        ActionChains(driver).move_to_element(login_button).click().perform()
        time.sleep(5)

    except Exception as e:
        logger.error(f"Ошибка при логине: {e}")
        return False


def check_unavailable_or_verification_error(driver):
    """
        Проверяет заголовок страницы и URL на наличие признаков ошибки.
        При обнаружении логирует, завершает драйвер и возвращает True.
        """
    try:
        if "unavailable" in driver.title.lower():
            logger.error(f"Обнаружена ошибка: unavailable")
            driver.quit()
            return True
        if "error" in driver.current_url.lower():
            logger.error(f"Обнаружена ошибка: An error occurred while processing the request")
            time.sleep(300)
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

            # 1. Выбор "Kolektivna rezervacija" по тексту label
            label_booking = driver.find_element(By.XPATH, "//label[contains(text(), 'Vrsta rezervacije')]")
            select_booking = label_booking.find_element(By.XPATH, "./following-sibling::select")
            Select(select_booking).select_by_visible_text("Kolektivna rezervacija")

            # Подождем, пока появится блок с выбором количества
            time.sleep(1)

            # 2. Выбор "1" в "Broj dodatnih podnosilaca zahteva"
            label_companions = driver.find_element(By.XPATH,
                                                   "//label[contains(text(), 'Broj dodatnih podnosilaca zahteva')]")
            select_companions = label_companions.find_element(By.XPATH, "./following-sibling::select")
            Select(select_companions).select_by_value("1")

            # Drugo/a državljanstvo
            input_citizenship = driver.find_element(By.ID, "DatiAddizionaliPrenotante_0___testo")
            input_citizenship.clear()
            input_citizenship.send_keys("Russia")

            # Razlog Boravka
            select_reason = Select(driver.find_element(By.ID, "ddls_1"))
            select_reason.select_by_visible_text("Turizam")

            # Adresa prebivališta
            input_address = driver.find_element(By.ID, "DatiAddizionaliPrenotante_2___testo")
            input_address.clear()
            input_address.send_keys(USER_ADDRESS)

            # показать скрытые поля, если необходимо
            driver.execute_script("document.getElementById('ifMultiple').style.display = 'block';")
            driver.execute_script("document.getElementById('divCompanion_0').style.display = 'block';")

            # заполнить фамилию, имя, дату рождения
            driver.find_element(By.ID, "Accompagnatori_0__CognomeAccompagnatore").send_keys(SECOND_PERSON_SURNAME)
            driver.find_element(By.ID, "Accompagnatori_0__NomeAccompagnatore").send_keys(SECOND_PERSON_NAME)
            driver.find_element(By.ID, "Accompagnatori_0__DataNascitaAccompagnatore").send_keys(SECOND_PERSON_DOB)

            # выбрать "Srodstvo" = Supružnik
            relation_select = Select(driver.find_element(By.ID, "ddlRelation_0"))
            relation_select.select_by_visible_text(SECOND_PERSON_STATUS)

            # заполнить "Drugo/a državljanstvo"
            driver.find_element(By.NAME, "Accompagnatori[0].DatiAddizionaliAccompagnatore[0]._testo").send_keys(
                "Russia")

            # выбрать "Razlog Boravka" = Turizam
            razlog_select = Select(driver.find_element(By.ID, "ddlsAcc_1"))  # предполагаемый ID
            razlog_select.select_by_visible_text("Turizam")

            # заполнить "Adresa prebivališta"
            driver.find_element(By.NAME, "Accompagnatori[0].DatiAddizionaliAccompagnatore[2]._testo").send_keys(
                SECOND_PERSON_ADDRESS)

            otp_button = driver.find_element(By.ID, "otp-send").click()

            Path("slot.html").write_text(driver.page_source, encoding="utf-8")

            driver.save_screenshot("slot.png")
            send_message(f"Возможно появился слот по этой ссылке {BASE_URL}/Services/Booking/{param}")
            send_pic("slot.png")

            # Таймер на случай, если пользователь не закроет вручную
            def auto_exit():
                logger.warning("\n⏰ Время вышло. Скрипт завершает работу.")
                sys.exit()

            timer = threading.Timer(600, auto_exit)  # 10 минут
            timer.start()

            # Передача управления пользователю
            try:
                input(
                    "⏸ Слот найден. Управление передано пользователю. Нажмите Enter, "
                    "чтобы завершить скрипт вручную раньше таймера...\n")
                timer.cancel()
                logger.info("✅ Скрипт завершён вручную.")
                sys.exit()
            except KeyboardInterrupt:
                logger.warning("\n🚪 Принудительное завершение.")
                sys.exit()

    except TimeoutException:
        logger.warning(f"⏱️ Элемент {param} не найден за {timeout} секунд.")
    except Exception as e:
        logger.error(f"Ошибка при проверке слота {param}: {e}")
