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

    # Добавляем дополнительные опции для обхода блокировок
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-3d-apis")

    # Отключаем WebDriver флаги
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Если headless=True, то включаем безголовый режим
    if headless:
        options.add_argument("--headless")

    # Создаём экземпляр Chrome WebDriver с заданными опциями
    driver = webdriver.Chrome(options=options)

    # # Выполняем JavaScript до загрузки страницы, чтобы скрыть автоматизацию
    # Снимаем флаг navigator.webdriver — один из признаков использования Selenium
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = { runtime: {} };
            """
        }
    )

    return driver
