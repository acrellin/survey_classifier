'''Assortment of utility functions.'''

import ast
import hashlib
import csv
import requests
from collections import defaultdict
from .config import cfg


__all__ = ['robust_literal_eval', 'prediction_to_csv', 'determine_model_ids']


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


def prediction_to_csv(pred, outpath=None):
    """Convert an `xarray.Dataset` prediction object's results to CSV.

    Parameters
    ----------
    pred : `xarray.Dataset`
        The `xarray.Dataset` object containing prediction data.
    outpath : str, optional
        Path to save CSV, if desired. Defaults to None.

    Returns
    -------
    list of lists of str (if `outpath` is None) or str
        If `outpath` is not None, returns a list of lists representing the
        tabular form of the prediction results, e.g.
        [['ts_name', 'target', 'prediction'],
         ['ts_1', 'Class_A', 'Class_A']]
        If `outpath` is specified, the data is saved in CSV format to the
        path specified, which is then returned.

    """
    head = ['ts_name']
    rows = []

    first_iter = True

    for tsname in pred.name.values:
        entry = pred.sel(name=tsname)
        row = [tsname]

        if 'target' in entry:
            row.append(entry.target.values.item())

            if first_iter:
                head.append('true_target')

        if 'class_label' in entry:
            for label, val in zip(entry.class_label.values,
                                  entry.prediction.values):
                row.extend([str(label), str(val)])

                if first_iter:
                    head.extend(['predicted_class', 'probability'])
        else:
            row.append(str(entry.prediction.values.item()))

            if first_iter:
                head.extend(['prediction'])

        rows.append(row)
        first_iter = False

    all_rows = [head]
    all_rows.extend(rows)

    if outpath:
        with open(outpath, 'w') as f:
            csv.writer(f).writerows(all_rows)
        return outpath
    else:
        return all_rows


def determine_model_ids(prediction_results):
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
        BLAH

    Returns
    -------
    pred_results_by_ts : dict
        Dictionary whose keys are TS names and values are weighted prediction
        results
    """
    ts_names = set([ts_name for model_id in sci_pred_results
                    for ts_name in sci_pred_results[model_id]])
    pred_results_by_ts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for model_id, results_dict in sci_pred_results.items():
        for ts_name, ts_results in results_dict.items():
            pred_results_by_ts[ts_name]['by_model'][model_id] = ts_results['prediction']
            for sci_class, prob in ts_results['prediction'].items():
                pred_results_by_ts[ts_name]['combined'][sci_class] += (
                    science_model_ids_and_probs[ts_name][model_id] * prob)
    return pred_results_by_ts
