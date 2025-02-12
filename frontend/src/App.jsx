import "./App.css";
import TopBarButtonDropDown from "./components/topbar/subComponents/TopBarButtonDropDown";
import TopBarButton from "./components/topbar/subComponents/TopBarButton";
import TopBar from "./components/topbar/TopBar";
import MainLogo from "./assets/main_logo.svg";
import LandingPage from "./pages/site/LandingPage";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import LogIn from "./pages/user/LogIn";
import Register from "./pages/user/Register";
import React from "react";
import axios from "axios";
import Account from "./pages/user/Account";

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};
const handleLogout = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  axios.defaults.headers.common["Authorization"] = null;
  console.log("Logged out");
};

const AppContent = () => {
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
              <img
                src={MainLogo}
                alt="SoundRise Logo"
                className="SoundRiseLogoMain"
                onClick={() => navigate("/")}
              />
              <p className="SoundRiseLogoText" onClick={() => navigate("/")}>
                SoundRise
              </p>
            </div>
            <TopBarButtonDropDown
              title="Feed"
              optionList={ExploreOptions}
              position={"center"}
            />
          </>
        }
        rightComponents={
          <>
            <TopBarButtonDropDown
              title="Accounts"
              optionList={accountsOptions}
              position={"center"}
            />
            <TopBarButton title="Log In" action={() => navigate("/login")} />
            <TopBarButton
              title="Register"
              action={() => navigate("/register")}
            />
          </>
        }
      />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LogIn />} />
        <Route path="/register" element={<Register />} />
        <Route path="/account" element={<Account />} />
      </Routes>
    </>
  );
};

export default App;
