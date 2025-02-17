// DashBoardTopBar.jsx
import React from "react";
import "./DashBoardTopBar.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars } from "@fortawesome/free-solid-svg-icons";

const DashBoardTopBar = ({ toggleSidebar }) => {
  return (
    <div className="dashboard-topbar default-box">
      <button className="toggle-sidebar-btn " onClick={toggleSidebar}>
        <FontAwesomeIcon icon={faBars} style={{ color: "#f2f2f2" }} />
      </button>
      <h3 className="topbar-title">BeatMaker DashBoard</h3>
    </div>
  );
};

export default DashBoardTopBar;
