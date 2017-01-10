from survey_app import util
import numpy.testing as npt
import pytest
import xarray as xr
import os
from operator import itemgetter
from collections import OrderedDict


def test_robust_literal_eval():
    """Test util.robust_literal_eval"""
    params = {"n_estimators": "1000",
              "max_features": "auto",
              "min_weight_fraction_leaf": "0.34",
              "bootstrap": "True",
              "class_weight": "{'a': 0.2, 'b': 0.8}",
              "max_features2": "[150.3, 20, 'auto']"}
    expected = {"n_estimators": 1000,
                "max_features": "auto",
                "min_weight_fraction_leaf": 0.34,
                "bootstrap": True,
                "class_weight": {'a': 0.2, 'b': 0.8},
                "max_features2": [150.3, 20, "auto"]}
    params = {k: util.robust_literal_eval(v) for k, v in params.items()}
    npt.assert_equal(params, expected)


def test_prediction_results_to_csv_xr_dataset():
    """Test util.prediction_results_to_csv with xr.Dataset input"""
    with xr.open_dataset(os.path.join(os.path.dirname(__file__),
                                       'data', 'test_pred.nc')) as pred:
        assert util.prediction_results_to_csv(pred) ==\
            [['ts_name', 'predicted_class', 'probability', 'predicted_class',
              'probability', 'predicted_class', 'probability', 'predicted_class',
              'probability', 'predicted_class', 'probability', 'predicted_class',
              'probability', 'predicted_class', 'probability', 'predicted_class',
              'probability', 'predicted_class', 'probability', 'predicted_class',
              'probability'],
             ['257141', 'ASAS', '0.814', 'OGLE-III', '0.119', 'LINEAR', '0.044',
              'SuperWASP', '0.023', 'CoRoT', '0.0', 'HATNet', '0.0', 'Hipparcos',
              '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['247327', 'ASAS', '0.846', 'OGLE-III', '0.142', 'LINEAR', '0.008',
              'SuperWASP', '0.003', 'Hipparcos', '0.001', 'CoRoT', '0.0',
              'HATNet', '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['243412', 'ASAS', '0.773', 'OGLE-III', '0.162', 'LINEAR', '0.044',
              'SuperWASP', '0.021', 'CoRoT', '0.0', 'HATNet', '0.0', 'Hipparcos',
              '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['235913', 'ASAS', '0.794', 'OGLE-III', '0.127', 'LINEAR', '0.056',
              'SuperWASP', '0.021', 'Hipparcos', '0.002', 'CoRoT', '0.0',
              'HATNet', '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['232798', 'ASAS', '0.765', 'OGLE-III', '0.166', 'LINEAR', '0.048',
              'SuperWASP', '0.02', 'Hipparcos', '0.001', 'CoRoT', '0.0',
              'HATNet', '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['224635', 'ASAS', '0.732', 'OGLE-III', '0.201', 'LINEAR', '0.047',
              'SuperWASP', '0.019', 'Hipparcos', '0.001', 'CoRoT', '0.0',
              'HATNet', '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0'],
             ['217801', 'ASAS', '0.751', 'OGLE-III', '0.23', 'LINEAR', '0.011',
              'SuperWASP', '0.007', 'Hipparcos', '0.001', 'CoRoT', '0.0',
              'HATNet', '0.0', 'KELT', '0.0', 'Kepler', '0.0', 'TrES', '0.0']]


def test_prediction_results_to_csv_dict_no_class():
    """Test util.prediction_results_to_csv with dict input - no true class"""
    pred = OrderedDict(
        [['0', {'combined': {'Mira': 0.9, 'Classical_Cepheid': 0.1}}],
         ['1', {'combined': {'Classical_Cepheid': 0.8, 'Mira': 0.2}}]])
    assert util.prediction_results_to_csv(pred) ==\
        [['ts_name', 'predicted_class', 'probability', 'predicted_class',
          'probability'],
         ['0', 'Mira', '0.9', 'Classical_Cepheid', '0.1'],
         ['1', 'Classical_Cepheid', '0.8', 'Mira', '0.2']]


def test_prediction_results_to_csv_dict_with_class():
    """Test util.prediction_results_to_csv with dict input - with true class"""
    pred = OrderedDict(
        [['0', {'target': 'Mira',
                'combined': {'Mira': 0.9, 'Classical_Cepheid': 0.1}}],
         ['1', {'target': 'Classical_Cepheid',
                'combined': {'Classical_Cepheid': 0.8, 'Mira': 0.2}}]])
    assert util.prediction_results_to_csv(pred) ==\
        [['ts_name', 'true_class', 'predicted_class', 'probability', 'predicted_class',
          'probability'],
         ['0', 'Mira', 'Mira', '0.9', 'Classical_Cepheid', '0.1'],
         ['1', 'Classical_Cepheid', 'Classical_Cepheid', '0.8', 'Mira', '0.2']]
