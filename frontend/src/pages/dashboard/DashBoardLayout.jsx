// DashboardLayout.jsx
import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import SideBar from "../../components/dashBoard/SideBar";
import DashBoardTopBar from "../../components/dashBoard/DashBoardTopBar";
import "./DashboardLayout.css";

const DashboardLayout = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  return (
    <div className="dashboard-layout">
      <DashBoardTopBar toggleSidebar={toggleSidebar} selectedLink="" />
      <div className="dashboard-separator">
        <SideBar isSidebarOpen={isSidebarOpen} />
        <main className="dashboard-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
