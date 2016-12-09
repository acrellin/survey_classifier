import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { reduxForm } from 'redux-form';

import { FormComponent, SelectInput, SubmitButton,
         TextInput, FileInput, Form } from './Form';
import * as Validate from './validate';
import Expand from './Expand';
import * as Action from './actions';
import { contains, reformatDatetime } from './utils';
import FoldableRow from './FoldableRow';
import Delete from './Delete';
import Tooltip from './Tooltip';
import { PredictionsTable, PredictionResults } from './Predictions';
import { DatasetInfo, DatasetTable, UploadPredictDatasetForm } from './Datasets';



const UploadPredictTab = props => (
  <div className="uploadPredictTab">

    <UploadPredictDatasetForm
      selectedProject={props.selectedProject}
    />

    <PredictionsTable selectedProject={props.selectedProject} />

  </div>
);
UploadPredictTab.propTypes = {
  selectedProject: PropTypes.object
};


export default UploadPredictTab;
