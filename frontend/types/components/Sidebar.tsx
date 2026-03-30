"use client";

import DetectionCard from "./DetectionCard";
import { Detection } from "@/types/detection";
import type { AnimatingDetection } from "@/app/search/page";

interface SidebarProps {
  detections: AnimatingDetection[];
  totalScanned?: number;
  onSelectDetection: (d: Detection) => void;
  activeId?: string;
  loading?: boolean;
  scanning?: boolean;
  scanStatus?: string;
  onScan?: () => void;
}

export default function Sidebar({ detections, totalScanned, onSelectDetection, activeId, loading, scanning, scanStatus, onScan }: SidebarProps) {
  return (
    <aside className="w-[300px] h-full bg-[#0d1117] border-r border-green-900/30 flex flex-col z-20 shrink-0">
      <div className="p-5 border-b border-green-900/30">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-lg font-bold text-green-500 tracking-tight">Live Signals</h1>
          {onScan && (
            <button
              onClick={onScan}
              disabled={scanning}
              className={`px-3 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider transition-all ${
                scanning
                  ? "bg-green-950/40 text-green-700 border border-green-900/30 cursor-not-allowed"
                  : "bg-green-500 text-black font-bold hover:bg-green-400 active:scale-95"
              }`}
            >
              {scanning ? "Scanning..." : "Scan Thailand"}
            </button>
          )}
        </div>
        {scanStatus ? (
          <p className="text-[10px] text-gray-500 font-mono animate-pulse truncate">{scanStatus}</p>
        ) : (
          <p className="text-[10px] text-gray-600 font-mono">
            {loading ? "Connecting..." : detections.length > 0
              ? `${totalScanned ?? detections.length} scanned · ${detections.length} flagged`
              : "Press Scan Thailand to begin surveillance"}
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {detections.map((detection) => (
          <DetectionCard
            key={detection.id}
            detection={detection}
            isActive={activeId === detection.id}
            onSelect={() => onSelectDetection(detection)}
          />
        ))}
        {!loading && !scanning && detections.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-12 h-12 rounded-full border-2 border-green-900/30 flex items-center justify-center mb-4">
              <span className="text-green-500 text-xl">?</span>
            </div>
            <p className="text-xs text-gray-600 font-mono">No active surveillance</p>
            <p className="text-[10px] text-gray-700 font-mono mt-1">Click &quot;Scan Thailand&quot; to start</p>
          </div>
        )}
      </div>
    </aside>
  );
}
