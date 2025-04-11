from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from checkers_and_funcs import random_sleep, check_login, check_popup, check_unavailable, login, check_salter
from driver_setup import create_driver
from logger_config import setup_logger

logger = setup_logger(__name__)


def main():
    driver = create_driver()
    logger.info("🚗 Драйвер создан")

    login(driver)
    logger.info("🔐 Выполнен логин")

    if not check_unavailable(driver):
        logger.info("Проверяем логин...")
        if check_login(driver):
            logger.info("✅ Логин успешен")
        else:
            logger.warning("⚠️ Логин, возможно, не удался")

        random_sleep()

        try:
            driver.find_element(By.ID, value="advanced").send_keys(Keys.ENTER)
            logger.info("➡️ Перешли на страницу с записью")
        except Exception as e:
            logger.error(f"❌ Ошибка при переходе: {e}")
            driver.quit()
            return

        for salter_id in (1151, 1258):
            logger.info(f"🔎 Проверяем слот: {salter_id}")
            check_salter(driver, salter_id)
    else:
        logger.warning("🚫 Страница недоступна (unavailable)")

    driver.quit()
    logger.info("🛑 Драйвер закрыт")


if __name__ == "__main__":
    main()
