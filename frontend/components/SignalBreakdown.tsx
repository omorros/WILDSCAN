"use client";

const SIGNAL_LABELS: Record<string, string> = {
  code_word: "Code Word",
  cites: "CITES",
  iucn: "IUCN",
  seizure: "Seizure",
  geographic: "Geographic",
  seller: "Seller",
  price: "Price",
  image: "Image",
};

const SIGNAL_ORDER = ["code_word", "cites", "iucn", "seizure", "geographic", "image"];

interface SignalBreakdownProps {
  breakdown: Record<string, { score: number; max: number }>;
}

export default function SignalBreakdown({ breakdown }: SignalBreakdownProps) {
  return (
    <div className="space-y-2">
      <h4 className="text-[10px] text-gray-500 uppercase tracking-widest font-mono mb-3">Signal Breakdown</h4>
      {SIGNAL_ORDER.map((key) => {
        const signal = breakdown[key];
        if (!signal) return null;
        const pct = signal.max > 0 ? (signal.score / signal.max) * 100 : 0;
        return (
          <div key={key} className="flex items-center gap-3">
            <span className="text-[10px] text-gray-400 font-mono w-20 shrink-0">{SIGNAL_LABELS[key]}</span>
            <div className="flex-1 h-2 bg-green-950/40 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  pct >= 80 ? "bg-red-500" : pct >= 50 ? "bg-orange-500" : pct > 0 ? "bg-green-500" : ""
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-[10px] text-gray-500 font-mono w-10 text-right shrink-0">
              {signal.score}/{signal.max}
            </span>
          </div>
        );
      })}
    </div>
  );
}
