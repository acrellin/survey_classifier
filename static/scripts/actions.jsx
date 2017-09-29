// Action format:
// https://github.com/acdlite/flux-standard-action

import { reset as resetForm } from 'redux-form';
// import * as API from './API';

export const HYDRATE = 'survey_app/HYDRATE';

export const FETCH_PROJECTS = 'survey_app/FETCH_PROJECTS';
export const RECEIVE_PROJECTS = 'survey_app/RECEIVE_PROJECTS';
export const ADD_PROJECT = 'survey_app/ADD_PROJECT';
export const DELETE_PROJECT = 'survey_app/DELETE_PROJECT';
export const SELECT_PROJECT = 'survey_app/SELECT_PROJECT';
export const UPDATE_PROJECT = 'survey_app/UPDATE_PROJECT';
export const HIDE_NEWPROJECT_FORM = 'survey_app/HIDE_NEWPROJECT_FORM';

export const FETCH_DATASETS = 'survey_app/FETCH_DATASETS';
export const RECEIVE_DATASETS = 'survey_app/RECEIVE_DATASETS';
export const UPLOAD_DATASET = 'survey_app/UPLOAD_DATASET';
export const UPLOAD_AND_PREDICT = 'survey_app/UPLOAD_AND_PREDICT';
export const DELETE_DATASET = 'survey_app/DELETE_DATASET';

export const FETCH_MODELS = 'survey_app/FETCH_MODELS';
export const RECEIVE_MODELS = 'survey_app/RECEIVE_MODELS';
export const CREATE_MODEL = 'survey_app/CREATE_MODEL';
export const DELETE_MODEL = 'survey_app/DELETE_MODEL';

export const FETCH_PREDICTIONS = 'survey_app/FETCH_PREDICTIONS';
export const RECEIVE_PREDICTIONS = 'survey_app/RECEIVE_PREDICTIONS';
export const DO_SURVEY_PREDICTION = 'survey_app/DO_SURVEY_PREDICTION';
export const DO_SCIENCE_PREDICTIONS = 'survey_app/DO_SCIENCE_PREDICTIONS';
export const DELETE_PREDICTION = 'survey_app/DELETE_PREDICTION';

export const TOGGLE_EXPANDER = 'survey_app/TOGGLE_EXPANDER';
export const HIDE_EXPANDER = 'survey_app/HIDE_EXPANDER';
export const SHOW_EXPANDER = 'survey_app/SHOW_EXPANDER';

export const SPIN_LOGO = 'survey_app/SPIN_LOGO';

import { showNotification } from './Notifications';
import promiseAction from './action_tools';
import { objectType } from './utils';

// Refactor this into a utility function
String.prototype.format = function (...args) {
  let i = 0;
  return this.replace(/{}/g, () => (
    typeof args[i] != 'undefined' ? args[i++] : ''
  ));
};


// Receive list of projects
function receiveProjects(projects) {
  return {
    type: RECEIVE_PROJECTS,
    payload: projects
  };
}


// Download projects
export function fetchProjects() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_PROJECTS,

      fetch('/project', {credentials: 'same-origin'})
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(receiveProjects(json.data));
          } else {
            dispatch(
              showNotification(
                'Error downloading projects ({})'.format(json.message)
              ));
          }
          return json;
        }
        ).catch(ex => console.log('fetchProjects exception:', ex))
      );
}


// Add a new project
export function addProject(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      ADD_PROJECT,

      fetch('/project',
            { credentials: 'same-origin',
              method: 'POST',
              body: JSON.stringify(form),
              headers: new Headers({
                'Content-Type': 'application/json'
              }) })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(resetForm('newProject'));
            dispatch(showNotification('Added new project'));
            dispatch(selectProject(json.data.id));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


// Update an existing project
export function updateProject(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      UPDATE_PROJECT,

      fetch('/project/{}'.format(form.projectId),
            { credentials: 'same-origin',
              method: 'PUT',
              body: JSON.stringify(form),
              headers: new Headers({
                'Content-Type': 'application/json'
              }) })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(resetForm('newProject'));
            dispatch(showNotification('Successfully updated project'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


export function deleteProject(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_PROJECT,

      fetch(`/project/${id}`, { credentials: 'same-origin', method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Project deleted'));
            dispatch(selectProject());
          } else {
            dispatch(
              showNotification(
                'Error deleting project ({})'.format(json.message)
              ));
          }
        })
  );
}


// Currently, used upon creation of a new project to switch to that project
export function selectProject(id=null) {
  return (dispatch) => {
    dispatch(hideExpander('newProjectExpander'));

    return dispatch({
      type: SELECT_PROJECT,
      payload: { id }
    });
  };
}


export function uploadDataset(form) {
  const formData = new FormData();

  for (const key in form) {
    if (form[key] && objectType(form[key][0]) === 'File') {
      formData.append(key, form[key][0]);
    } else {
      formData.append(key, form[key]);
    }
  }

  return dispatch =>
    promiseAction(
      dispatch,
      UPLOAD_DATASET,

      fetch('/dataset', { credentials: 'same-origin', method: 'POST',
                          body: formData })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Successfully uploaded new dataset'));
            dispatch(hideExpander('newDatasetExpander'));
            dispatch(resetForm('newDataset'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


// Download datasets
export function fetchDatasets() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_DATASETS,

      fetch('/dataset', { credentials: 'same-origin' })
        .then(response => response.json())
        .then((json) => (
          dispatch(receiveDatasets(json.data))
        )
        ).catch(ex => console.log('fetchDatasets', ex))
    );
}


// Receive list of datasets
function receiveDatasets(datasets) {
  return {
    type: RECEIVE_DATASETS,
    payload: datasets
  };
}


export function deleteDataset(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_DATASET,

      fetch(`/dataset/${id}`, { credentials: 'same-origin', method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Dataset deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting dataset ({})'.format(json.message)
              ));
          }
        })
  );
}


