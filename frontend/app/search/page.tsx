"use client";

import React, { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import DetailPanel from "@/components/DetailPanel";
import { Detection, GlobeResponse } from "@/types/detection";

const MapBox = dynamic(() => import("@/components/MapBox"), {
  ssr: false,
  loading: () => <div className="flex-1 bg-[#0d1117]" />,
});

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const THAI_POSITIONS: { name: string; lat: number; lng: number }[] = [
  { name: "Bangkok", lat: 13.76, lng: 100.50 },
  { name: "Chiang Mai", lat: 18.79, lng: 98.98 },
  { name: "Chiang Rai", lat: 19.91, lng: 99.84 },
  { name: "Phuket", lat: 7.88, lng: 98.39 },
  { name: "Khon Kaen", lat: 16.43, lng: 102.82 },
  { name: "Hat Yai", lat: 7.01, lng: 100.47 },
  { name: "Nakhon Ratchasima", lat: 14.98, lng: 102.10 },
  { name: "Udon Thani", lat: 17.42, lng: 102.79 },
  { name: "Ubon Ratchathani", lat: 15.25, lng: 104.85 },
  { name: "Surat Thani", lat: 9.14, lng: 99.33 },
  { name: "Lampang", lat: 18.29, lng: 99.49 },
  { name: "Phitsanulok", lat: 16.82, lng: 100.26 },
  { name: "Kanchanaburi", lat: 14.02, lng: 99.00 },
  { name: "Rayong", lat: 12.68, lng: 101.28 },
  { name: "Trat", lat: 12.24, lng: 102.51 },
  { name: "Nakhon Si Thammarat", lat: 8.43, lng: 99.96 },
  { name: "Nan", lat: 18.78, lng: 100.77 },
  { name: "Tak", lat: 16.88, lng: 99.13 },
  { name: "Chumphon", lat: 10.49, lng: 99.18 },
  { name: "Nakhon Phanom", lat: 17.39, lng: 104.77 },
  { name: "Buriram", lat: 14.99, lng: 103.10 },
  { name: "Roi Et", lat: 16.05, lng: 103.65 },
  { name: "Krabi", lat: 8.09, lng: 98.91 },
  { name: "Prachuap Khiri Khan", lat: 11.81, lng: 99.80 },
  { name: "Chonburi", lat: 13.36, lng: 100.98 },
  { name: "Ayutthaya", lat: 14.35, lng: 100.57 },
  { name: "Saraburi", lat: 14.53, lng: 100.91 },
  { name: "Loei", lat: 17.49, lng: 101.72 },
  { name: "Sukhothai", lat: 17.01, lng: 99.82 },
  { name: "Mae Hong Son", lat: 19.30, lng: 97.97 },
  { name: "Ranong", lat: 9.97, lng: 98.64 },
  { name: "Phetchabun", lat: 16.42, lng: 101.16 },
  { name: "Nong Khai", lat: 17.88, lng: 102.74 },
  { name: "Sakon Nakhon", lat: 17.16, lng: 104.15 },
  { name: "Surin", lat: 14.88, lng: 103.49 },
  { name: "Phrae", lat: 18.14, lng: 100.14 },
  { name: "Ratchaburi", lat: 13.54, lng: 99.81 },
  { name: "Satun", lat: 6.62, lng: 100.07 },
  { name: "Narathiwat", lat: 6.43, lng: 101.82 },
  { name: "Mukdahan", lat: 16.54, lng: 104.72 },
];

function assignThaiLocation(id: string, index: number): { lat: number; lng: number; text: string } {
  const pos = THAI_POSITIONS[index % THAI_POSITIONS.length];
  return { lat: pos.lat, lng: pos.lng, text: pos.name + ", Thailand" };
}

export interface AnimatingDetection extends Detection {
  animationStage?: "scanning" | "analyzing" | "scored" | "settled";
  code_word_count?: number;
  image_product?: string;
  cites_appendix?: string;
  showOnMap?: boolean;
}

function parseDetections(detectionsData: any): AnimatingDetection[] {
  return (detectionsData.detections || []).map((d: any, i: number) => {
    const hasLocation = d.location?.lat && d.location?.lng;
    const fallback = !hasLocation ? assignThaiLocation(d.id, i) : null;
    return {
      id: d.id,
      platform: d.platform,
      title: d.title_translated || d.title_original || "Untitled",
      risk_score: d.risk_score,
      alert_tier: d.alert_tier,
      species: d.species || null,
      lat: hasLocation ? d.location.lat : fallback!.lat,
      lng: hasLocation ? d.location.lng : fallback!.lng,
      location_text: hasLocation ? d.location.text : fallback!.text,
      post_date: d.post_date || null,
      animationStage: "settled" as const,
      showOnMap: true,
    };
  });
}

export default function SearchPage() {
  const [detections, setDetections] = useState<AnimatingDetection[]>([]);
  const [routes, setRoutes] = useState<GlobeResponse["routes"] | null>(null);
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);
  const [loading, setLoading] = useState(true);

  const [scanning, setScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState("");
  const [newMarkerIds, setNewMarkerIds] = useState<Set<string>>(new Set());

  // Fetch only globe routes on mount
  useEffect(() => {
    fetch(`${API}/api/globe`)
      .then((r) => r.json())
      .then((globeData: GlobeResponse) => {
        setRoutes(globeData.routes);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSelectDetection = useCallback((d: Detection) => {
    setSelectedDetection(d);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedDetection(null);
  }, []);

  async function startScan() {
    if (scanning) return;
    setScanning(true);
    setDetections([]);
    setSelectedDetection(null);
    setScanStatus("Scanning OLX Thailand marketplace...");

    // Simulate scanning delay, then fetch all detections
    await new Promise((resolve) => setTimeout(resolve, 5000));

    try {
      const res = await fetch(`${API}/api/detections?limit=200`);
      const data = await res.json();
      const parsed = parseDetections(data);
      parsed.sort((a, b) => b.risk_score - a.risk_score);

      // Pop all markers at once
      const allIds = new Set(parsed.map((d) => d.id));
      setNewMarkerIds(allIds);
      setDetections(parsed);
      setTimeout(() => setNewMarkerIds(new Set()), 700);

      setScanning(false);
      setScanStatus(`Scan complete — ${parsed.length} detections flagged`);
      setTimeout(() => setScanStatus(""), 5000);
    } catch {
      setScanStatus("Failed to fetch detections");
      setScanning(false);
      setTimeout(() => setScanStatus(""), 5000);
    }
  }

  return (
    <div className="flex flex-col h-screen w-full overflow-hidden bg-[#0d1117]">
      <nav className="flex items-center justify-between px-8 py-3 border-b border-green-900/30 bg-[#0d1117] z-50 shrink-0">
        <Link
          href="/"
          className="text-xl font-bold tracking-tighter text-white font-mono hover:opacity-80 transition-opacity"
        >
          WILDSCAN<span className="text-green-500">_</span>
        </Link>
        <div className="text-xs uppercase tracking-widest font-medium font-mono text-gray-500">
          <Link href="/" className="hover:text-green-400 transition-colors">Home</Link>
        </div>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          detections={detections}
          totalScanned={detections.length}
          onSelectDetection={handleSelectDetection}
          activeId={selectedDetection?.id}
          loading={loading}
          scanning={scanning}
          scanStatus={scanStatus}
          onScan={startScan}
        />

        <section className="relative flex-1">
          <MapBox
            detections={detections}
            selectedDetection={selectedDetection}
            routes={routes}
            onMarkerClick={handleSelectDetection}
            scanning={scanning}
            newMarkerIds={newMarkerIds}
          />
        </section>

        {selectedDetection && (
          <DetailPanel
            detectionId={selectedDetection.id}
            onClose={handleCloseDetail}
          />
        )}
      </div>
    </div>
  );
}
