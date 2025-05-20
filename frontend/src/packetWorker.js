import { io } from "socket.io-client";

let socket = null;

self.onmessage = (e) => {
  const { type } = e.data;
  if (type === "START") {
    socket = io("/", { transports: ["websocket"] });
    socket.on("connect", () => self.postMessage({ type: "WS_CONNECTED" }));
    socket.on("packet", (pkt) => {
      self.postMessage(pkt);
    });
    socket.on("disconnect", () => {
      self.postMessage({ type: "CLOSED" });
    });
  } else if (type === "STOP" && socket) {
    socket.disconnect();
  }
};
