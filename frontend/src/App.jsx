import React from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import axios from "axios";
import "./App.css";
import TopBar from "./components/topbar/TopBar";
import TopBarButtonDropDown from "./components/topbar/subComponents/TopBarButtonDropDown";
import TopBarButton from "./components/topbar/subComponents/TopBarButton";
import MainLogo from "./assets/main_logo.svg";
import LandingPage from "./pages/site/LandingPage";
import LogIn from "./pages/user/LogIn";
import Register from "./pages/user/Register";
import Account from "./pages/user/Account";
import Notification from "./components/notifications/Notification";
import { useState, useEffect } from "react";
const clientId = "162639459241-vfs3ogmpn0fb9jhva7fhfc18k1qlqqm0.apps.googleusercontent.com";

const handleLogout = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  axios.defaults.headers.common["Authorization"] = null;
  console.log("Logged out");
};

const defaultNotifications = [];

const AppContent = () => {
  const storedNotifications = JSON.parse(localStorage.getItem("notifications"));
  const [notifications, setNotifications] = useState(storedNotifications || defaultNotifications);

  useEffect(() => {
    localStorage.setItem("notifications", JSON.stringify(notifications));
  }, [notifications]);

  const navigate = useNavigate();
  const accountsOptions = [
    ["Profile", () => navigate("/account")],
    ["Settings", () => console.log("Settings")],
    ["Messages", () => console.log("Messages")],
    ["Log Out", handleLogout],
  ];
  const ExploreOptions = [
    ["Beats", () => console.log("Beats")],
    ["SoundTracks", () => console.log("SoundTracks")],
    ["Trending", () => console.log("Trending")],
    ["Free", () => console.log("Free")],
  ];

  return (
    <>
      <TopBar
        leftComponents={
          <>
            <div className="SoundRiseLogoContainer">
              <img src={MainLogo} alt="SoundRise Logo" className="SoundRiseLogoMain" onClick={() => navigate("/")} />
              <p className="SoundRiseLogoText" onClick={() => navigate("/")}>
                SoundRise
              </p>
            </div>
            <TopBarButtonDropDown title="Feed" optionList={ExploreOptions} position="center" />
          </>
        }
        rightComponents={
          <>
            <TopBarButtonDropDown title="Accounts" optionList={accountsOptions} position="center" />
            <TopBarButton title="Log In" action={() => navigate("/login")} />
            <TopBarButton title="Register" action={() => navigate("/register")} />
          </>
        }
      />
      <Notification notifications={notifications} setNotifications={setNotifications} />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LogIn />} />
        <Route path="/register" element={<Register />} />
        <Route path="/account" element={<Account />} />
      </Routes>
    </>
  );
};

const App = () => {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <Router>
        <AppContent />
      </Router>
    </GoogleOAuthProvider>
  );
};

export default App;
