from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Создаёт экземпляр Selenium Chrome WebDriver.
    """
    options = Options()
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-popup-blocking")

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                    const newProto = navigator.__proto__;
                    delete newProto.webdriver;
                    navigator.__proto__ = newProto;
                """
        }
    )

    return driver
