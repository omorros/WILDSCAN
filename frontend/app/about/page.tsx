"use client";

import React from 'react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-300 font-sans selection:bg-green-500">
      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-gray-800 bg-[#0d1117] sticky top-0 z-50">
        <div className="text-xl font-bold tracking-tighter text-white">WILDSCAN</div>
        <div className="space-x-8 text-xs uppercase tracking-widest font-medium">
          <Link href="/" className="hover:text-green-400 transition-colors">Home</Link>
          <Link href="/search" className="hover:text-green-400 transition-colors">Search</Link>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-16 px-6 lg:px-8">
        {/* Header Section */}
        <header className="mb-16 border-l-4 border-green-500 pl-6">
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
            WILDSCAN
          </h1>
          <p className="text-green-500 font-mono text-sm tracking-widest uppercase">
            Product Requirements Document // Version 3.0
          </p>
          <div className="mt-4 flex flex-wrap gap-4 text-xs font-mono text-gray-500">
            <span>Track: Web MCP Agents</span>
            <span>|</span>
            <span>Powered by Bright Data</span>
          </div>
        </header>

        {/* Section 1: Problem Statement */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-green-500 mr-2">01.</span> Problem Statement
          </h2>
          <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800 leading-relaxed">
            <p className="mb-4">
              Wildlife trafficking is a <span className="text-white font-semibold">$23B criminal enterprise</span> that has moved online. 
              Sellers trade ivory, pangolin scales, and rhino horn across geo-restricted marketplaces using local languages 
              and evolving code words.
            </p>
            <p className="text-sm text-gray-400 italic border-l-2 border-gray-700 pl-4">
              "The geo-proxy requirement is absolute: you cannot access Thai OLX or Vietnamese Facebook Marketplace from a UK or US IP."
            </p>
          </div>
        </section>

        {/* Section 2: Multi-Model Strategy Table */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-green-500 mr-2">02.</span> Multi-Model Strategy
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse bg-gray-900/30 rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-gray-800/50 text-white text-xs uppercase tracking-wider">
                  <th className="p-4 border-b border-gray-700">Task</th>
                  <th className="p-4 border-b border-gray-700">Model</th>
                  <th className="p-4 border-b border-gray-700">Why</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr className="border-b border-gray-800">
                  <td className="p-4 font-semibold text-green-400">Vision</td>
                  <td className="p-4">GPT-4o Vision</td>
                  <td className="p-4 text-gray-400">Superior fine-grained object identification.</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="p-4 font-semibold text-green-400">Translation</td>
                  <td className="p-4">GPT-4o</td>
                  <td className="p-4 text-gray-400">Stronger multilingual performance (Thai, VN, Burmese).</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="p-4 font-semibold text-green-400">Reasoning</td>
                  <td className="p-4">Claude Sonnet</td>
                  <td className="p-4 text-gray-400">Better nuanced contextual reasoning and calibration.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 3: System Architecture (ASCII Card) */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-green-500 mr-2">03.</span> Architecture
          </h2>
          <pre className="bg-black p-6 rounded-lg border border-green-900/30 text-[10px] md:text-xs text-green-500 overflow-x-auto font-mono leading-tight">
{`┌──────────────────────────────────────────────────┐
│             BRIGHT DATA PROXY LAYER              │
├──────────────────────────────────────────────────┤
│ TH Proxy ──→ OLX.th, FB Marketplace TH           │
│ VN Proxy ──→ Chợ Tốt, FB Marketplace VN          │
└────────────────────────┬─────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────┐
│           AGENT PIPELINE (LangGraph)             │
├────────────┬───────────┬────────────┬────────────┤
│  Scanner   │  Triage   │ Linguist   │   Vision   │
│ (Bright)   │ (Regex)   │ (Claude)   │  (GPT-4o)  │
└────────────┴─────┬─────┴────────────┴────────────┘
                   │
┌──────────────────▼──────────────────┐
│       RISK SCORER (8 Signals)       │
└─────────────────────────────────────┘`}
          </pre>
        </section>

        {/* Section 4: Data Sources */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="text-green-500 mr-2">04.</span> Critical Data Sources
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <h4 className="text-white font-bold mb-1">Species+ Checklist API</h4>
              <p className="text-xs text-gray-400">Maps species to CITES appendix (I/II/III) and trade bans.</p>
            </div>
            <div className="p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <h4 className="text-white font-bold mb-1">IUCN Red List API</h4>
              <p className="text-xs text-gray-400">Conservation status and population threat trends.</p>
            </div>
          </div>
        </section>

        {/* Footer Navigation */}
        <footer className="mt-20 pt-8 border-t border-gray-800 text-center">
          <p className="text-gray-500 text-sm mb-6">Ready to see the system in action?</p>
          <Link 
            href="/search" 
            className="px-8 py-3 bg-green-600 hover:bg-green-500 text-white font-bold rounded-full transition-all uppercase tracking-widest text-xs"
          >
            Launch Search Interface
          </Link>
        </footer>
      </main>
    </div>
  );
}
