from survey_app import util
import numpy.testing as npt
import pytest
import xarray as xr


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


def TODO_test_prediction_to_csv_xr_dataset():
    """Test util.prediction_to_csv with xr.Dataset input"""
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, model_type='LinearSGDClassifier') as m,\
         create_test_prediction(ds, m) as pred:
        pred = featureset.from_netcdf(pred.file.uri)
        assert util.prediction_to_csv(pred) ==\
            [['ts_name', 'true_class', 'prediction'],
             ['0', 'Mira', 'Mira'],
             ['1', 'Classical_Cepheid', 'Classical_Cepheid'],
             ['2', 'Mira', 'Mira'],
             ['3', 'Classical_Cepheid', 'Classical_Cepheid'],
             ['4', 'Mira', 'Mira']]


def test_prediction_to_csv_dict_no_class():
    """Test util.prediction_to_csv with dict input - no true class"""
    pred = {'0': {'combined': {'Mira': 0.9, 'Classical_Cepheid': 0.1}},
            '1': {'combined': {'Classical_Cepheid': 0.8, 'Mira': 0.2}}}
    assert util.prediction_results_to_csv(pred) ==\
        [['ts_name', 'predicted_class', 'probability', 'predicted_class',
          'probability'],
         ['0', 'Mira', '0.9', 'Classical_Cepheid', '0.1'],
         ['1', 'Classical_Cepheid', '0.8', 'Mira', '0.2']]


def test_prediction_to_csv_dict_with_class():
    """Test util.prediction_to_csv with dict input - with true class"""
    pred = {'0': {'target': 'Mira',
                  'combined': {'Mira': 0.9, 'Classical_Cepheid': 0.1}},
            '1': {'target': 'Classical_Cepheid',
                  'combined': {'Classical_Cepheid': 0.8, 'Mira': 0.2}}}
    assert util.prediction_results_to_csv(pred) ==\
        [['ts_name', 'true_class', 'predicted_class', 'probability', 'predicted_class',
          'probability'],
         ['0', 'Mira', 'Mira', '0.9', 'Classical_Cepheid', '0.1'],
         ['1', 'Classical_Cepheid', 'Classical_Cepheid', '0.8', 'Mira', '0.2']]
