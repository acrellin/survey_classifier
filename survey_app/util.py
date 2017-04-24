'''Assortment of utility functions.'''

import ast
import hashlib
import csv
import requests
from collections import defaultdict
from operator import itemgetter
import pandas as pd
from .config import cfg


__all__ = ['robust_literal_eval', 'prediction_results_to_csv',
           'determine_model_ids', 'aggregate_pred_results_by_ts']


def robust_literal_eval(val):
    """Call `ast.literal_eval` without raising `ValueError`.

    Parameters
    ----------
    val : str
        String literal to be evaluated.

    Returns
    -------
    Output of `ast.literal_eval(val)', or `val` if `ValueError` was raised.

    """
    try:
        return ast.literal_eval(val)
    except ValueError:
        return val


def determine_model_ids(prediction_results):
    """Parse results and group model IDs and probabilities by time series name.

    Parameters
    ----------
    prediction_results : dict
        Dictionary whose keys are time series names, and values are dictionaries
        containing the results as returned by `cesium_web`.

    Returns
    -------
    ts_name_model_ids_and_probs : dict
        Dictionary whose keys are TS names and values are dictionaries of
        model IDs and their associated probabilities, respectively,
        e.g. {'ts_1': {mdl_id_1: mdl_id_1_prob, ...}, ...}.
    """
    model_name_to_id = {model['name']: model['id'] for model in
                        requests.get('{}/models'.format(cfg['cesium_app']['url']))
                        .json()['data'] if model['project'] ==
                        cfg['cesium_app']['survey_classifier_project_id']}
    ts_name_model_ids_and_probs = {}
    for ts_name in prediction_results:
        ts_name_model_ids_and_probs[ts_name] = {
            model_name_to_id[model_name]: prob for model_name, prob in
            prediction_results[ts_name]['prediction'].items() if prob >= 0.05}
    # Normalize probabilities
    for ts_name in ts_name_model_ids_and_probs:
        old_sum = sum(ts_name_model_ids_and_probs[ts_name].values())
        ts_name_model_ids_and_probs[ts_name] = {
            model_id: old_prob / old_sum
            for model_id, old_prob in ts_name_model_ids_and_probs[ts_name].items()}
    return ts_name_model_ids_and_probs


def aggregate_pred_results_by_ts(sci_pred_results, science_model_ids_and_probs):
    """Map model-wise prediction results to TS-wise results.

    Parameters
    ----------
    sci_pred_results : dict
        Dictionary whose keys are cesium_web model IDs, and values are
        dictionaries containing prediction results for that model.
    science_model_ids_and_probs : dict
        Dictionary whose primary keys are TS names, and values are dicts with
        associated model IDs and probabilities as keys and values, respectively,
        e.g. {'ts_1': {mdl_id_1: mdl_id_1_prob, mdl_id_2: mdl_id_2_prob}, ...}

    Returns
    -------
    pred_results_by_ts : dict
        Dictionary whose keys are TS names and values are dictionaries
        containing both weighted prediction results dicts (class names as keys,
        combined probabilities as values) accessed by the 'combined' key, and
        model-wise results ('by_model'). See below for example structure.
        E.g. {'ts_1': {'by_model': {'model_1': {'class_1': 0.6, 'class_2': 0.1, ...},
                                    'model_2': {'class_1': 0.3, 'class_2': 0.4, ...},
                                    ...},
                       'combined': {'class_1': 0.5, 'class_2': 0.2, ...}},
              ...}
    """
    model_id_to_name = {model['id']: model['name'] for model in
                        requests.get('{}/models'.format(cfg['cesium_app']['url']))
                        .json()['data'] if model['project'] ==
                        cfg['cesium_app']['survey_classifier_project_id']}
    ts_names = set([ts_name for model_id in sci_pred_results
                    for ts_name in sci_pred_results[model_id]])
    pred_results_by_ts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for model_id, results_dict in sci_pred_results.items():
        for ts_name, ts_results in results_dict.items():
            pred_results_by_ts[ts_name]['by_model'][
                model_id_to_name[model_id]] = ts_results['prediction']
            for sci_class, prob in ts_results['prediction'].items():
                pred_results_by_ts[ts_name]['combined'][sci_class] += (
                    science_model_ids_and_probs[ts_name][model_id] * prob)
    return pred_results_by_ts
