// AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Check if access token exists to determine loggedIn state
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("access_token"));
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  // Automatically fetch user info when logged in and not already in state
  useEffect(() => {
    if (loggedIn && !user) {
      const fetchUserInfo = async () => {
        try {
          const token = localStorage.getItem("access_token");
          const response = await axios.get("http://127.0.0.1:8000/api/user/", {
            headers: { Authorization: `Bearer ${token}` },
          });
          setUser(response.data);
          localStorage.setItem("user", JSON.stringify(response.data));
        } catch (error) {
          console.error("Error fetching user info:", error);
          // Optionally, log out or refresh token if needed
        }
      };
      fetchUserInfo();
    }
  }, [loggedIn, user]);

  const login = (token) => {
    localStorage.setItem("access_token", token);
    setLoggedIn(true);
    // Optionally, you could immediately fetch user info here as well
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    setLoggedIn(false);
  };

  return <AuthContext.Provider value={{ loggedIn, user, login, logout, setUser }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
