import React, { useState, useEffect } from 'react';

const PageLoader = ({ message = 'Loading...', delay = 250, overlay = false }) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Only show loader after a short delay to avoid flashing on quick loads
    const timer = setTimeout(() => setShow(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  if (!show) return null;

  const content = (
    <div className="loader-container">
      <div className="spinner"></div>
      <p className="loader-message">{message}</p>
    </div>
  );

  if (overlay) {
    return (
      <div className="loader-overlay">
        {content}
      </div>
    );
  }

  return content;
};

export default PageLoader;
