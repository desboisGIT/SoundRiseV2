// Notification.js
import { useEffect, useState } from "react";
import "./Notification.css";

export default function Notification({ notifications, setNotifications }) {
  const [currentNotification, setCurrentNotification] = useState(null);
  const [isDisplayed, setIsDisplayed] = useState(false);

  useEffect(() => {
    if (notifications.length === 0) return;

    // Display the first notification
    setCurrentNotification(notifications[0]);
    setIsDisplayed(true);

    // Hide after 1 second and remove after animation
    const timeout = setTimeout(() => {
      setIsDisplayed(false);
      // Remove after animation finishes (500ms later)
      setTimeout(() => {
        setNotifications((prev) => prev.slice(1)); // This will also update localStorage via the effect in AppContent
      }, 500);
    }, 1000);

    return () => clearTimeout(timeout);
  }, [notifications, setNotifications]);

  if (!currentNotification) return null;

  return (
    <div className={`notification ${isDisplayed ? "displayed" : ""}`}>
      <p>{currentNotification}</p>
    </div>
  );
}
