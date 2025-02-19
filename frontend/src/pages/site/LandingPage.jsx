import React from "react";
import "./LandingPage.css";
import { useNotification } from "../../components/context/NotificationContext";

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
        </header>
        <div className="extra-content">
          {Array.from({ length: 20 }).map((_, index) => (
            <p key={index}>Extra content {index + 1}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
