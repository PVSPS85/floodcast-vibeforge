'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useStationStore } from '@/store/useStationStore';
import { Station } from '@/types';
import { formatCFS, getStatusColor } from '@/lib/utils';
import { Activity, ShieldAlert, Mountain, Compass } from 'lucide-react';

// Controller to smoothly pan to selected station
const MapPanController: React.FC<{ targetLat: number; targetLon: number }> = ({
  targetLat,
  targetLon,
}) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo([targetLat, targetLon], 7, { duration: 1.2 });
  }, [targetLat, targetLon, map]);
  return null;
};

export const StationMap: React.FC = () => {
  const { stations, selectedStation, setSelectedStation } = useStationStore();

  return (
    <div className="relative h-full w-full rounded-2xl overflow-hidden border border-slate-800/80 bg-slate-900 shadow-xl">
      <div className="absolute top-3 left-3 z-[1000] flex items-center space-x-2 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
        <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="font-semibold text-slate-200">50 USGS Gauges</span>
        <span className="text-slate-400">&bull; Click station to inspect</span>
      </div>

      <MapContainer
        center={[selectedStation.lat, selectedStation.lon]}
        zoom={5}
        scrollWheelZoom={true}
        className="h-full w-full min-h-[420px]"
      >
        <MapPanController targetLat={selectedStation.lat} targetLon={selectedStation.lon} />

        {/* Esri Dark Gray Base Map (Free, No API Key Required) */}
        <TileLayer
          attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Esri, DeLorme, NAVTEQ'
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        />

        {stations.map((station) => {
          const isSelected = station.station_id === selectedStation.station_id;
          const statusStyle = getStatusColor(station.status);

          return (
            <CircleMarker
              key={station.station_id}
              center={[station.lat, station.lon]}
              radius={isSelected ? 11 : 7}
              pathOptions={{
                color: isSelected ? '#ffffff' : statusStyle.hex,
                fillColor: statusStyle.hex,
                fillOpacity: isSelected ? 0.95 : 0.75,
                weight: isSelected ? 3 : 1.5,
              }}
              eventHandlers={{
                click: () => setSelectedStation(station),
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <div className="text-xs font-sans">
                  <p className="font-bold text-slate-900">{station.name}</p>
                  <p className="text-slate-700">Q: {formatCFS(station.current_discharge_cfs)}</p>
                </div>
              </Tooltip>

              <Popup className="floodcast-popup">
                <div className="p-1 space-y-2 text-xs font-sans">
                  <div className="border-b border-slate-200 pb-1">
                    <p className="text-[10px] font-bold tracking-wider text-slate-500 uppercase">
                      USGS #{station.station_id}
                    </p>
                    <p className="font-bold text-slate-900 text-sm">{station.name}</p>
                    <p className="text-slate-600">{station.river}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="bg-slate-100 p-1.5 rounded">
                      <span className="text-slate-500 block">Current Flow</span>
                      <span className="font-bold text-slate-900">{formatCFS(station.current_discharge_cfs)}</span>
                    </div>
                    <div className="bg-slate-100 p-1.5 rounded">
                      <span className="text-slate-500 block">Peak Forecast</span>
                      <span className="font-bold text-cyan-700">{formatCFS(station.predicted_peak_cfs)}</span>
                    </div>
                  </div>

                  <div className="pt-1 flex items-center justify-between text-[10px] text-slate-500">
                    <span>Drainage: {station.drainage_area_sqmi.toLocaleString()} sq mi</span>
                    <span className="capitalize font-bold text-rose-600">{station.status}</span>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Map Legend */}
      <div className="absolute bottom-3 right-3 z-[1000] bg-slate-950/90 backdrop-blur-md p-2.5 rounded-xl border border-slate-800 text-[11px] space-y-1.5 shadow-lg">
        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">River Status</p>
        <div className="flex items-center space-x-2">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
          <span className="text-slate-300">Normal</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2.5 w-2.5 rounded-full bg-cyan-500" />
          <span className="text-slate-300">Advisory Stage</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
          <span className="text-slate-300">Warning Stage</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse" />
          <span className="text-slate-300 font-semibold text-rose-400">Flood Stage</span>
        </div>
      </div>
    </div>
  );
};
export default StationMap;
