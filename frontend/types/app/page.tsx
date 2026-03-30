"use client";

import React from "react";
import Link from "next/link";

const PIPELINE_AGENTS = [
  { name: "Scanner", desc: "Bright Data MCP", icon: "⌁" },
  { name: "Triage", desc: "Noise Filter", icon: "⊘" },
  { name: "Linguist", desc: "8 Languages", icon: "⟟", parallel: true },
  { name: "Vision", desc: "Image Analysis", icon: "◎", parallel: true },
  { name: "Species ID", desc: "CITES / IUCN", icon: "⧈" },
  { name: "Risk Scorer", desc: "8-Signal Score", icon: "⬡" },
];

export default function WildScanLanding() {
  return (
    <div className="h-screen bg-black text-white font-sans selection:bg-green-500 flex flex-col overflow-hidden">
      {/* Minimal Nav */}
      <nav className="flex items-center px-8 py-5 w-full z-50">
        <div className="text-xl font-bold tracking-tighter font-mono">
          WILDSCAN<span className="text-green-500">_</span>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center relative">
        {/* Animated Globe */}
        <div className="absolute w-[420px] h-[420px] opacity-20 flex items-center justify-center pointer-events-none">
          <div className="absolute w-full h-full rounded-full border-2 border-dashed border-green-500 animate-[spin_20s_linear_infinite]" />
          <div className="absolute w-[70%] h-[70%] rounded-full border border-green-800 animate-[spin_10s_linear_infinite_reverse]" />
          <div className="absolute w-[40%] h-[40%] rounded-full bg-green-500/10 animate-pulse" />
        </div>

        {/* Content */}
        <div className="z-10 text-center px-4">
          <h1 className="text-7xl md:text-9xl font-black tracking-tighter mb-3 drop-shadow-[0_0_15px_rgba(34,197,94,0.3)]">
            WILDSCAN
          </h1>
          <p className="text-gray-500 mb-8 tracking-[0.15em] uppercase text-[11px] md:text-xs font-mono">
            Autonomous Multi-Agent Wildlife Trafficking Detection Network
          </p>

          {/* Capability Stats */}
          <div className="flex items-center justify-center gap-8 mb-10 font-mono text-[11px] tracking-wider uppercase">
            <StatBlock label="Agents" value={6} color="text-green-400" />
            <StatBlock label="Risk Signals" value={8} color="text-green-400" />
            <StatBlock label="Languages" value={8} color="text-green-400" />
            <StatBlock label="Species DB" value={"200+"} color="text-green-400" />
          </div>

          <Link
            href="/search"
            className="inline-block px-10 py-3.5 bg-white text-black font-bold rounded-full hover:bg-green-500 hover:text-white transition-all duration-300 transform hover:scale-105 active:scale-95 uppercase tracking-widest text-xs"
          >
            Enter Command Center
          </Link>
        </div>
      </main>

      {/* Agent Pipeline */}
      <section className="w-full px-6 pb-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-[10px] text-gray-600 uppercase tracking-[0.2em] font-mono mb-3 text-center">
            6-Agent Detection Pipeline
          </p>
          <div className="flex items-center justify-center gap-0">
            {PIPELINE_AGENTS.map((agent, i) => (
              <React.Fragment key={agent.name}>
                {/* Connector */}
                {i > 0 && (
                  <div className="flex items-center">
                    {/* Fork visual for parallel agents */}
                    {agent.parallel && i === 3 ? (
                      <div className="w-4 h-px bg-green-900" />
                    ) : agent.parallel && i === 2 ? (
                      <>
                        <div className="w-6 flex flex-col items-center">
                          <div className="w-full h-px bg-green-900" />
                        </div>
                      </>
                    ) : (
                      <div className="w-6 flex items-center">
                        <div className="flex-1 h-px bg-green-900" />
                        <div className="text-green-800 text-[8px]">▸</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Agent Node */}
                <div
                  className={`flex flex-col items-center px-3 py-2 rounded border border-green-900/40 bg-green-950/20 min-w-[90px] ${
                    agent.parallel ? "relative" : ""
                  }`}
                >
                  <span className="text-green-500 text-lg mb-0.5">{agent.icon}</span>
                  <span className="text-[10px] font-mono text-white font-medium">
                    {agent.name}
                  </span>
                  <span className="text-[8px] font-mono text-gray-500 mt-0.5">
                    {agent.desc}
                  </span>
                </div>
              </React.Fragment>
            ))}
          </div>

          {/* Parallel bracket label */}
          <div className="flex justify-center mt-1">
            <div className="ml-[200px] flex flex-col items-center" style={{ width: "200px" }}>
              <div className="w-full flex items-center">
                <div className="flex-1 h-px bg-green-900/40" />
                <span className="text-[8px] text-gray-600 font-mono px-2">parallel</span>
                <div className="flex-1 h-px bg-green-900/40" />
              </div>
            </div>
          </div>
        </div>

        {/* Powered By */}
        <div className="flex items-center justify-center gap-4 mt-4 mb-1">
          <span className="text-[9px] text-gray-600 font-mono uppercase tracking-widest">
            Powered by Bright Data Web MCP · Claude · GPT-4o Vision
          </span>
        </div>
      </section>
    </div>
  );
}

function StatBlock({
  label,
  value,
  color,
}: {
  label: string;
  value: number | string | null;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-xl font-bold tabular-nums ${color}`}>
        {value !== null ? value : "—"}
      </span>
      <span className="text-gray-600">{label}</span>
    </div>
  );
}
