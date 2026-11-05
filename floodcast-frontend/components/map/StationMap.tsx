'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  Tooltip,
  useMap,
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useStationStore } from '@/store/useStationStore';
import { Station } from '@/types';
import { formatCFS } from '@/lib/utils';
import { Search, X, MapPin, Compass } from 'lucide-react';

// Initial geographic center and zoom focused on the United States
const INITIAL_CENTER: [number, number] = [39.8283, -98.5795];
const INITIAL_ZOOM = 5;

// Helper function to return severity color based on discharge_cfs
export function getSeverityColor(discharge_cfs: number): string {
  if (discharge_cfs < 15000) {
    return '#00BFFF'; // Normal/Blue
  } else if (discharge_cfs < 35000) {
    return '#FFA500'; // High-Surge/Amber
  } else {
    return '#FF0033'; // Dangerous/Red
  }
}

// Map controller to execute flyTo smoothly when station changes
const MapPanController: React.FC<{ targetStation: Station | null }> = ({
  targetStation,
}) => {
  const map = useMap();
  const prevIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!targetStation) return;
    if (prevIdRef.current !== targetStation.station_id) {
      prevIdRef.current = targetStation.station_id;
      map.flyTo([targetStation.lat, targetStation.lon], 8, {
        duration: 1.4,
        easeLinearity: 0.25,
      });
    }
  }, [targetStation, map]);

  return null;
};

