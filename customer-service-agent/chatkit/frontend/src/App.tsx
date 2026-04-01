import { ChatKit, useChatKit } from "@openai/chatkit-react";

export default function App() {
  const chatkit = useChatKit({
    api: {
      url: "/chatkit",
      domainKey: "domain_pk_localhost_dev",
    },
    composer: {
      placeholder: "How can we help you today?",
      attachments: { enabled: false },
    },
  });

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        background: "#f1f5f9",
      }}
    >
      {/* Header */}
      <header
        style={{
          width: "100%",
          maxWidth: "960px",
          padding: "16px 24px 8px",
          display: "flex",
          alignItems: "center",
          gap: "12px",
        }}
      >
        <span style={{ fontSize: "28px" }}>🎧</span>
        <div>
          <h1 style={{ fontSize: "20px", fontWeight: 600, lineHeight: 1.2, color: "#1e293b" }}>
            Customer Service Agent
          </h1>
          <p style={{ fontSize: "13px", color: "#64748b" }}>
            Powered by OpenAI Agents SDK + ChatKit
          </p>
        </div>
      </header>

      {/* ChatKit panel — matches starter app pattern */}
      <div
        style={{
          width: "100%",
          maxWidth: "960px",
          height: "85vh",
          borderRadius: "16px",
          overflow: "hidden",
          background: "#fff",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          marginBottom: "32px",
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        <ChatKit
          control={chatkit.control}
          style={{ display: "block", height: "100%", width: "100%" }}
        />
      </div>
    </div>
  );
}
