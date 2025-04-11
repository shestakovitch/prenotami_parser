from selenium import webdriver


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Создаёт и настраивает экземпляр Selenium WebDriver для браузера Chrome.

    Параметры:
    ----------
    headless : bool, optional (по умолчанию False)
        Если True — браузер запускается в фоновом (безголовом) режиме, без отображения графического интерфейса.
        Это удобно для серверных задач и автоматизации без участия пользователя.

    Возвращает:
    -----------
    webdriver.Chrome
        Объект Chrome WebDriver с заданными настройками.

    Особенности реализации:
    -----------------------
    - Устанавливается кастомный User-Agent для эмуляции настоящего пользователя.
      Это помогает обходить базовые антибот-защиты, определяющие "ненастоящие" браузеры.

    - Добавляется JavaScript-хак через Chrome DevTools Protocol (CDP),
      который убирает флаг "navigator.webdriver" в окне браузера.
      По умолчанию этот флаг установлен в `true` в управляемом Selenium браузере,
      и многие сайты проверяют его, чтобы определить, используется ли автоматизация.

    - Поддерживается headless-режим через опцию `--headless`.

    Пример использования:
    ---------------------
        driver = create_driver(headless=True)
        driver.get("https://example.com")
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
