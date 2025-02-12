import React, { useState } from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import { register } from "../../api/auth";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    try {
      const response = await register(username, email, password);
      console.log("Registration successful:", response);
      setSuccess(true);

      // Redirect to login after a short delay
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    } catch (err) {
      setError(err.response?.data || "Registration failed. Please try again.");
    }
  };

  return (
    <div className="login-page-background">
      <DefaultForm
        title="Register"
        subText="I already have an account?"
        handleSubTextClick={() => (window.location.href = "/login")}
        handleSubmit={handleSubmit} // Pass the function to the form
      >
        <input
          type="text"
          placeholder="Username"
          className="form-input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          className="form-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="form-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && (
          <div className="error-message">
            {typeof error === "string" ? (
              <p>{error}</p>
            ) : (
              Object.entries(error).map(([key, value]) => (
                <p key={key}>{`${key}: ${value}`}</p>
              ))
            )}
          </div>
        )}
        {success && (
          <p className="success-message">
            Registration successful! Redirecting...
          </p>
        )}
      </DefaultForm>
    </div>
  );
}
