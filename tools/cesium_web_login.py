from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from baselayer.app import load_config


def cesium_web_login():
    driver = webdriver.PhantomJS()
    cfg = load_config()
    driver.get(cfg['cesium_app:url'])

    for i in range(5):
        try:
            driver.implicitly_wait(5)
            driver.find_element_by_xpath(
                '//*[contains(text(), "testuser@cesium-ml.org")]')
            break
        except NoSuchElementException:
            element = WebDriverWait(driver, 5).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/login/google-oauth2"]')))
            element.click()
    else:
        raise TimeoutException("cesium_web login failed")
    print('Successfully logged in to cesium_web')
    for cookie in driver.get_cookies():
        if cookie['name'] == 'user_id':
            with open(f'{cfg["paths:cesium_web_login_cookie_folder"]}/login.cookie',
                      'w') as f:
                f.write(cookie['value'])


if __name__ == '__main__':
    cesium_web_login()
