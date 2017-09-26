import React from 'react';
import ReactTooltip from 'react-tooltip';

const Tooltip = props => (
  <ReactTooltip place={props.place} delayShow={props.delay} id={props.id}>
    <span>
      {props.text}
    </span>
  </ReactTooltip>
);
Tooltip.propTypes = {
  id: React.PropTypes.string.isRequired,
  text: React.PropTypes.oneOfType([
    React.PropTypes.string,
    React.PropTypes.array
  ]).isRequired,
  place: React.PropTypes.string,
  delay: React.PropTypes.number
};
Tooltip.defaultProps = {
  place: 'top',
  delay: 700
};
export default Tooltip;
