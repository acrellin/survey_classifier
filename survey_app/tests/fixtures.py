'''Assortment of fixtures for use in test modules.'''

import uuid
import os
from os.path import join as pjoin
from contextlib import contextmanager
from survey_app import models as m
import shutil
import peewee
import joblib
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from tempfile import mkdtemp


TMP_DIR = mkdtemp()


@contextmanager
def create_test_project(driver):
    """Create test project and yield name, then delete."""
    driver.get("/")
    driver.implicitly_wait(1)
    driver.find_element_by_partial_link_text('Or click here to add a new one').click()

    project_name_field = driver.find_element_by_css_selector('[name=projectName]')
    proj_name = str(uuid.uuid4())
    project_name_field.send_keys(proj_name)
    project_desc = driver.find_element_by_css_selector('[name=projectDescription]')
    project_desc.send_keys("Test Description")

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Added new project')]")
    try:
        yield proj_name
    finally:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_visible_text(proj_name)
        driver.find_element_by_partial_link_text('Delete Project').click()
