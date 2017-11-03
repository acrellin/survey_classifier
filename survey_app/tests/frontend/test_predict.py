import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import uuid
import time
import os
from os.path import join as pjoin
import numpy as np
import numpy.testing as npt
from survey_app.tests.fixtures import create_test_project


def _click_delete(driver):
    wait = WebDriverWait(driver, 15)
    elem = wait.until(EC.element_to_be_clickable(
        (By.PARTIAL_LINK_TEXT, 'Delete')))
    elem.click()


def _click_completed(driver):
    driver.wait_for_xpath("//td[contains(text(),'Completed')]", 10)
    wait = WebDriverWait(driver, 10)
    clickable_elem = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//td[contains(text(),'Completed')]")))
    clickable_elem.click()


def _add_prediction(proj_name, driver):
    driver.refresh()
    time.sleep(1)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_visible_text(proj_name)
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload Data & Predict').click()

    test_dataset_name =  str(uuid.uuid4())
    dataset_name = driver.find_element_by_css_selector('[name=datasetName]')
    dataset_name.send_keys(test_dataset_name)

    header_file = driver.find_element_by_css_selector('[name=headerFile]')
    header_file.send_keys(pjoin(os.path.dirname(os.path.dirname(__file__)), 'data',
                                'asas_training_subset_classes.dat'))

    tar_file = driver.find_element_by_css_selector('[name=tarFile]')
    tar_file.send_keys(pjoin(os.path.dirname(os.path.dirname(__file__)), 'data',
                             'asas_training_subset.tar.gz'))

    driver.find_element_by_class_name('btn-primary').click()

    driver.wait_for_xpath(
        "//div[contains(text(),'Successfully uploaded new dataset')]", 5)
    driver.wait_for_xpath(
        "//div[contains(text(),'Survey classifier model predictions begun')]", 5)
    driver.wait_for_xpath(
        "//div[contains(text(),'Science classifier model predictions begun')]", 20)
    driver.wait_for_xpath(
        "//div[contains(text(),'Science prediction completed')]", 30)

    try:
        driver.wait_for_xpath("//td[contains(text(),'Completed')]", 30)
    except:
        driver.save_screenshot("/tmp/pred_fail.png")
        raise


def _click_prediction_row(proj_name, driver):
    driver.refresh()
    time.sleep(0.5)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_visible_text(proj_name)
    driver.find_element_by_id('react-tabs-2').click()
    _click_completed(driver)


def _grab_pred_results_table_rows(driver, text_to_look_for):
    td = driver.wait_for_xpath(f"//td[contains(text(),'{text_to_look_for}')]",
                               30)
    tr = td.find_element_by_xpath('..')
    table = tr.find_element_by_xpath('..')
    rows = table.find_elements_by_tag_name('tr')
    return rows


def test_add_prediction(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        _click_delete(driver)


def test_survey_pred_results_table(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        _click_prediction_row(proj_name, driver)
        try:
            rows = _grab_pred_results_table_rows(
                driver, 'ASAS')
            for row in rows:
                probs = [float(v.text)
                         for v in row.find_elements_by_tag_name('td')[3::2]]
                assert sorted(probs, reverse=True) == probs
            driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise
        _click_delete(driver)


def test_science_pred_results_table(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        _click_prediction_row(proj_name, driver)
        try:
            rows = _grab_pred_results_table_rows(
                driver, 'Mira')
            for row in rows:
                probs = [float(v.text)
                         for v in row.find_elements_by_tag_name('td')[2::2]]
                assert sorted(probs, reverse=True) == probs
            driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
            driver.find_element_by_xpath("//td[contains(text(),'Mira')]")
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise
        _click_delete(driver)


def test_delete_prediction(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_visible_text(proj_name)
        driver.find_element_by_id('react-tabs-2').click()
        _click_completed(driver)
        _click_delete(driver)
        driver.implicitly_wait(10)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Prediction deleted')]")


def _click_download(proj_name, driver, idx):
    driver.refresh()
    time.sleep(0.5)
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_visible_text(proj_name)
    driver.find_element_by_id('react-tabs-2').click()
    _click_completed(driver)
    driver.implicitly_wait(10)
    dl_links = driver.find_elements_by_xpath("//a[contains(text(),'Download')]")
    elem = dl_links[idx]
    wait = WebDriverWait(driver, 10)
    clickable_elem = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'Download')]")))
    clickable_elem.click()
    time.sleep(0.5)


def test_download_survey_prediction_csv(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        _click_download(proj_name, driver, 0)
        assert os.path.exists('/tmp/survey_app_prediction_results.csv')
        try:
            text_lines = np.genfromtxt('/tmp/survey_app_prediction_results.csv',
                                       dtype='str')
            assert text_lines[0] == (
                'ts_name,label,ASAS,CoRoT,HATNet,Hipparcos,KELT,Kepler,'
                'LINEAR,OGLE-III,SuperWASP,TrES')

            line2_els = text_lines[1].split(',')
            assert all([el.replace('.', '').isdigit() for el in line2_els[2:]])
        finally:
            os.remove('/tmp/survey_app_prediction_results.csv')


def test_download_science_prediction_csv(driver):
    driver.get('/')
    with create_test_project(driver) as proj_name:
        _add_prediction(proj_name, driver)
        _click_download(proj_name, driver, 1)
        assert os.path.exists('/tmp/survey_app_prediction_results.csv')
        try:
            text_lines = np.genfromtxt('/tmp/survey_app_prediction_results.csv',
                                       dtype='str')
            assert text_lines[0] == (
                'ts_name,Beta_Cephei,Beta_Lyrae,Beta_Persei,'
                'ChemPeculiar,ClassT_Tauri,Classical_Cepheid,Delta_Scuti,'
                'Ellipsoidal,Herbig_AEBE,LSP,Mira,MultiMode_Cepheid,'
                'PopII_Cepheid,Pulsating_Be,RCB,RR_Lyrae_DM,RR_Lyrae_FM,'
                'RR_Lyrae_FO,RSG,RS_CVn,RV_Tauri,SARG_A,SARG_B,SX_Phe,'
                'S_Doradus,Semireg_PV,W_Ursae_Maj,Weakline_T_Tauri')

            line2_els = text_lines[1].split(',')
            assert all([el.replace('.', '').isdigit() for el in line2_els[1:]])
        finally:
            os.remove('/tmp/survey_app_prediction_results.csv')
