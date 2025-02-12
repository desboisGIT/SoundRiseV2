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
import { NotificationProvider } from "./components/NotificationContext";
import { AuthProvider, useAuth } from "./components/context/AuthContext"; // Import your Auth context
// (We no longer need to call isLoggedIn() manually here.)
const clientId = "162639459241-vfs3ogmpn0fb9jhva7fhfc18k1qlqqm0.apps.googleusercontent.com";

const AppContent = () => {
  const navigate = useNavigate();
  // Get the global auth state and logout function from the context
  const { loggedIn, logout } = useAuth();

  // Define your options for the account dropdown
  const accountsOptions = [
    ["Profile", () => navigate("/account")],
    ["Settings", () => console.log("Settings")],
    ["Messages", () => console.log("Messages")],
    [
      "Log Out",
      () => {
        logout(); // This updates the auth state immediately.
        // Optionally, clear axios defaults or navigate to a public route:
        axios.defaults.headers.common["Authorization"] = null;
        navigate("/");
      },
    ],
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
            {loggedIn ? (
              <TopBarButtonDropDown title="Accounts" optionList={accountsOptions} position="center" />
            ) : (
              <>
                <TopBarButton title="Log In" action={() => navigate("/login")} />
                <TopBarButton title="Register" action={() => navigate("/register")} />
              </>
            )}
          </>
        }
      />
      <NotificationProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LogIn />} />
          <Route path="/register" element={<Register />} />
          <Route path="/account" element={<Account />} />
        </Routes>
      </NotificationProvider>
    </>
  );
};

const App = () => {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
