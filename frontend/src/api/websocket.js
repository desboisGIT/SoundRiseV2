// /src/api/websocket.js
class WebSocketService {
  constructor(userId, token) {
    this.url = `ws://localhost:8000/ws/collaboration/${userId}/?token=${token}`;
    this.socket = null;
    this.listeners = new Set();
    this.reconnectInterval = 5000; // Reconnect every 5 seconds if disconnected
  }

  connect() {
    if (this.socket) {
      console.warn("WebSocket already connected.");
      return;
    }

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log("✅ WebSocket connected:", this.url);
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("📩 WebSocket received message:", message);
      this.notifyListeners(message);
    };

    this.socket.onclose = () => {
      console.warn("⚠️ WebSocket closed. Reconnecting in 5 seconds...");
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.socket.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
    };
  }

  addListener(callback) {
    this.listeners.add(callback);
  }

  removeListener(callback) {
    this.listeners.delete(callback);
  }

  notifyListeners(data) {
    this.listeners.forEach((callback) => callback(data));
  }

  sendMessage(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error("❌ WebSocket is not open. Unable to send message.");
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default WebSocketService;
