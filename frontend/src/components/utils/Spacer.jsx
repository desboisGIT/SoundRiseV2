import React from "react";
import PropTypes from "prop-types";

const Spacer = ({ size, color, orientation, length, customMargin }) => {
  const isPercentage = typeof length === "string" && length.trim().endsWith("%");

  const margin = customMargin || (orientation === "horizontal" ? (isPercentage ? "1px auto" : "1px 0") : isPercentage ? "auto 10px" : "0 10px");

  const style =
    orientation === "horizontal"
      ? {
          height: size,
          width: length,
          backgroundColor: color,
          margin,
        }
      : {
          width: size,
          height: length,
          backgroundColor: color,
          margin,
        };

  return <div style={style} />;
};

Spacer.propTypes = {
  size: PropTypes.string,
  color: PropTypes.string,
  orientation: PropTypes.oneOf(["horizontal", "vertical"]),
  length: PropTypes.string,
  customMargin: PropTypes.string,
};

Spacer.defaultProps = {
  size: "1px",
  color: "#ccc",
  orientation: "horizontal",
  length: "100%",
};

export default Spacer;
