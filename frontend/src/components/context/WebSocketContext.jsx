// /src/contexts/WebSocketContext.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import WebSocketService from "../../api/websocket";
import { useAuth } from "./AuthContext";

const WebSocketContext = createContext(null);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const { user, loggedIn } = useAuth();
  const [wsService, setWsService] = useState(null);

  useEffect(() => {
    if (!loggedIn || !user) return;

    const token = localStorage.getItem("access_token");
    const service = new WebSocketService(user.id, token);
    service.connect();
    setWsService(service);

    return () => {
      service.disconnect();
    };
  }, [loggedIn, user]);

  return <WebSocketContext.Provider value={wsService}>{children}</WebSocketContext.Provider>;
};
