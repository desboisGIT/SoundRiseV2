// AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Initialize auth state based on whether a token exists
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("access_token"));

  // Optionally, you could add effects to listen for changes or to verify the token

  const login = (token) => {
    localStorage.setItem("access_token", token);
    setLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setLoggedIn(false);
  };

  return <AuthContext.Provider value={{ loggedIn, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
