import React, { useEffect, useState } from "react";
import { useWebSocket } from "../context/WebSocketContext";
import Notification from "./Notification";

export default function NotificationList() {
  const [notifications, setNotifications] = useState([]); // Store all notifications
  const wsService = useWebSocket();

  useEffect(() => {
    if (!wsService) return;

    const handleWebSocketMessage = (message) => {
      console.log("📩 WebSocket received message:", message);

      if (message.type === "unread_notifications") {
        // 🟢 If it's past notifications, merge them with existing notifications
        setNotifications((prev) => {
          const newNotifs = message.notifications.map((notif) => ({
            notif_type: notif.notif_type,
            id: notif.id,
            message: notif.message,
            timestamp: notif.timestamp,
          }));
          return [...newNotifs, ...prev]; // Keep new notifications on top
        });
      } else if (message.type === "invitation_notification") {
        // 🟢 If it's a new invitation notification, add it to the list
        setNotifications((prev) => [
          {
            notif_type: message.notif_type,
            id: message.invite_id,
            message: `${message.sender} vous a invité à collaborer sur '${message.draftbeat_title}'.`,
            timestamp: new Date().toISOString(),
          },
          ...prev, // Keep existing notifications
        ]);
      }
    };

    wsService.addListener(handleWebSocketMessage);
    return () => wsService.removeListener(handleWebSocketMessage);
  }, [wsService]);

  return (
    <div style={{ padding: "10px", border: "1px solid #ddd", borderRadius: "5px", marginTop: "20px" }}>
      <h2>🔔 Notifications</h2>
      {notifications.length === 0 ? (
        <p>No notifications.</p>
      ) : (
        notifications.map((notif, index) => (
          <Notification
            key={notif.id || index} // Use `id` if available, otherwise fallback to `index`
            message={notif.message}
            id={notif.id}
            type={notif.notif_type}
            timestamp={new Date(notif.timestamp).toLocaleString()}
          />
        ))
      )}
    </div>
  );
}
