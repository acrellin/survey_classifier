import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { reduxForm } from 'redux-form';

import { FormComponent, SelectInput, SubmitButton,
         Form } from './Form';

import * as Validate from './validate';

import Expand from './Expand';
import * as Action from './actions';
import { contains, reformatDatetime } from './utils';
import FoldableRow from './FoldableRow';
import Delete from './Delete';


let PredictForm = (props) => {
  const { fields: { modelID, datasetID }, handleSubmit, submitting, resetForm,
          error } = props;

  const datasets = props.datasets.map(ds => (
    { id: ds.id,
      label: ds.name }
  ));

  const models = props.models
                   .filter(model => !Validate.isEmpty(model.finished))
                   .map(model => (
                     { id: model.id,
                       label: model.name }
                   ));

  return (
    <div>
      <Form onSubmit={handleSubmit} error={error}>
        <SelectInput
          label="Select Model"
          key={`${props.selectedProject.id}modelID`}
          options={models}
          {...modelID}
        />
        <SelectInput
          label="Select Data Set"
          key={`${props.selectedProject.id}datasetID`}
          options={datasets}
          {...datasetID}
        />
        <SubmitButton
          label="Predict"
          submitting={submitting}
          resetForm={resetForm}
        />
      </Form>
    </div>
  );
};
PredictForm.propTypes = {
  fields: React.PropTypes.object.isRequired,
  error: React.PropTypes.string,
  handleSubmit: React.PropTypes.func.isRequired,
  resetForm: React.PropTypes.func.isRequired,
  submitting: React.PropTypes.bool.isRequired,
  datasets: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  models: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  selectedProject: React.PropTypes.object.isRequired
};


const mapStateToProps = (state, ownProps) => {
  const filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project === ownProps.selectedProject.id));
  const zerothDataset = filteredDatasets[0];

  const models = JSON.parse(JSON.stringify(state.models));
  const zerothModel = models[0];

  return {
    datasets: filteredDatasets,
    models,
    fields: ['modelID', 'datasetID'],
    initialValues: { modelID: zerothModel ? zerothModel.id : '',
                    datasetID: zerothDataset ? zerothDataset.id : '' }
  };
};

const validate = Validate.createValidator({
  modelID: [Validate.required],
  datasetID: [Validate.required],
});


PredictForm = reduxForm({
  form: 'predict',
  fields: [''],
  validate
}, mapStateToProps)(PredictForm);


export let PredictionsTable = props => (
  <table className="table">
    <thead>
      <tr>
        <th style={{ width: '15em' }}>Data Set Name</th>
        <th style={{ width: '15em' }}>Model Name</th>
        <th style={{ width: '25em' }}>Created</th>
        <th style={{ width: '15em' }}>Status</th>
        <th style={{ width: '15em' }}>Actions</th>
        <th style={{ width: 'auto' }} />{ /* extra column, used to capture expanded space */ }
      </tr>
    </thead>

    {
      props.predictions.map((prediction, idx) => {
        const done = prediction.finished;
        const status = done ? <td>Completed {reformatDatetime(prediction.finished)}</td> : <td>In progress</td>;
        const sciPredDone = prediction.science_preds_finished;

        const foldedContent = done && ([
          <tr key={`surv_pred${idx}`}>
            <td colSpan={6}>
              <SurveyPredictionResults prediction={prediction} />
            </td>
          </tr>,
          <tr key={`sci_pred${idx}`}>
            <td colSpan={6}>
              { sciPredDone && <SciencePredictionResults prediction={prediction} /> }
            </td>
          </tr>
        ]);

        return (
          <FoldableRow key={idx}>
            <tr key={`row${idx}`}>
              <td>{prediction.dataset_name}</td>
              <td style={{ textDecoration: 'underline' }}>{prediction.model_name}</td>
              <td>{reformatDatetime(prediction.created)}</td>
              {status}
              <td>
                <DeletePrediction ID={prediction.id} />
              </td>
              <td />
            </tr>
            {foldedContent}
          </FoldableRow>
        ); })
    }

  </table>
);
PredictionsTable.propTypes = {
  predictions: PropTypes.arrayOf(PropTypes.object)
};


export const SurveyPredictionResults = (props) => {
  const modelType = props.prediction.model_type;
  const results = props.prediction.results;

  const firstResult = results ? results[Object.keys(results)[0]] : null;
  const classes = (firstResult && firstResult.prediction) ?
                Object.keys(firstResult.prediction) : null;

  let modelHasClass = contains(['RidgeClassifierCV'], modelType);
  const modelHasProba = props.prediction.isProbabilistic;
  const modelHasTarget = contains(['RandomForestRegressor',
                                 'LinearRegressor',
                                 'BayesianARDRegressor',
                                 'BayesianRidgeRegressor'],
                                  modelType);
  if (modelType === 'LinearSGDClassifier') {
    modelHasClass = !modelHasProba;
  }

  const hasTrueTargetLabel = p => (p && p.label);

  return (
    <table className="table">
      <thead>
        <tr>
          <td colSpan={6}>
            <h5><b>Survey Classifier Prediction Results</b></h5>
          </td>
          <td style={{ width: "100px" }}>
            <br />
            <DownloadSurveyPredCSV ID={props.prediction.id} />
          </td>
        </tr>
        <tr>
          <th>Time Series</th>
          {hasTrueTargetLabel(firstResult) && <th>True Class/Target</th>}

          {modelHasProba &&
           classes.map((classLabel, idx) => ([
             <th key="0">Predicted Class</th>,
             <th key="1">Probability</th>
           ]))
          }

          {modelHasClass && <th>Predicted Class</th>}
          {modelHasTarget && <th>Predicted Target</th>}
        </tr>
      </thead>

      <tbody>
      {results && Object.keys(results).map((fname, idx) => {
        const result = results[fname];
        const classesSorted = classes.sort((a, b) => (result.prediction[b] - result.prediction[a]));

        return (
          <tr key={idx}>

            <td>{fname}</td>

            {
              [hasTrueTargetLabel(result) &&
                <td key="pt">{result.label}</td>,

               modelHasProba &&
               classesSorted.map((classLabel, idx2) => ([
                 <td key="cl0">{classLabel}</td>,
                 <td key="cl1">{result.prediction[classLabel]}</td>
               ])),

               modelHasClass && <td key="rp">{result.prediction}</td>,

               modelHasTarget && <td key="rp">{result.prediction}</td>
             ]}

          </tr>
        ); })}
      </tbody>
    </table>
  );
};
SurveyPredictionResults.propTypes = {
  prediction: PropTypes.object.isRequired
};


