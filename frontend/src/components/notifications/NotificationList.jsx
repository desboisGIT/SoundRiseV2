import React, { useEffect, useState, useCallback } from "react";
import { useWebSocket } from "../context/WebSocketContext";
import Notification from "./Notification";
import Spacer from "../utils/Spacer";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell } from "@fortawesome/free-solid-svg-icons";

function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffSeconds = Math.floor(diffMs / 1000);

  if (diffSeconds < 60) {
    return "il y a quelques secondes...";
  }

  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) {
    return `il y a ${diffMinutes} minute${diffMinutes > 1 ? "s" : ""}...`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) {
    let hours = date.getHours();
    let minutes = date.getMinutes();
    minutes = minutes < 10 ? "0" + minutes : minutes;
    return `${hours}h${minutes}`;
  }

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) {
    const daysFrench = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
    let dayName = daysFrench[date.getDay()];
    let hours = date.getHours();
    let minutes = date.getMinutes();
    minutes = minutes < 10 ? "0" + minutes : minutes;
    return `${dayName} ${hours}h${minutes}`;
  }

  let day = date.getDate();
  let month = date.getMonth() + 1;
  const year = date.getFullYear();
  day = day < 10 ? "0" + day : day;
  month = month < 10 ? "0" + month : month;
  return `${day}/${month}/${year}`;
}

export default function NotificationList({ enableWebSocket = true }) {
  const [notifications, setNotifications] = useState([]);
  const wsService = useWebSocket();

  // Helper: adds a notification and sorts by timestamp (most recent first)
  const addNotification = useCallback((newNotif) => {
    setNotifications((prev) => {
      const updated = [newNotif, ...prev];
      return updated.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    });
  }, []);

  useEffect(() => {
    if (!enableWebSocket || !wsService) return;

    const handleWebSocketMessage = (message) => {
      console.log("📩 WebSocket Message:", message);
      if (message.type === "unread_notifications") {
        const newNotifs = message.notifications.map((notif) => ({
          id: notif.id,
          notif_type: notif.notif_type,
          message: notif.message,
          timestamp: notif.timestamp,
          sender_id: notif.sender_id,
          sender_username: notif.sender_username,
          draft_beat_title: notif.draft_beat_title,
          is_live: false,
        }));
        setNotifications((prev) => {
          const combined = [...newNotifs, ...prev];
          return combined.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        });
      } else if (message.type === "invitation_notification") {
        addNotification({
          id: message.invite_id,
          notif_type: message.notif_type,
          message: `${message.sender_username} vous a invité à collaborer sur '${message.draftbeat_title}'.`,
          timestamp: new Date().toISOString(),
          sender_id: message.sender_id,
          sender_username: message.sender_username,
          draft_beat_title: message.draftbeat_title,
          is_live: true,
        });
      }
    };

    wsService.addListener(handleWebSocketMessage);
    return () => wsService.removeListener(handleWebSocketMessage);
  }, [wsService, enableWebSocket, addNotification]);

  return (
    <div className="notification-list">
      <div className="notificaction-list-header">
        <FontAwesomeIcon icon={faBell} />
        <h2>Notifications</h2>
      </div>
      {notifications.length === 0 ? (
        <p>Aucune notification.</p>
      ) : (
        notifications.map((notif, index) => (
          <React.Fragment key={notif.id}>
            {index !== 0 && <Spacer size="1px" color="#313131" orientation="horizontal" length="95%" />}
            <Notification
              sender_id={notif.sender_id}
              sender_username={notif.sender_username}
              message={notif.message}
              id={notif.id}
              type={notif.notif_type}
              timestamp={formatTimestamp(notif.timestamp)}
              draft_beat_title={notif.draft_beat_title}
              is_live={notif.is_live}
            />
          </React.Fragment>
        ))
      )}
    </div>
  );
}
