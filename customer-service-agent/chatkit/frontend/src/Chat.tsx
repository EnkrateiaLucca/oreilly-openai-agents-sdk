import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function Chat({ apiKey, onClearKey }: { apiKey: string; onClearKey: () => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    // Add placeholder for assistant response
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          api_key: apiKey,
          history: messages,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: `Error: ${err.error || "Something went wrong"}`,
          };
          return updated;
        });
        setIsStreaming(false);
        return;
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No reader");

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6);
          if (data === "[DONE]") continue;

          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: `Error: ${parsed.error}`,
                };
                return updated;
              });
            } else if (parsed.text) {
              // `text` is the full message so far (not incremental)
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  content: parsed.text,
                };
                return updated;
              });
            }
          } catch {
            // skip malformed JSON
          }
        }
      }
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : "Connection failed";
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: `Error: ${errMsg}`,
        };
        return updated;
      });
    }

    setIsStreaming(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        background: "#f1f5f9",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Header */}
      <header
        style={{
          width: "100%",
          maxWidth: "720px",
          padding: "16px 24px 8px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "28px" }}>🎧</span>
          <div>
            <h1 style={{ fontSize: "20px", fontWeight: 600, lineHeight: 1.2, color: "#1e293b" }}>
              Customer Service Agent
            </h1>
            <p style={{ fontSize: "13px", color: "#64748b" }}>
              Powered by OpenAI Agents SDK
            </p>
          </div>
        </div>
        <button
          onClick={onClearKey}
          style={{
            background: "none",
            border: "1px solid #cbd5e1",
            borderRadius: "8px",
            padding: "6px 12px",
            fontSize: "12px",
            color: "#64748b",
            cursor: "pointer",
          }}
        >
          Change API Key
        </button>
      </header>

      {/* Messages area */}
      <div
        style={{
          width: "100%",
          maxWidth: "720px",
          flex: 1,
          overflowY: "auto",
          padding: "16px 24px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "#94a3b8",
              gap: "12px",
            }}
          >
            <span style={{ fontSize: "48px" }}>🎧</span>
            <p style={{ fontSize: "15px" }}>How can we help you today?</p>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "center", marginTop: "8px" }}>
              {["What are my orders?", "I want a refund for ORD-001", "Where is my package?"].map(
                (suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setInput(suggestion);
                    }}
                    style={{
                      background: "#fff",
                      border: "1px solid #e2e8f0",
                      borderRadius: "20px",
                      padding: "8px 16px",
                      fontSize: "13px",
                      color: "#475569",
                      cursor: "pointer",
                    }}
                  >
                    {suggestion}
                  </button>
                )
              )}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                maxWidth: "80%",
                padding: "12px 16px",
                borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                background: msg.role === "user" ? "#0f172a" : "#fff",
                color: msg.role === "user" ? "#fff" : "#1e293b",
                fontSize: "14px",
                lineHeight: 1.6,
                boxShadow: msg.role === "assistant" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.content || (isStreaming && i === messages.length - 1 ? "..." : "")}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div
        style={{
          width: "100%",
          maxWidth: "720px",
          padding: "12px 24px 24px",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "8px",
            background: "#fff",
            borderRadius: "16px",
            padding: "8px 8px 8px 16px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            border: "1px solid #e2e8f0",
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={isStreaming}
            autoFocus
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              fontSize: "14px",
              background: "transparent",
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isStreaming}
            style={{
              background: input.trim() && !isStreaming ? "#0f172a" : "#cbd5e1",
              color: "#fff",
              border: "none",
              borderRadius: "10px",
              padding: "8px 16px",
              fontSize: "14px",
              fontWeight: 600,
              cursor: input.trim() && !isStreaming ? "pointer" : "not-allowed",
            }}
          >
            {isStreaming ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
