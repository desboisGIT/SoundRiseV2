import React, { useState } from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import "./LogIn.css";
import axios from "axios";
import { login } from "../../api/auth";

export default function LogIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = await login(email, password);
      // Save tokens in localStorage (or in your auth context/state)
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      // Optionally set the axios default Authorization header for future requests
      axios.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;

      console.log("Login successful", data);
      // Redirect or update global auth state as needed
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    }
  };

  return (
    <div className="login-page-background">
      <DefaultForm
        title="Log In"
        subText="Don't have an account yet?"
        handleSubTextClick={() => (window.location.href = "/register")}
        handleSubmit={handleSubmit}
      >
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
      </DefaultForm>
    </div>
  );
}
