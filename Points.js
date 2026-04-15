import React from 'react';
import PropTypes from 'prop-types';
import PaymentPointsContext from './PaymentPointsContext';
import { withContext } from '../../components';

function Points({ agentPoints: { points, lastUpdated } }) {
	if (points === 0) return null;
	return (
		<div className="header__points">
			<p>{points} points</p>
			<div className="header__points__tooltip__tail"></div>
			<div className="header__points__tooltip">
				<p className="type--p3 type--p3--medium spc--bottom--med">Payment point balance</p>
				<p className="type--p4">(Last Updated: {lastUpdated}) </p>
			</div>
		</div>
	);
}

Points.propTypes = {
	agentPoints: PropTypes.shape({
		points: PropTypes.number.isRequired,
		lastUpdated: PropTypes.string.isRequired,
	}).isRequired,
};

export default withContext(Points, PaymentPointsContext, 'agentPoints');
