import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
import numpy as np
import numpy.testing as npt
from survey_app.tests.fixtures import create_test_project, create_test_dataset


def _add_prediction(proj_id, driver):
    driver.refresh()
    time.sleep(0.5)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Predict Targets').click()

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Model predictions begun')]")

    try:
        driver.implicitly_wait(30)
        status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
    except:
        driver.save_screenshot("/tmp/pred_fail.png")
        raise


def _click_prediction_row(proj_id, driver):
    driver.refresh()
    time.sleep(0.5)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()


def _grab_pred_results_table_rows(driver, text_to_look_for):
    driver.implicitly_wait(1)
    td = driver.find_element_by_xpath("//td[contains(text(),'{}')]".format(
        text_to_look_for))
    tr = td.find_element_by_xpath('..')
    table = tr.find_element_by_xpath('..')
    rows = table.find_elements_by_tag_name('tr')
    return rows


def test_add_prediction(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds:
        _add_prediction(p.id, driver)
        driver.find_element_by_partial_link_text('Delete').click()


def test_pred_results_table(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds:
        _add_prediction(p.id, driver)
        _click_prediction_row(p.id, driver)
        try:
            rows = _grab_pred_results_table_rows(driver, 'ASAS')
            for row in rows:
                probs = [float(v.text)
                         for v in row.find_elements_by_tag_name('td')[2::2]]
                assert sorted(probs, reverse=True) == probs
            driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise
        driver.find_element_by_partial_link_text('Delete').click()


def test_delete_prediction(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds:
        _add_prediction(p.id, driver)
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-4').click()
        driver.implicitly_wait(1)
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        time.sleep(0.2)
        driver.find_element_by_partial_link_text('Delete').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Prediction deleted')]")


def _click_download(proj_id, driver):
    driver.refresh()
    time.sleep(0.5)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-4').click()
    driver.implicitly_wait(1)
    driver.find_element_by_partial_link_text('Download').click()
    time.sleep(0.5)


def test_download_prediction_csv_class(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds:
        _add_prediction(p.id, driver)
        _click_download(p.id, driver)
        assert os.path.exists('/tmp/survey_app_prediction_results.csv')
        try:
            npt.assert_equal(
                np.genfromtxt('/tmp/survey_app_prediction_results.csv',
                              dtype='str'),
                ['ts_name,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability,predicted_class,probability',
       '257141,ASAS,0.814,CoRoT,0.0,HATNet,0.0,Hipparcos,0.0,KELT,0.0,Kepler,0.0,LINEAR,0.044,OGLE-III,0.119,SuperWASP,0.023,TrES,0.0',
       '247327,ASAS,0.846,CoRoT,0.0,HATNet,0.0,Hipparcos,0.001,KELT,0.0,Kepler,0.0,LINEAR,0.008,OGLE-III,0.142,SuperWASP,0.003,TrES,0.0',
       '243412,ASAS,0.773,CoRoT,0.0,HATNet,0.0,Hipparcos,0.0,KELT,0.0,Kepler,0.0,LINEAR,0.044,OGLE-III,0.162,SuperWASP,0.021,TrES,0.0',
       '235913,ASAS,0.794,CoRoT,0.0,HATNet,0.0,Hipparcos,0.002,KELT,0.0,Kepler,0.0,LINEAR,0.056,OGLE-III,0.127,SuperWASP,0.021,TrES,0.0',
       '232798,ASAS,0.765,CoRoT,0.0,HATNet,0.0,Hipparcos,0.001,KELT,0.0,Kepler,0.0,LINEAR,0.048,OGLE-III,0.166,SuperWASP,0.02,TrES,0.0',
       '224635,ASAS,0.732,CoRoT,0.0,HATNet,0.0,Hipparcos,0.001,KELT,0.0,Kepler,0.0,LINEAR,0.047,OGLE-III,0.201,SuperWASP,0.019,TrES,0.0',
       '217801,ASAS,0.751,CoRoT,0.0,HATNet,0.0,Hipparcos,0.001,KELT,0.0,Kepler,0.0,LINEAR,0.011,OGLE-III,0.23,SuperWASP,0.007,TrES,0.0'])
        finally:
            os.remove('/tmp/survey_app_prediction_results.csv')
