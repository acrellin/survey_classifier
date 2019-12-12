import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from survey_app.tests.fixtures import create_test_project

def DISABLED_test_tab_tooltips(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        driver.refresh()

        hover = ActionChains(driver).move_to_element(
            driver.find_element_by_id('react-tabs-0'))
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(text(),'Manage your projects')]"
        ).is_displayed()

        hover = ActionChains(driver).move_to_element(
            driver.find_element_by_id('react-tabs-2'))
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(text(),'Upload your light curves and generate predictions')]"
            ).is_displayed()


def DISABLED_test_file_upload_tooltips(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        driver.refresh()
        driver.find_element_by_id('react-tabs-2').click()
        driver.find_element_by_partial_link_text('Upload Data & Predict').click()

        header_file = driver.find_element_by_css_selector('[name=headerFile]')
        hover = ActionChains(driver).move_to_element(header_file)
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(.,'filename,target')]"
        ).is_displayed()

        tar_file = driver.find_element_by_css_selector('[name=tarFile]')
        hover = ActionChains(driver).move_to_element(tar_file)
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(.,'Each file in tarball should be formatted as follows')]"
        ).is_displayed()
