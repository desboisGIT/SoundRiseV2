import React from "react";
import "./DefaultForm.css";

export default function DefaultForm({ title, children, className }) {
  return (
    <div className={`default-form ${className}`}>
      <div className="default-form-top-section">
        <div className="default-form-forms">{children}</div>
      </div>
    </div>
  );
}