export const StationMap: React.FC = () => {
  const { stations, selectedStation, setSelectedStation } = useStationStore();

  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter stations by name, state, river, or station ID
  const filteredStations = stations.filter((s) => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    const name = ((s as unknown as { station_name?: string }).station_name ?? s.name).toLowerCase();
    return (
      name.includes(q) ||
      s.state.toLowerCase() === q ||
      s.state.toLowerCase().includes(q) ||
      s.river.toLowerCase().includes(q) ||
      s.station_id.includes(q)
    );
  });

  const handleSelectStation = (station: Station) => {
    setSelectedStation(station);
    const stationName = (station as unknown as { station_name?: string }).station_name ?? station.name;
    setQuery(`${stationName} (${station.state})`);
    setIsOpen(false);
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
  };

  return (
    <div className="flex flex-col h-full w-full space-y-2.5 flex-1">
      {/* NWS Professional Search & Filter Bar */}
      <div ref={searchRef} className="relative z-[1100] w-full shrink-0">
        <div className="flex items-center gap-2 rounded-xl border border-slate-700/80 bg-slate-900/95 p-2 shadow-lg backdrop-blur-md">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-cyan-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIsOpen(true);
              }}
              onFocus={() => setIsOpen(true)}
              placeholder="Search USGS gauges by station name, state (e.g. MO, NC, CA), or ID..."
              className="w-full rounded-lg border border-slate-800 bg-slate-950/80 py-2 pl-9 pr-9 text-xs font-medium text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
            {query && (
              <button
                onClick={handleClear}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          <div className="hidden sm:flex items-center space-x-1.5 px-2 text-[11px] font-mono text-slate-400 border-l border-slate-800">
            <Compass className="h-3.5 w-3.5 text-cyan-400" />
            <span>Telemetry Dashboard</span>
          </div>
        </div>

        {/* Autocomplete Results Dropdown */}
        {isOpen && (
          <div className="absolute left-0 right-0 mt-1.5 max-h-64 overflow-y-auto rounded-xl border border-slate-700 bg-slate-900/98 p-1.5 shadow-2xl backdrop-blur-md">
            <div className="px-2 py-1 text-[10px] font-semibold tracking-wider text-slate-400 uppercase border-b border-slate-800/80">
              Matching Gauges ({filteredStations.length})
            </div>
            {filteredStations.length === 0 ? (
              <div className="p-3 text-center text-xs text-slate-400">
                No USGS station found matching &ldquo;{query}&rdquo;
              </div>
            ) : (
              filteredStations.map((station) => {
                const discharge_cfs =
                  (station as unknown as { discharge_cfs?: number }).discharge_cfs ??
                  station.current_discharge_cfs ??
                  0;
                const station_name =
                  (station as unknown as { station_name?: string }).station_name ??
                  station.name;
                const markerColor = getSeverityColor(discharge_cfs);
                const isSelected = station.station_id === selectedStation.station_id;

                return (
                  <button
                    key={station.station_id}
                    onClick={() => handleSelectStation(station)}
                    className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition ${
                      isSelected
                        ? 'bg-cyan-950/40 text-cyan-200 border border-cyan-800/50'
                        : 'text-slate-200 hover:bg-slate-800/80'
                    }`}
                  >
                    <div className="flex items-center space-x-2 truncate pr-2">
                      <MapPin className="h-3.5 w-3.5 shrink-0" style={{ color: markerColor }} />
                      <div className="truncate">
                        <span className="font-bold text-white">{station_name}</span>
                        <span className="ml-1.5 text-[10px] text-slate-400 font-mono">
                          [{station.state}] &bull; #{station.station_id}
                        </span>
                        <p className="text-[10px] text-slate-400 truncate">{station.river}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 shrink-0">
                      <span className="font-mono text-[11px] font-semibold" style={{ color: markerColor }}>
                        {formatCFS(discharge_cfs)}
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        )}
      </div>

      {/* Map Container Viewport */}
      <div className="relative flex-1 w-full rounded-2xl overflow-hidden border border-slate-800/90 bg-slate-900 shadow-xl min-h-[500px] flex flex-col">
        <div className="absolute top-3 left-3 z-[1000] flex items-center space-x-2 bg-slate-950/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
          <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-bold text-slate-200">High-Resolution Satellite Telemetry</span>
          <span className="text-slate-400">&bull; Esri World Imagery</span>
        </div>

        <MapContainer
          center={INITIAL_CENTER}
          zoom={INITIAL_ZOOM}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%', minHeight: '500px' }}
          className="h-full w-full min-h-[500px] flex-1"
        >
          <MapPanController targetStation={selectedStation} />

          {/* High-Resolution Esri World Imagery Satellite Map */}
          <TileLayer
            attribution='&copy; <a href="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer">Esri World Imagery</a> &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />

          {stations.map((station) => {
            const discharge_cfs =
              (station as unknown as { discharge_cfs?: number }).discharge_cfs ??
              station.current_discharge_cfs ??
              0;
            const station_name =
              (station as unknown as { station_name?: string }).station_name ??
              station.name;
            const station_id = station.station_id;
            const markerColor = getSeverityColor(discharge_cfs);

            return (
              <CircleMarker
                key={station.station_id}
                center={[station.lat, station.lon]}
                radius={12}
                fillOpacity={0.8}
                weight={3}
                color={markerColor}
                fillColor={markerColor}
                eventHandlers={{
                  click: () => setSelectedStation(station),
                }}
              >
                <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                  <div className="text-xs font-sans">
                    <p className="font-bold text-slate-900">
                      {station_name}, {station.state}
                    </p>
                    <p className="text-slate-700">
                      USGS #{station_id} &bull; Q: {formatCFS(discharge_cfs)}
                    </p>
                  </div>
                </Tooltip>

                {/* Clean, Dark-Themed Popup */}
                <Popup className="floodcast-popup">
                  <div className="p-2 space-y-2 text-xs font-sans text-slate-100 bg-slate-900 rounded-lg min-w-[200px]">
                    <div className="border-b border-slate-700/80 pb-1.5">
                      <p className="font-bold text-white text-sm leading-tight">
                        {station_name}
                      </p>
                      <div className="mt-0.5 flex items-center justify-between text-[11px] font-mono">
                        <span className="text-cyan-400 font-semibold">
                          USGS #{station_id}
                        </span>
                        <span className="text-slate-400">
                          {station.state}
                        </span>
                      </div>
                    </div>

                    <div className="bg-slate-950/80 p-2 rounded border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">
                        Current Discharge
                      </span>
                      <span
                        className="font-mono font-bold text-sm"
                        style={{ color: markerColor }}
                      >
                        {formatCFS(discharge_cfs)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-0.5">
                      <span>Severity Status:</span>
                      <span
                        className="px-1.5 py-0.5 rounded font-bold uppercase text-[9px]"
                        style={{
                          backgroundColor: `${markerColor}22`,
                          color: markerColor,
                          border: `1px solid ${markerColor}66`,
                        }}
                      >
                        {discharge_cfs < 15000
                          ? 'Normal (<15k)'
                          : discharge_cfs < 35000
                          ? 'High-Surge'
                          : 'Dangerous (≥35k)'}
                      </span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Dynamic Telemetry Severity Legend */}
        <div className="absolute bottom-3 right-3 z-[1000] bg-slate-950/92 backdrop-blur-md p-2.5 rounded-xl border border-slate-800 text-[11px] space-y-1.5 shadow-xl">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Telemetry Severity
          </p>
          <div className="flex items-center space-x-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: '#00BFFF' }} />
            <span className="text-slate-300">Normal (&lt; 15,000 cfs)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: '#FFA500' }} />
            <span className="text-slate-300">High-Surge (15,000 – 35,000 cfs)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="h-2.5 w-2.5 rounded-full animate-pulse" style={{ backgroundColor: '#FF0033' }} />
            <span className="text-slate-300 font-semibold text-rose-400">Dangerous (&ge; 35,000 cfs)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StationMap;
