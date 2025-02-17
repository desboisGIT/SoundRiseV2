import React from "react";
import "./DefaultPopUp.css";

const DefaultPopUp = ({ isDisplayed, children, onClose, className, ...rest }) => {
  if (!isDisplayed) {
    return null;
  }

  // Close the popup if the click happens on the overlay
  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="popup-overlay" onClick={handleOverlayClick}>
      <div className={`popup-content ${className || ""}`} {...rest}>
        {children}
      </div>
    </div>
  );
};

export default DefaultPopUp;
