import React from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import "./LogIn.css";

export default function LogIn() {
  return (
    <>
      <div className="login-page-background">
        <DefaultForm
          title="Log In"
          subText="Doesn't have an account yet ?"
          handleSubTextClick={() => (window.location.href = "/register")}
          handleSubmit={() => null}
        >
          {" "}
          <input
            type="text"
            placeholder="Username"
            className="form-input"
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="form-input"
            required
          />
        </DefaultForm>
      </div>
    </>
  );
}
