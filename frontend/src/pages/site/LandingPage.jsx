import React from "react";
import "./LandingPage.css";
import { useNotification } from "../../components/NotificationContext";

export default function LandingPage() {
  const { addNotification } = useNotification();

  const handleNotify = (message, type) => {
    addNotification({ message, type });
  };
  return (
    <div className="background-gradient">
      <div className="landing-page">
        <header className="header">
          <h1>Welcome to SoundRise</h1>
          <button onClick={() => handleNotify("Connecter", "success")}>success</button>
          <button onClick={() => handleNotify("Déconnecté", "error")}>error</button>
          <button onClick={() => handleNotify("Connection faible", "warning")}>warning</button>
          <button onClick={() => handleNotify("Nouveau message", "default")}>default</button>
          <p>Site in construction...</p>
        </header>
      </div>
    </div>
  );
}
