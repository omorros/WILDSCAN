"use client";

import type { AnimatingDetection } from "@/app/search/page";

const TIER_COLORS: Record<string, string> = {
  red: "bg-red-500",
  amber: "bg-orange-500",
  yellow: "bg-yellow-400",
  clear: "bg-green-500",
};

const TIER_TEXT: Record<string, string> = {
  red: "text-red-400",
  amber: "text-orange-400",
  yellow: "text-yellow-400",
  clear: "text-green-400",
};

const TIER_LABEL: Record<string, string> = {
  red: "RED ALERT",
  amber: "AMBER ALERT",
  yellow: "YELLOW",
  clear: "CLEAR",
};

function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

interface DetectionCardProps {
  detection: AnimatingDetection;
  isActive: boolean;
  onSelect: () => void;
}

export default function DetectionCard({ detection, isActive, onSelect }: DetectionCardProps) {
  const stage = detection.animationStage;

  // Stage 1: Scanning
  if (stage === "scanning") {
    return (
      <div className="p-4 bg-[#161b22] border border-green-900/50 rounded-xl animate-slide-in-left">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shrink-0" />
          <span className="text-green-500 font-mono text-xs uppercase tracking-wider animate-pulse">Scanning</span>
        </div>
      </div>
    );
  }

  // Stage 2: Analyzing
  if (stage === "analyzing") {
    const codeWords = detection.code_word_count || 0;
    const product = detection.image_product || "suspicious item";
    return (
      <div className="p-4 bg-[#161b22] border border-yellow-900/50 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-yellow-400 shrink-0" />
          <span className="text-yellow-400 font-mono text-xs">
            {codeWords} code word{codeWords !== 1 ? "s" : ""} / {product}
          </span>
        </div>
      </div>
    );
  }

  // Stage 3: Scored (final reveal before settling)
  if (stage === "scored") {
    return (
      <div className={`p-4 bg-[#161b22] border rounded-xl ${
        detection.alert_tier === "red" ? "border-red-500/70" :
        detection.alert_tier === "amber" ? "border-orange-500/70" :
        "border-yellow-500/70"
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full shrink-0 ${TIER_COLORS[detection.alert_tier]}`} />
          <span className={`font-mono text-sm font-bold ${TIER_TEXT[detection.alert_tier]}`}>
            {detection.risk_score} {TIER_LABEL[detection.alert_tier]}
          </span>
        </div>
        {detection.species && (
          <p className="text-[10px] text-gray-400 font-mono mt-1 pl-[22px]">
            {detection.species}{detection.cites_appendix ? ` (CITES ${detection.cites_appendix})` : ""}
          </p>
        )}
      </div>
    );
  }

  // Settled / normal state (identical to original design)
  return (
    <div
      onClick={onSelect}
      className={`group p-4 bg-[#161b22] border border-green-900/30 rounded-xl cursor-pointer hover:border-green-500/50 transition-all ${
        isActive ? "ring-2 ring-green-500 ring-offset-2 ring-offset-[#0d1117]" : ""
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${TIER_COLORS[detection.alert_tier]}`} />
          <h3 className="font-medium text-sm text-[#e6edf3] truncate group-hover:text-green-400">
            {detection.title}
          </h3>
        </div>
        <span className={`text-sm font-bold font-mono tabular-nums shrink-0 ml-2 ${TIER_TEXT[detection.alert_tier]}`}>
          {detection.risk_score}
        </span>
      </div>

      <div className="text-[10px] text-gray-500 font-mono space-y-1 pl-[18px]">
        <p className="uppercase tracking-wider">{detection.platform}{detection.location_text ? ` · ${detection.location_text}` : ""}</p>
        {detection.species && (
          <p className="text-gray-400">{detection.species}</p>
        )}
        {detection.post_date && (
          <p>{timeAgo(detection.post_date)}</p>
        )}
      </div>
    </div>
  );
}
