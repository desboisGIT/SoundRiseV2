// SideBar.jsx
import React from "react";
import { NavLink } from "react-router-dom";
import "./SideBar.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTachometerAlt,
  faMusic,
  faUpload,
  faFileInvoiceDollar,
  faChartLine,
  faUser,
  faCog,
  faComments,
  faHeadset,
} from "@fortawesome/free-solid-svg-icons";

const SideBar = ({ isSidebarOpen }) => {
  return (
    <div className={`sidebar ${isSidebarOpen ? "open" : "closed"}`}>
      <div className="sidebar-header">
        <h3>Dashboard</h3>
      </div>
      <ul className="sidebar-list">
        <li>
          <NavLink
            to="/dashboard/my-beats"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faMusic} /> My Beats
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/upload-beat"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faUpload} /> Upload Beat
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/licences"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faFileInvoiceDollar} /> Licences
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/analytics"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faChartLine} /> Analytics
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/profile"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faUser} /> Profile
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/settings"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faCog} /> Settings
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/messages"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faComments} /> Messages
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/dashboard/support"
            className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          >
            <FontAwesomeIcon icon={faHeadset} /> Support
          </NavLink>
        </li>
      </ul>
    </div>
  );
};

export default SideBar;
