"use client";

import { useState, useRef } from "react";
import { IntelBrief as IntelBriefType } from "@/types/detection";

const API = "http://localhost:8000";

interface IntelBriefProps {
  detectionId: string;
  brief: IntelBriefType | null;
}

export default function IntelBrief({ detectionId, brief: initialBrief }: IntelBriefProps) {
  const [brief, setBrief] = useState<IntelBriefType | null>(initialBrief);
  const [generating, setGenerating] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<{ role: string; content: string }[]>([]);
  const [streaming, setStreaming] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  async function generateBrief() {
    setGenerating(true);
    try {
      const res = await fetch(`${API}/api/intel/brief/${detectionId}`, { method: "POST" });
      const data = await res.json();
      if (!data.error) setBrief(data);
    } catch {
      // silent fail
    }
    setGenerating(false);
  }

  async function sendChat() {
    if (!chatInput.trim() || streaming) return;
    const question = chatInput;
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", content: question }]);
    setStreaming(true);

    try {
      const res = await fetch(`${API}/api/intel/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          detection_id: detectionId,
          question,
          chat_history: chatMessages,
        }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = "";

      setChatMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ") && line !== "data: [DONE]") {
              try {
                const parsed = JSON.parse(line.slice(6));
                assistantMsg += parsed.text;
                setChatMessages((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { role: "assistant", content: assistantMsg };
                  return updated;
                });
              } catch {
                // skip malformed chunks
              }
            }
          }
        }
      }
    } catch {
      setChatMessages((prev) => [...prev, { role: "assistant", content: "Failed to connect." }]);
    }
    setStreaming(false);
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="space-y-4">
      <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">Intelligence Brief</h4>

      {!brief && !generating && (
        <button
          onClick={generateBrief}
          className="w-full py-2 px-4 bg-green-950/40 border border-green-900/30 rounded-lg text-green-400 text-xs font-mono uppercase tracking-wider hover:bg-green-900/30 transition-colors"
        >
          Generate Intel Brief
        </button>
      )}

      {generating && (
        <div className="text-xs text-gray-500 font-mono animate-pulse">Generating brief with Claude...</div>
      )}

      {brief && (
        <div className="space-y-3 text-xs">
          <div>
            <span className="text-gray-500 font-mono text-[10px] uppercase">Summary</span>
            <p className="text-gray-300 mt-1">{brief.executive_summary}</p>
          </div>

          {brief.key_evidence?.length > 0 && (
            <div>
              <span className="text-gray-500 font-mono text-[10px] uppercase">Key Evidence</span>
              <ul className="mt-1 space-y-1">
                {brief.key_evidence.map((e, i) => (
                  <li key={i} className="text-gray-400 flex gap-2">
                    <span className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded ${
                      e.confidence === "high" ? "bg-red-950 text-red-400" : "bg-yellow-950 text-yellow-400"
                    }`}>{e.confidence}</span>
                    <span>{e.description}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {brief.recommended_actions?.length > 0 && (
            <div>
              <span className="text-gray-500 font-mono text-[10px] uppercase">Recommended Actions</span>
              <ul className="mt-1 space-y-1">
                {brief.recommended_actions.map((a, i) => (
                  <li key={i} className="text-gray-400 text-xs">→ {a}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono pt-2 border-t border-green-900/30">
        Ask About This Case
      </h4>

      {chatMessages.length > 0 && (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {chatMessages.map((msg, i) => (
            <div key={i} className={`text-xs ${msg.role === "user" ? "text-green-400" : "text-gray-400"}`}>
              <span className="font-mono text-[9px] text-gray-600 uppercase">{msg.role === "user" ? "You" : "Intel"}: </span>
              {msg.content}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendChat()}
          placeholder="Ask about this case..."
          className="flex-1 bg-[#161b22] border border-green-900/30 rounded-lg px-3 py-2 text-xs text-white font-mono placeholder:text-gray-600 focus:outline-none focus:border-green-500/50"
        />
        <button
          onClick={sendChat}
          disabled={streaming || !chatInput.trim()}
          className="px-3 py-2 bg-green-950/40 border border-green-900/30 rounded-lg text-green-400 text-xs font-mono hover:bg-green-900/30 transition-colors disabled:opacity-30"
        >
          →
        </button>
      </div>
    </div>
  );
}
