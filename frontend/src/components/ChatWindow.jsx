import { useState } from "react";
import { api } from "../api/client";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    const { data } = await api.post(
      "/chat",
      {
        employee_id: "EMP001",
        session_id: "default-session",
        message: input,
        context_window: 12
      },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` } }
    );

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: data.response },
      { role: "system", content: data.disclaimer }
    ]);
    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`bubble ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask Ali Doctor..." />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
