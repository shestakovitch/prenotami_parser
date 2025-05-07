from selenium import webdriver


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Создаёт экземпляр Selenium Chrome WebDriver.

    :param headless: Запускать ли браузер в headless-режиме.
    :return: webdriver.Chrome
    """

    # Устанавливаем пользовательский агент (user-agent), чтобы притвориться обычным браузером
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    )

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Если headless=True, то включаем безголовый режим
    if headless:
        options.add_argument("--headless")

    # Создаём экземпляр Chrome WebDriver с заданными опциями
    driver = webdriver.Chrome(options=options)

    # Выполняем JavaScript до загрузки страницы, чтобы скрыть автоматизацию
    # Снимаем флаг navigator.webdriver — один из признаков использования Selenium
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )

    return driver
