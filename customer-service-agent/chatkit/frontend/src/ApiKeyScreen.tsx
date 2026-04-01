import { useState } from "react";

export function ApiKeyScreen({ onSubmit }: { onSubmit: (key: string) => void }) {
  const [key, setKey] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (key.trim()) onSubmit(key.trim());
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f1f5f9",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          borderRadius: "16px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          padding: "40px",
          maxWidth: "440px",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <span style={{ fontSize: "40px" }}>🎧</span>
          <h1 style={{ fontSize: "22px", fontWeight: 600, color: "#1e293b", marginTop: "12px" }}>
            Customer Service Agent
          </h1>
          <p style={{ fontSize: "14px", color: "#64748b", marginTop: "4px" }}>
            Enter your OpenAI API key to start chatting
          </p>
        </div>

        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="sk-..."
          autoFocus
          style={{
            width: "100%",
            padding: "12px 16px",
            fontSize: "14px",
            border: "1px solid #cbd5e1",
            borderRadius: "10px",
            outline: "none",
            boxSizing: "border-box",
            fontFamily: "monospace",
          }}
        />

        <button
          type="submit"
          disabled={!key.trim()}
          style={{
            width: "100%",
            padding: "12px",
            fontSize: "15px",
            fontWeight: 600,
            background: key.trim() ? "#0f172a" : "#cbd5e1",
            color: "#fff",
            border: "none",
            borderRadius: "10px",
            cursor: key.trim() ? "pointer" : "not-allowed",
          }}
        >
          Start Chat
        </button>

        <p style={{ fontSize: "12px", color: "#94a3b8", textAlign: "center", lineHeight: 1.5 }}>
          Your key is stored in your browser only and sent directly to OpenAI.{" "}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#64748b" }}
          >
            Get an API key
          </a>
        </p>
      </form>
    </div>
  );
}
