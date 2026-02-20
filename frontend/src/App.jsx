import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import AdminDashboard from "./components/AdminDashboard";

export default function App() {
  const [view, setView] = useState("chat");

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Ali Doctor</h2>
        <button onClick={() => setView("chat")}>Chat</button>
        <button onClick={() => setView("dashboard")}>Admin Dashboard</button>
      </aside>
      <main className="content">{view === "chat" ? <ChatWindow /> : <AdminDashboard />}</main>
    </div>
  );
}
