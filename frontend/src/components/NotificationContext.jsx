// NotificationContext.jsx
import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import "./NotificationSystem.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

const NotificationContext = createContext();

export const useNotification = () => {
  return useContext(NotificationContext);
};

export const NotificationProvider = ({ children }) => {
  // Each notification is an object: { message: string, type: string }
  const [queue, setQueue] = useState([]);
  const [current, setCurrent] = useState(null);
  const [visible, setVisible] = useState(false);
  const timeoutRef = useRef(null);

  // addNotification accepts an object with a message and a type.
  const addNotification = ({ message, type = "default" }) => {
    setQueue((prevQueue) => [...prevQueue, { message, type }]);
  };

  // Function to manually close the notification.
  const closeNotification = () => {
    clearTimeout(timeoutRef.current);
    setVisible(false);
  };

  // When no notification is visible and the queue has items, show the next one.
  useEffect(() => {
    if (!visible && queue.length > 0) {
      const nextNotification = queue[0];
      setQueue((prevQueue) => prevQueue.slice(1));
      setCurrent(nextNotification);
      setVisible(true);
    }
  }, [queue, visible]);

  // Auto-hide the notification after 2000ms.
  useEffect(() => {
    if (visible) {
      timeoutRef.current = setTimeout(() => {
        setVisible(false);
      }, 2000);
    }
    return () => clearTimeout(timeoutRef.current);
  }, [visible]);

  // Once the notification expires (visible becomes false) and it is the last notification in the queue,
  // update its type to "default" if it's not already.
  useEffect(() => {
    if (!visible && current && queue.length === 0) {
      if (current.type !== "default") {
        setCurrent({ ...current, type: "default" });
      }
    }
  }, [visible, current, queue]);

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <div className={`notification-wrapper ${visible ? "show" : ""}`}>
        {current && (
          <div className={`notification ${current.type}`}>
            <span className="notification-message">{current.message}</span>
            <button className="notification-close" onClick={closeNotification}>
              <FontAwesomeIcon icon={faXmark} color="#fff" />
            </button>
          </div>
        )}
      </div>
    </NotificationContext.Provider>
  );
};
