import React from "react";
import "./TopBar.css";

function TopBar({ leftComponents, rightComponents, centerComponents }) {
  return (
    <div className="TopBar">
      <div className="TopBarLeft">{leftComponents}</div>
      <div className="TopBarRight">{centerComponents}</div>
      <div className="TopBarRight">{rightComponents}</div>
    </div>
  );
}

export default TopBar;