export const SciencePredictionResults = (props) => {
  const modelType = props.prediction.model_type;
  const results = props.prediction.science_results;

  const firstResult = results ? results[Object.keys(results)[0]] : null;
  const classes = (firstResult && firstResult.combined) ?
                  Object.keys(firstResult.combined) : null;

  let modelHasClass = contains(['RidgeClassifierCV'], modelType);
  const modelHasProba = props.prediction.isProbabilistic;
  const modelHasTarget = contains(['RandomForestRegressor',
                                   'LinearRegressor',
                                   'BayesianARDRegressor',
                                   'BayesianRidgeRegressor'],
                                  modelType);
  if (modelType === 'LinearSGDClassifier') {
    modelHasClass = !modelHasProba;
  }

  const hasTrueTargetLabel = p => (p && p.label);

  const nClassesToShow = 10;

  return (
    <table className="table">
      <thead>
        <tr>
          <td colSpan={6}>
            <h5><b>Science Classifier Prediction Results</b></h5>
          </td>
          <td>
            <br />
            <DownloadSciencePredCSV ID={props.prediction.id} />
          </td>
        </tr>
        <tr>
          <th>Time Series</th>
          {hasTrueTargetLabel(firstResult) && <th>True Class/Target</th>}

          {modelHasProba &&
           classes.slice(0, nClassesToShow).map((classLabel, idx) => ([
             <th key="0">Predicted Class</th>,
             <th key="1">Probability</th>
           ]))
          }

          {modelHasClass && <th>Predicted Class</th>}
          {modelHasTarget && <th>Predicted Target</th>}
        </tr>
      </thead>

      <tbody>
        {results && Object.keys(results).map((fname, idx) => {
           const result = results[fname].combined;
           const classesSorted = classes.sort((a, b) => (result[b] - result[a]));

           return (
             <tr key={idx}>

               <td>{fname}</td>

               {
                 [hasTrueTargetLabel(result) &&
                  <td key="pt">{result.label}</td>,

                  modelHasProba &&
                  classesSorted.slice(0, nClassesToShow).map((classLabel, idx2) => ([
                    <td key="cl0">{classLabel}</td>,
                    <td key="cl1">{Math.round(result[classLabel] * 1000) / 1000}</td>
                  ]))
                 ]}

             </tr>
           ); })}
      </tbody>
    </table>
  );
};
SciencePredictionResults.propTypes = {
  prediction: PropTypes.object.isRequired
};

const ptMapStateToProps = (state, ownProps) => {
  const filteredPredictions = state.predictions.filter(pred =>
    (pred.project === ownProps.selectedProject.id));
  return {
    predictions: filteredPredictions
  };
};


PredictionsTable = connect(ptMapStateToProps)(PredictionsTable);

const dpMapDispatchToProps = dispatch => (
    { delete: id => dispatch(Action.deletePrediction(id)) }
);

const DeletePrediction = connect(null, dpMapDispatchToProps)(Delete);

const DownloadSurveyPredCSV = (props) => (
  <a
    style={{ display: "inline-block" }}
    href={`/survey_predictions/${props.ID}/download`}
  >
    Download
  </a>
);
DownloadSurveyPredCSV.propTypes = {
  ID: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
};

const DownloadSciencePredCSV = (props) => (
  <a
    style={{ display: "inline-block" }}
    href={`/science_predictions/${props.ID}/download`}
  >
    Download
  </a>
);
DownloadSciencePredCSV.propTypes = {
  ID: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
};

let PredictTab = props => (
  <div>
    <Expand label="Predict Targets" id="predictFormExpander">
      <PredictForm
        onSubmit={props.doSurveyPrediction}
        selectedProject={props.selectedProject}
      />
    </Expand>
    <br />
    <PredictionsTable selectedProject={props.selectedProject} />
  </div>
);
PredictTab.propTypes = {
  doSurveyPrediction: PropTypes.func.isRequired,
  selectedProject: PropTypes.object
};


const mapDispatchToProps = dispatch => (
  {
    doSurveyPrediction: form => dispatch(Action.doSurveyPrediction(form))
  }
);


PredictTab = connect(null, mapDispatchToProps)(PredictTab);


export default PredictTab;
