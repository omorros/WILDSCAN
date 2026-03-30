"use client";

import { useEffect, useState } from "react";
import { DetectionDetail } from "@/types/detection";
import SignalBreakdown from "./SignalBreakdown";
import IntelBrief from "./IntelBrief";

const API = "http://localhost:8000";

const TIER_LABELS: Record<string, { label: string; color: string }> = {
  red: { label: "RED ALERT", color: "text-red-500" },
  amber: { label: "AMBER ALERT", color: "text-orange-500" },
  yellow: { label: "YELLOW FLAG", color: "text-yellow-400" },
  clear: { label: "CLEAR", color: "text-green-500" },
};

const TIER_DOT: Record<string, string> = {
  red: "bg-red-500",
  amber: "bg-orange-500",
  yellow: "bg-yellow-400",
  clear: "bg-green-500",
};

interface DetailPanelProps {
  detectionId: string;
  onClose: () => void;
}

export default function DetailPanel({ detectionId, onClose }: DetailPanelProps) {
  const [detail, setDetail] = useState<DetectionDetail | null>(null);
  const [error, setError] = useState(false);
  const [zoomedImage, setZoomedImage] = useState<string | null>(null);

  useEffect(() => {
    setDetail(null);
    setError(false);
    fetch(`${API}/api/detections/${detectionId}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          setError(true);
        } else {
          // Normalize brief: API returns full_brief as nested JSONB
          if (data.brief?.full_brief) {
            data.brief = { ...data.brief.full_brief, ...{ executive_summary: data.brief.executive_summary || data.brief.full_brief.executive_summary, recommended_actions: data.brief.recommended_actions || data.brief.full_brief.recommended_actions } };
          }
          // Ensure arrays are never null
          data.species_matches = data.species_matches || [];
          data.code_word_matches = data.code_word_matches || [];
          data.seizure_correlations = data.seizure_correlations || [];
          data.images = data.images || [];
          data.images_local = data.images_local || [];
          setDetail(data);
        }
      })
      .catch(() => setError(true));
  }, [detectionId]);

  if (error) {
    return (
      <aside className="w-[420px] h-full bg-[#0d1117] border-l border-green-900/30 flex flex-col items-center justify-center">
        <p className="text-gray-500 text-xs font-mono">Failed to load detection</p>
        <button onClick={() => setError(false)} className="text-green-400 text-xs font-mono mt-2 underline">Retry</button>
      </aside>
    );
  }

  if (!detail) {
    return (
      <aside className="w-[420px] h-full bg-[#0d1117] border-l border-green-900/30 flex items-center justify-center">
        <p className="text-gray-500 text-xs font-mono animate-pulse">Loading...</p>
      </aside>
    );
  }

  const tier = TIER_LABELS[detail.alert_tier] || TIER_LABELS.clear;
  const images = detail.images.length > 0 ? detail.images : detail.images_local;
  const topSpecies = detail.species_matches[0] || null;

  return (
    <aside className="w-[420px] h-full bg-[#0d1117] border-l border-green-900/30 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-green-900/30 flex items-start justify-between shrink-0">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${TIER_DOT[detail.alert_tier]}`} />
            <span className="text-[10px] font-mono uppercase tracking-wider text-gray-500 bg-[#161b22] px-2 py-0.5 rounded">
              {detail.platform}
            </span>
          </div>
          <h2 className="text-sm font-medium text-white truncate">
            {detail.title_translated || detail.title_original}
          </h2>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors text-lg shrink-0 ml-2">×</button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Images */}
        {images.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-2">
            {images.map((src, i) => {
              const url = src.startsWith("/") ? `${API}${src}` : src;
              return (
                <img
                  key={i}
                  src={url}
                  alt=""
                  onClick={() => setZoomedImage(url)}
                  className="h-24 w-auto rounded-lg border border-green-900/30 object-cover shrink-0 cursor-zoom-in hover:border-green-500/50 transition-colors"
                />
              );
            })}
          </div>
        )}

        {/* Image Zoom Overlay */}
        {zoomedImage && (
          <div
            className="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center cursor-zoom-out"
            onClick={() => setZoomedImage(null)}
          >
            <img
              src={zoomedImage}
              alt=""
              className="max-w-[90vw] max-h-[90vh] object-contain rounded-lg"
            />
          </div>
        )}

        {/* Risk Score */}
        <div className="flex items-baseline gap-3">
          <span className={`text-4xl font-black font-mono tabular-nums ${tier.color}`}>
            {detail.risk_score}
          </span>
          <span className={`text-xs font-mono uppercase tracking-widest ${tier.color}`}>
            {tier.label}
          </span>
        </div>

        {/* Signal Breakdown */}
        {detail.signal_breakdown && Object.keys(detail.signal_breakdown).length > 0 && (
          <SignalBreakdown breakdown={detail.signal_breakdown} />
        )}

        {/* Species Match */}
        {topSpecies && (
          <div>
            <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono mb-2">Species Match</h4>
            <div className="bg-[#161b22] border border-green-900/30 rounded-lg p-3 space-y-1">
              <p className="text-sm text-white font-medium">{topSpecies.common_name}</p>
              <p className="text-xs text-gray-400 italic">{topSpecies.scientific_name}</p>
              <div className="flex gap-2 mt-2 flex-wrap">
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-red-950 text-red-400 uppercase">
                  CITES {topSpecies.cites_appendix}
                </span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-orange-950 text-orange-400 uppercase">
                  IUCN {topSpecies.iucn_status}
                </span>
                {topSpecies.trade_suspension_active && (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-red-950 text-red-400 uppercase">
                    Trade Suspended
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Code Word Matches */}
        {detail.code_word_matches.length > 0 && (
          <div>
            <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono mb-2">Code Words Detected</h4>
            <div className="flex gap-2 flex-wrap">
              {detail.code_word_matches.map((cw, i) => (
                <span
                  key={i}
                  className="text-[10px] font-mono px-2 py-1 rounded-lg bg-[#161b22] border border-green-900/30 text-green-400"
                >
                  {cw.code_word}
                  <span className="text-gray-600 ml-1.5">{cw.match_type}</span>
                  <span className="text-gray-600 ml-1">{Math.round(cw.confidence * 100)}%</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Geographic Risk */}
        {detail.geographic_risk && (
          <div>
            <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono mb-2">Geographic Risk</h4>
            <div className="text-xs text-gray-400 space-y-1">
              <p>{detail.geographic_risk.reasoning}</p>
              <div className="flex gap-3 text-[10px] font-mono">
                <span className={detail.geographic_risk.legal_trade_possible ? "text-green-400" : "text-red-400"}>
                  Legal trade: {detail.geographic_risk.legal_trade_possible ? "possible" : "no"}
                </span>
                <span className="text-gray-500">
                  {detail.geographic_risk.supporting_seizures} prior seizures
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Seizure Correlations */}
        {detail.seizure_correlations.length > 0 && (
          <div>
            <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono mb-2">Seizure History</h4>
            <div className="space-y-1">
              {detail.seizure_correlations.slice(0, 5).map((s, i) => (
                <div key={i} className="flex justify-between text-[10px] font-mono text-gray-400">
                  <span>{s.country} · {s.product_type}</span>
                  <span>{s.quantity} {s.quantity_unit} · {s.date}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Intel Brief + Chat */}
        <IntelBrief detectionId={detectionId} brief={detail.brief} />
      </div>
    </aside>
  );
}
