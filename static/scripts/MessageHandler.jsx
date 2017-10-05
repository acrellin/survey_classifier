import * as Action from './actions';
import { SHOW_NOTIFICATION, showNotification } from 'baselayer/components/Notifications';
import MessageHandler from 'baselayer/MessageHandler';

let AppMessageHandler = dispatch => {
  return new MessageHandler(dispatch, message => {
    switch (message.action) {
      case Action.FETCH_PROJECTS:
        dispatch(Action.fetchProjects());
        break;
      case Action.FETCH_DATASETS:
        dispatch(Action.fetchDatasets());
        break;
      case Action.FETCH_MODELS:
        dispatch(Action.fetchModels());
        break;
      case Action.FETCH_PREDICTIONS:
        dispatch(Action.fetchPredictions());
        break;
      case Action.DO_SCIENCE_PREDICTIONS:
        dispatch(Action.doSciencePredictions(message.payload));
        break;
      default:
        console.log('Unknown message received through flow:',
                    message);
    }
  });
}

export default AppMessageHandler;
