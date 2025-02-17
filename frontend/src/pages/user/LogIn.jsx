import React, { useState, useEffect } from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import "./LogIn.css";
import axios from "axios";
import { login as loginApi } from "../../api/auth";
import LoginWithGoogle from "../../components/auth/LoginWithGoogle";
import { useNotification } from "../../components/NotificationContext";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/context/AuthContext"; // Import the auth hook

export default function LogIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const { addNotification } = useNotification();
  const navigate = useNavigate();
  const { login } = useAuth(); // Destructure the login function from context

  const handleNotify = (message, type) => {
    addNotification({ message, type });
  };

  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
      navigate("/account");
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = await loginApi(email, password);
      // Instead of just setting localStorage here, call the login function from the context
      login(data.access, data.refresh);
      handleNotify("Bienvenue sur SoundRise", "success");
      axios.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;
      navigate("/account");
    } catch (err) {
      handleNotify(err.response?.data?.detail || "Login failed. Please try again.", "error");
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
          <p className="default-form-bottom-section-text" onClick={() => navigate("/register")}>
            Don't have an account yet?
          </p>
          <button type="submit" onClick={handleSubmit} className="default-form-bottom-section-sumbit-button">
            Envoyer
          </button>
        </div>
      </DefaultForm>
    </div>
  );
}