export function deleteFeatureset(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_FEATURESET,

      fetch(`/features/${id}`, { credentials: 'same-origin', method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Feature set deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting feature set ({})'.format(json.message)
              ));
          }
        })
  );
}


// Download models
export function fetchModels() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_MODELS,

      fetch('/models', { credentials: 'same-origin' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            return dispatch(receiveModels(json.data));
          } else {
            return dispatch(
              showNotification(
                'Error downloading models ({})'.format(json.message)
              ));
          }
        }
        ).catch(ex => console.log('fetchModels', ex))
    );
}

// Receive list of models
function receiveModels(models) {
  return {
    type: RECEIVE_MODELS,
    payload: models
  };
}


export function doSurveyPrediction(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      DO_SURVEY_PREDICTION,

      fetch('/survey_predictions',
            { credentials: 'same-origin',
              method: 'POST',
              body: JSON.stringify(form),
              headers: new Headers({
                'Content-Type': 'application/json'
              }) }
      ).then(response => response.json()
      ).then((json) => {
        if (json.status == 'success') {
          dispatch(resetForm('predict'));
          dispatch(showNotification('Survey classifier model predictions begun'));
          dispatch(hideExpander('predictFormExpander'));
        } else {
          return Promise.reject({ _error: json.message });
        }
        return json;
      })
    );
}


export function doSciencePredictions(payload) {
  return dispatch =>
    promiseAction(
      dispatch,
      DO_SCIENCE_PREDICTIONS,

      fetch('/science_predictions',
            { credentials: 'same-origin',
              method: 'POST',
              body: JSON.stringify(payload),
              headers: new Headers({
                'Content-Type': 'application/json'
              }) }
      ).then(response => response.json()
      ).then((json) => {
        if (json.status == 'success') {
          dispatch(showNotification('Science classifier model predictions begun'));
        } else {
          return Promise.reject({ _error: json.message });
        }
        return json;
      })
    );
}


export function uploadAndPredict(form) {
  const formData = new FormData();
  for (const key in form) {
    if (form[key] && objectType(form[key][0]) === 'File') {
      formData.append(key, form[key][0]);
    } else {
      formData.append(key, form[key]);
    }
  }
  return dispatch =>
    promiseAction(
      dispatch,
      UPLOAD_DATASET,

      fetch('/dataset', { credentials: 'same-origin', method: 'POST',
                          body: formData })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Successfully uploaded new dataset'));
            dispatch(hideExpander('uploadPredictFormExpander'));
            dispatch(resetForm('uploadPredict'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
        .then((json) => {
          const predSurveyFormData = { datasetID: json.data.id,
                                       modelID: 1 };
          dispatch(doSurveyPrediction(predSurveyFormData))
          return json;
        })
  );
}


export function deletePrediction(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_PREDICTION,

      fetch(`/predictions/${id}`, { credentials: 'same-origin', method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Prediction deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting prediction ({})'.format(json.message)
              ));
          }
        })
    );
}


// Download predictions
export function fetchPredictions() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_PREDICTIONS,

      fetch('/predictions', { credentials: 'same-origin' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(receivePredictions(json.data));
          } else {
            dispatch(showNotification(json.message));
          }
        }
        ).catch(ex => console.log('fetchPredictions', ex))
    );
}

// Receive list of predictions
export function receivePredictions(preds) {
  return {
    type: RECEIVE_PREDICTIONS,
    payload: preds
  };
}


export function spinLogo() {
  return {
    type: SPIN_LOGO
  };
}



export function hydrate() {
  return (dispatch) => {
    dispatch(fetchProjects())
      .then((proj) => {
        Promise.all([
          dispatch(fetchDatasets()),
          dispatch(fetchPredictions()),
          dispatch(fetchModels())
        ]).then(() => {
          dispatch(spinLogo());
        });
      });
  };
}




export function hideExpander(id) {
  return {
    type: HIDE_EXPANDER,
    payload: {
      id
    }
  };
}

export function showExpander(id) {
  return {
    type: SHOW_EXPANDER,
    payload: {
      id
    }
  };
}

export function toggleExpander(id) {
  return {
    type: TOGGLE_EXPANDER,
    payload: {
      id
    }
  };
}
