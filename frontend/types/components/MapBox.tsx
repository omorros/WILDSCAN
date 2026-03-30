"use client";

import React, { useState, useEffect, useRef } from "react";
import Map, { Marker, NavigationControl, Source, Layer, MapRef } from "react-map-gl/mapbox";
import { Detection, GlobeResponse } from "@/types/detection";
import "mapbox-gl/dist/mapbox-gl.css";

const TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

const TIER_MARKER_COLOR: Record<string, string> = {
  red: "bg-red-500",
  amber: "bg-orange-500",
  yellow: "bg-yellow-400",
  clear: "bg-green-500",
};

interface MapBoxProps {
  detections: Detection[];
  selectedDetection: Detection | null;
  routes: GlobeResponse["routes"] | null;
  onMarkerClick: (d: Detection) => void;
  scanning?: boolean;
  newMarkerIds?: Set<string>;
}

export default function MapBox({ detections, selectedDetection, routes, onMarkerClick, scanning, newMarkerIds }: MapBoxProps) {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState({
    longitude: 101,
    latitude: 13.5,
    zoom: 5,
  });

  // Fly-to on selection — but NOT during scan
  useEffect(() => {
    if (scanning) return;
    if (selectedDetection?.lat && selectedDetection?.lng && mapRef.current) {
      mapRef.current.flyTo({
        center: [selectedDetection.lng, selectedDetection.lat],
        zoom: 6,
        duration: 2000,
        essential: true,
      });
    }
  }, [selectedDetection, scanning]);

  const visibleDetections = detections
    .filter((d) => d.risk_score >= 40)
    .sort((a, b) => a.risk_score - b.risk_score);

  function handleMapLoad() {
    const map = mapRef.current?.getMap();
    if (!map) return;
    const style = map.getStyle();
    if (!style?.layers) return;
    const KEEP = [
      "background", "land", "water", "ocean", "sea", "lake", "river",
      "boundary", "admin", "border", "coastline",
      "country-label", "continent-label", "state-label", "settlement",
      "place-city", "place-town", "place-label",
      "landcover", "landuse", "hillshade", "terrain",
    ];
    for (const layer of style.layers) {
      const id = layer.id.toLowerCase();
      const keep = KEEP.some((k) => id.includes(k));
      if (!keep) {
        try {
          map.setLayoutProperty(layer.id, "visibility", "none");
        } catch {
          // some layers don't support visibility
        }
      }
    }
  }

  return (
    <div className="w-full h-full relative">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        mapboxAccessToken={TOKEN}
        projection={{ name: "globe" } as any}
        attributionControl={false}
        onLoad={handleMapLoad}
      >
        <NavigationControl position="bottom-right" />

        {routes && routes.features.length > 0 && (
          <Source id="routes" type="geojson" data={routes}>
            <Layer
              id="route-lines"
              type="line"
              paint={{
                "line-color": "#ffffff",
                "line-opacity": 0.08,
                "line-width": 1,
              }}
              layout={{
                "line-cap": "round",
                "line-join": "round",
              }}
            />
          </Source>
        )}

        {visibleDetections.map((d) => {
          if (!d.lat || !d.lng) return null;
          const isNew = newMarkerIds?.has(d.id);
          const isSelected = selectedDetection?.id === d.id;

          return (
            <Marker key={d.id} longitude={d.lng} latitude={d.lat} anchor="center">
              <div
                className="group relative flex flex-col items-center cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  onMarkerClick(d);
                }}
              >
                {/* Ring pulse for new markers */}
                {isNew && (
                  <div className={`absolute w-3 h-3 rounded-full ${TIER_MARKER_COLOR[d.alert_tier]} animate-marker-ring`} />
                )}
                {/* Selected marker ping */}
                {isSelected && !isNew && (
                  <div className="absolute -inset-2 bg-green-500/20 rounded-full animate-ping" />
                )}
                {/* The dot */}
                <div
                  className={`w-3 h-3 rounded-full border-2 border-white shadow-lg transition-transform hover:scale-150
                    ${TIER_MARKER_COLOR[d.alert_tier]}
                    ${isNew ? "animate-marker-pop" : ""}
                    ${isSelected && !isNew ? "scale-150 ring-4 ring-green-500/30" : ""}`}
                />
              </div>
            </Marker>
          );
        })}
      </Map>
    </div>
  );
}
