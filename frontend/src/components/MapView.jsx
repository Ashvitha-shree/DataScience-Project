import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix default marker icon paths (common Leaflet + bundler issue)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export default function MapView({ roads }) {
  const validRoads = roads.filter((r) => r.latitude && r.longitude);
  const center = validRoads.length
    ? [validRoads[0].latitude, validRoads[0].longitude]
    : [13.0827, 80.2707]; // default: Chennai

  return (
    <MapContainer center={center} zoom={11} style={{ height: "420px", width: "100%", borderRadius: "0.75rem" }}>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {validRoads.map((road) => (
        <Marker key={road.road_id} position={[road.latitude, road.longitude]}>
          <Popup>
            <strong>{road.road_name}</strong>
            <br />
            {road.location}
            <br />
            Type: {road.road_type}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
