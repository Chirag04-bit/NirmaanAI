import React, { useState, useRef, useEffect } from "react";
import { submitCopilotQuery } from "../api/client";
import "../styles/CopilotChat.css";

const QUICK_PROMPTS = [
  "What is the health of M2?",
  "Why is M2 degrading?",
  "What maintenance action is recommended for M2?",
  "What is the M2 bearing inventory status?",
  "What is M2's gross financial exposure?",
  "What bottleneck risk does M2 have?",
  "Was MAINT_0003 part of the prospective decision evidence?",
  "What is the health of M99?",
];

export default function CopilotChat() {
  const [messages, setMessages] = useState([
    {
      id: "initial-msg",
      role: "assistant",
      query: null,
      answer: "Hello, I am the NirmaanAI Grounded Factory Copilot. I provide evidence-backed decision support across plant topology, machine health, predictive failure risk, root causes, inventory buffers, and financial exposures grounded in Phase 3–20 verified analytics. Ask an operational question or select a quick prompt below.",
      confidence: "HIGH",
      epistemic_status: "DERIVED",
      sources: ["Phase 19 Factory Knowledge Memory"],
      limitations: ["Answers strictly derived from approved factory telemetry and analytical models."],
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (queryText) => {
    const q = (queryText || inputQuery).trim();
    if (!q) return;

    const userMessageId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      { id: userMessageId, role: "user", text: q },
    ];
    setMessages(newMessages);
    setInputQuery("");
    setLoading(true);

    try {
      const response = await submitCopilotQuery(q);
      setMessages([
        ...newMessages,
        {
          id: `bot-${Date.now()}`,
          role: "assistant",
          query: q,
          ...response,
        },
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          id: `bot-err-${Date.now()}`,
          role: "assistant",
          query: q,
          answer: "An unexpected error occurred while communicating with the Copilot inference service.",
          status: "NO_SUFFICIENT_EVIDENCE",
          confidence: "NO_EVIDENCE",
          epistemic_status: "UNKNOWN",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="copilot-section" id="copilot-section">
      <div className="section-header">
        <div>
          <h2 className="section-title">AI Factory Copilot (Grounded RAG Interface)</h2>
          <p className="section-subtitle">Grounded decision support with provenance citations and epistemic bounds</p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-epistemic">PHASE 20 SUBSYSTEM</span>
          <span className="badge badge-info">FASTAPI /api/v1/copilot/ask</span>
        </div>
      </div>

      <div className="glass-card copilot-container" id="copilot-chat-container">
        {/* Quick Prompts Bar */}
        <div className="quick-prompts-bar">
          <span className="quick-prompts-label">QUICK VERIFICATION QUERIES:</span>
          <div className="quick-chips-wrapper">
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                id={`copilot-chip-${idx}`}
                className="prompt-chip"
                onClick={() => handleSend(prompt)}
                disabled={loading}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Message Thread */}
        <div className="messages-thread" id="copilot-messages-thread">
          {messages.map((msg) => {
            const isUser = msg.role === "user";

            return (
              <div
                key={msg.id}
                className={`chat-message ${isUser ? "user-message" : "bot-message"}`}
              >
                <div className="message-header">
                  <span className="sender-tag mono">{isUser ? "PLANT OPERATOR" : "NIRMAAN COPILOT"}</span>
                  {!isUser && msg.epistemic_status && (
                    <span className="badge badge-epistemic">{msg.epistemic_status}</span>
                  )}
                  {!isUser && msg.confidence && (
                    <span className={`badge ${msg.confidence === "HIGH" ? "badge-healthy" : msg.confidence === "MEDIUM" ? "badge-info" : "badge-warning"}`}>
                      CONFIDENCE: {msg.confidence}
                    </span>
                  )}
                </div>

                <div className="message-body">
                  <p>{isUser ? msg.text : msg.answer}</p>
                </div>

                {/* Sources & Citations Tray */}
                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <div className="citations-tray">
                    <span className="citations-label">Grounded Sources:</span>
                    <div className="citations-list">
                      {msg.sources.map((src, i) => (
                        <span key={i} className="citation-pill mono">
                          📚 {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Explicit Limitations Tray */}
                {!isUser && msg.limitations && msg.limitations.length > 0 && (
                  <div className="limitations-tray">
                    <span className="limitations-label">Epistemic Limitations &amp; Boundary:</span>
                    <ul className="limitations-list">
                      {msg.limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
          {loading && (
            <div className="chat-message bot-message loading-indicator">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="mono text-muted" style={{ fontSize: "12px", marginLeft: "12px" }}>
                Retrieving Phase 19 Knowledge Chunks &amp; Verifying Provenance...
              </span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-bar"
          id="copilot-input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            id="copilot-query-input"
            className="chat-input"
            placeholder="Ask anything about machine health, root causes, inventory, or financial losses..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            id="copilot-send-button"
            className="btn btn-primary chat-send-btn"
            disabled={loading || !inputQuery.trim()}
          >
            {loading ? "Searching..." : "Ask Copilot →"}
          </button>
        </form>
      </div>
    </section>
  );
}
