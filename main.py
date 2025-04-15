from checkers_and_funcs import random_sleep, check_login, check_unavailable, login, go_to_services, check_salter
from driver_setup import create_driver
from logger_config import setup_logger

logger = setup_logger(__name__)


def main():
    driver = create_driver()
    logger.info("🚗 Драйвер создан")

    login(driver)

    if not check_unavailable(driver):
        logger.info("Проверяем логин...")
        if check_login(driver):
            logger.info("🔐Логин выполнен")
        else:
            logger.warning("⚠️ Не удалось найти имя пользователя.")
            driver.quit()
            logger.info("🛑 Драйвер закрыт")
            return

        random_sleep()
        go_to_services(driver)

        for salter_id in (1151, 1258):
            logger.info(f"🔎 Проверяем слот: {salter_id}")
            check_salter(driver, salter_id)
    else:
        logger.warning("🚫 Страница недоступна (unavailable)")

    driver.quit()
    logger.info("🛑 Драйвер закрыт")


if __name__ == "__main__":
    main()
