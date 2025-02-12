import React, { useState, useEffect } from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import "./LogIn.css";
import axios from "axios";
import { login } from "../../api/auth";
import LoginWithGoogle from "../../components/auth/LoginWithGoogle";

export default function LogIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
      window.location.href = "/account";
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = await login(email, password);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      axios.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;
      window.location.href = "/account";
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    }
  };

  return (
    <div className="login-page-background">
      <DefaultForm title="Log In">
        {error && <p className="error">{error}</p>}
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

        <div className="default-form-bottom-section">
          <LoginWithGoogle />
          <p
            className="default-form-bottom-section-text"
            onClick={() => (window.location.href = "/register")}
          >
            Don't have an account yet?
          </p>
          <button
            type="submit"
            onClick={handleSubmit}
            className="default-form-bottom-section-sumbit-button"
          >
            Envoyer
          </button>
        </div>
      </DefaultForm>
    </div>
  );
}
