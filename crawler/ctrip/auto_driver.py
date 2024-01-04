from selenium.webdriver import Safari, Edge, Firefox, Chrome, Ie, WebKitGTK, EdgeOptions, FirefoxOptions, ChromeOptions, IeOptions, WebKitGTKOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.options import ArgOptions
from typing import Type
from pathlib import Path

TESTED_DRIVER_CACHE_FILENAME = 'tested.cache'

OPTIONS_MAPPING = {
    Safari : None,
    Edge : EdgeOptions,
    Firefox : FirefoxOptions,
    Chrome : ChromeOptions,
    Ie : IeOptions,
    WebKitGTK : WebKitGTKOptions,
}

def get_cache_path() -> Path:
    return Path.cwd().joinpath(TESTED_DRIVER_CACHE_FILENAME)

def get_auto_driver(
        priorities = (Chrome, Firefox, Edge, Safari, Ie, WebKitGTK),
        using_cache = True
) -> tuple[Type[WebDriver], Type[ArgOptions]]:
    '''
    Test if the driver is available and works well. This examination takes time.

    Args:
        priorties: The priority sequence, webdrivers are tested in this queue.
        using_cache: Whether to use history cache, this will improve test speed.
    Returns:
        The first driver type that works well in the queue.
    '''
    def check(WebDriverType: Type[WebDriver]) -> bool:
        try:
            options = OPTIONS_MAPPING[WebDriverType]()
            options.add_argument('headless')
            driver = WebDriverType(options=options)
            driver.quit()
            return True
        except:
            return False

    unchecked = set(priorities)
    for WebDriverType in priorities:
        if WebDriverType not in unchecked and check(WebDriverType):
            return WebDriverType, OPTIONS_MAPPING[WebDriverType]
        unchecked.remove(WebDriverType)
    return None, None