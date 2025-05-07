from selenium import webdriver
import time

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

    # # Первый заход на сайт — чтобы Selenium мог добавить куки
    # driver.get("https://prenotami.esteri.it/")
    # time.sleep(3)  # подождать, чтобы сайт успел загрузиться

    # # Заранее полученные cookies
    # cookies = [
    #     {"name": "BIGipServerpool_prenotami.esteri.it", "value": "rd21o00000000000000000000ffffc0a806e8o443"},
    #     {"name": "_pk_id.E1e0Ge2p6l.5f67", "value": "1de57a82bf5583a2.1743603417."},
    #     {"name": "__RequestVerificationToken", "value": "3DT--fbLZSlvh5Q6bXzPKUufM6Vg8bLTwHfXBmk_p30eycdlH1zkVZ1mUWGUO-q7-aTeCi3HQItTKXcoY7SIojgS8VodETW85mt0ik3U-fY1"},
    #     {"name": "ASP.NET_SessionId", "value": "ssm0uvyptevkcdnwrknj1osx"},
    #     {"name": "_pk_ref.E1e0Ge2p6l.5f67", "value": '["","","1746634098","https://ambbelgrado.esteri.it/"]'},
    #     {"name": "_pk_ses.E1e0Ge2p6l.5f67", "value": "1"},
    #     {"name": "Lyp1CWKh", "value": "AxJlgauWAQAA6KPY5k4ru_QpXQFZ9oN5xWOdHz3vLcXy7_rJf6xzy6h36cerAVd0pCmucohSwH9eCOfvosJeCA=="},
    #     {"name": "_Culture", "value": "23"},
    #     {"name": ".cookie.", "value": "r7TnSOkjv47Q7bFY4I561e9kFujdgAUJsMlfEi4IPXBIitaE13DYnr86MN4ojoSIEZnjPHWSv-5O_cFnnzgMAx4r1L5ltKnc1WrZqWNTPuPFtTP17fzeBOBKCm4A3W4RcXP3cPC60PA6R64ZfB396OJhSiAUC2zsK69SRAbiv-2dKtQO9p_U3yehOzsbfIOuBpZskT8gcQekFM8S0nx-uKAM6JBr3Abu32VSYoTuma0XPm8QMa5U342KEd3PNIw1h9KvFppmZrWysj4azmkZKG7zICVlR7mwwwY3ypMgUo_bWvX7WuBqP_VsDFR750GJkr89-ccphF-vR2t1nQbhq5nKZR65yMrI8wK0H34a1Uqj6ctF6pXuIqHWo2qBTStcrfrItiAgmA3ittAxzHG7CGktoJfv2UaQj_SSI0m304IcFkbHJIHqPOpdA1XD8bza101k6OpMm_nbfgRDNKDPAMDS3nYRtl1G076ctSg9NoE9AFCpxxOL4MhlClroC1DCqDOZ-WbG2TW8F9PyAxtHYgKsDfg0SOVHtpFEmK9Lfg3532rNO5-bHd3quTZ0e0KywA45BpBMmxIRCbPADRvGqW_Ms5E-tGlPVqlabXAl9E8"},
    #     {"name": "TS01a5ae52030", "value": "01574ed751cc79261fd90755e4f8b3f42c6513230e3d6b6944fd899b9e827808f15a1e35a7419dd63fc7525cf775908ce3fe8380b4"},
    #     {"name": "OClmoOot", "value": "A5W23PaVAQAADw_ANBqLwEs9cOpNQTjp9NXvEj1reoF_35mt2tc5NNkaQRQcAVd0oiuuckX5wH9eCOfvosJeCA|1|0|d93681c53d60568e110aaa9b77f95e1824c5398c"},
    #     {"name": "TS01a5ae52", "value": "01a6f07363666b26ee530dec21aa79bb45378ffbacd8f2a426ba525c91315580cb79fc9421db5865fcc02f884a9f05a9542167b6afad59439c49fbc60deb64568d31f54b0625a75c6b66480c5ed614d6ff617dc4596a0f4b81ed1367c9648042af139ba7032035eea0acbb3f39f8b9d797f08b9d5377532b95b0ae36a731da046f42a1047b003fc89c584df8300c2d2d433fa371b2acec18748820e98cea12a3e99351f216"},
    #     {"name": "TS85ef4567027", "value": "085c4e0199ab2000e460a927a2f42a6bc3f09abe10e57c1be9c47724066db2402bf4ad5bf9b8015b08e6d2e6cb113000f8b41d4e4eec846201623e7b5684d4a79292819b835663893b1968500054dfaa06b737bcc10ace92c850ee0681a256f5"},
    # ]

    # # Добавляем cookies
    # for cookie in cookies:
    #     try:
    #         driver.add_cookie(cookie)
    #     except Exception as e:
    #         print(f"Не удалось добавить cookie: {cookie['name']}: {e}")

    driver.get("https://bot.sannysoft.com/")

    return driver
