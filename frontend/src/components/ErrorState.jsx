import React from 'react';

const ErrorState = ({ message = 'Something went wrong.', onRetry }) => {
  return (
    <div className="error-state">
      <div className="error-icon">⚠️</div>
      <p className="error-message">{message}</p>
      {onRetry && (
        <button className="btn btn-outline btn-sm" onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorState;
