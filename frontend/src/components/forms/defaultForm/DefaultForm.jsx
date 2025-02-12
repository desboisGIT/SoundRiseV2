import React from "react";
import "./DefaultForm.css";

export default function DefaultForm({ title, children }) {
  return (
    <div className="default-form">
      <div className="default-form-top-section">
        <h2 className="default-form-title">{title}</h2>
        <div className="default-form-forms">
          <form>{children}</form>
        </div>
      </div>
    </div>
  );
}
