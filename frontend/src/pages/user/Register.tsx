import React from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";

export default function Register() {
  return (
    <>
      <div className="login-page-background">
        <DefaultForm
          title="Register"
          subText="I already have an account ?"
          handleSubTextClick={() => (window.location.href = "/login")}
          handleSubmit={() => null}
        >
          {" "}
          <input type="text" placeholder="Username" className="form-input" />
          <input
            type="password"
            placeholder="Password"
            className="form-input"
          />
        </DefaultForm>
      </div>
    </>
  );
}
