import React, { useState, useEffect } from "react";
import DefaultForm from "../../components/forms/defaultForm/DefaultForm";
import "./LogIn.css";
import axios from "axios";
import { login as loginApi } from "../../api/auth";
import LoginWithGoogle from "../../components/auth/LoginWithGoogle";
import { useNotification } from "../../components/context/NotificationContext";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/context/AuthContext"; // Import the auth hook
import MainLogo from "../../assets/main_logo.svg";
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
      <DefaultForm className="login-form">
        <p className="SoundRiseLogoTextLogin" onClick={() => navigate("/")}>
          Connectez-vous gratuitement pour profiter de nos fonctionnalités.
        </p>
        <div className="oauth-separator">
          <div className="separator-second"></div>
          <p className="continue-with-text">Se connecter</p>
          <div className="separator-second"></div>
        </div>
        <form>
          {error && <p className="error">{error}</p>}
          <div className="form-input-group">
            <label htmlFor="email" className="form-input-label">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="Email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-input-group">
            <label htmlFor="password" className="form-input-label">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              placeholder="Mot de passe"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>{" "}
          <div>
            <button type="submit" onClick={handleSubmit} className="default-form-bottom-section-sumbit-button">
              Connexion
            </button>
            <p className="default-form-bottom-section-text" onClick={() => navigate("/register")}>
              Don't have an account yet?
            </p>
          </div>
        </form>
        <div className="oauth-separator">
          <div className="separator-second"></div>
          <p className="continue-with-text">Ou continué avec</p>
          <div className="separator-second"></div>
        </div>

        <div className="default-form-bottom-section">
          <LoginWithGoogle />
        </div>
      </DefaultForm>
    </div>
  );
}
