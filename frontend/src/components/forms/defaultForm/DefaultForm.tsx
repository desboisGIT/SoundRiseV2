import React from "react";
import "./DefaultForm.css";

export default function DefaultForm({
  title,
  children,
  subText,
  handleSubTextClick,
  handleSubmit,
}) {
  return (
    <div className="default-form">
      <div className="default-form-top-section">
        <h2 className="default-form-title">{title}</h2>
        <div className="default-form-forms">
          <form>{children}</form>
        </div>
      </div>

      <div className="default-form-bottom-section">
        <p
          className="default-form-bottom-section-text"
          onClick={handleSubTextClick}
        >
          {subText}
        </p>{" "}
        <button
          type="submit"
          onClick={handleSubmit}
          className="default-form-bottom-section-sumbit-button"
        >
          Envoyer
        </button>
      </div>
    </div>
  );
}
