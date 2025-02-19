import React, { useEffect, useState } from "react";
import { getUserInfo } from "../api/user";
import { logout } from "../api/auth";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../components/context/WebSocketContext";

export default function DebugPage() {
  const [userInfo, setUserInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const wsService = useWebSocket();

  const [recipientId, setRecipientId] = useState("");
  const [draftbeatId, setDraftbeatId] = useState("");
  const [inviteId, setInviteId] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    getUserInfo()
      .then((data) => {
        if (data) {
          setUserInfo(data);
        } else {
          logout();
          navigate("/login");
        }
      })
      .catch((error) => {
        console.error("Error fetching user info:", error);
        logout();
        navigate("/login");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [navigate]);

  useEffect(() => {
    if (!wsService) return;

    const handleWebSocketMessage = (message) => {
      setMessages((prev) => [...prev, message]);
    };

    wsService.addListener(handleWebSocketMessage);
    return () => wsService.removeListener(handleWebSocketMessage);
  }, [wsService]);

  const sendInvite = () => {
    if (!wsService) {
      console.error("WebSocket is not connected.");
      return;
    }
    if (!recipientId || !draftbeatId) {
      alert("Recipient ID and Draft ID are required.");
      return;
    }
    wsService.sendMessage({
      action: "send_invite",
      draftbeat_id: Number(draftbeatId),
      recipient_id: Number(recipientId),
    });
    console.log(`✅ Sent invite to user ${recipientId} for draft ${draftbeatId}`);
  };

  const acceptInvite = () => {
    if (!wsService) {
      console.error("WebSocket is not connected.");
      return;
    }
    if (!inviteId) {
      alert("Invite ID is required.");
      return;
    }
    wsService.sendMessage({
      action: "accept_invite",
      invite_id: Number(inviteId),
    });
    console.log(`✅ Accepted invite ${inviteId}`);
  };

  const declineInvite = () => {
    if (!wsService) {
      console.error("WebSocket is not connected.");
      return;
    }
    if (!inviteId) {
      alert("Invite ID is required.");
      return;
    }
    wsService.sendMessage({
      action: "refuse_invite",
      invite_id: Number(inviteId),
    });
    console.log(`❌ Declined invite ${inviteId}`);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (!userInfo) {
    return null;
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>🔍 Debug Page</h1>
      <p>
        <strong>ID:</strong> {userInfo.id}
      </p>
      <p>
        <strong>Username:</strong> {userInfo.username}
      </p>
      <p>
        <strong>Email:</strong> {userInfo.email}
      </p>

      <h2>📨 Send Collaboration Invite</h2>
      <input type="number" placeholder="Recipient ID" value={recipientId} onChange={(e) => setRecipientId(e.target.value)} />
      <input type="number" placeholder="Draft ID" value={draftbeatId} onChange={(e) => setDraftbeatId(e.target.value)} />
      <button onClick={sendInvite}>Send Invite</button>

      <h2>✅ Accept or ❌ Decline Invite</h2>
      <input type="number" placeholder="Invite ID" value={inviteId} onChange={(e) => setInviteId(e.target.value)} />
      <button onClick={acceptInvite}>Accept Invite</button>
      <button onClick={declineInvite}>Decline Invite</button>

      <h2>📡 WebSocket Messages</h2>
      <div style={{ border: "1px solid #ccc", padding: "10px", maxHeight: "200px", overflowY: "auto" }}>
        {messages.length === 0 ? (
          <p>No messages received yet.</p>
        ) : (
          messages.map((msg, index) => <pre key={index}>{JSON.stringify(msg, null, 2)}</pre>)
        )}
      </div>
    </div>
  );
}
