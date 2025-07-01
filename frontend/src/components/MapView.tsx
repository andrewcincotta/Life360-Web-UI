// MapView.tsx - Main map component

import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import toast from "react-hot-toast";
import Life360Api from "../api";
import { CircleInfo, MemberSummary } from "../types";
import { TileProvider, getTileUrl } from "../mapProviders";
import CircleSelector from "./CircleSelector";
import MapStyleSelector from "./MapStyleSelector";
import MemberMarker from "./MemberMarker";
import "leaflet/dist/leaflet.css";
import "./MapView.css";

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

interface MapViewProps {
  token: string;
  onLogout: () => void;
  tileProvider: TileProvider;
}

// Component to handle map bounds
const MapBounds: React.FC<{ members: MemberSummary[] }> = ({ members }) => {
  const map = useMap();

  useEffect(() => {
    if (members.length === 0) return;

    const bounds = L.latLngBounds(
      members
        .filter((m) => m.location)
        .map((m) => [m.location!.latitude, m.location!.longitude])
    );

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [members, map]);

  return null;
};

const MapView: React.FC<MapViewProps> = ({ token, onLogout, tileProvider }) => {
  const [circles, setCircles] = useState<CircleInfo[]>([]);
  const [selectedCircle, setSelectedCircle] = useState<string>(() => {
    return localStorage.getItem("selectedCircle") || "";
  });
  const [members, setMembers] = useState<MemberSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const apiRef = useRef<Life360Api>(new Life360Api(token));

  // Load circles on mount
  useEffect(() => {
    loadCircles();
  }, []);

  // Load members when circle changes
  useEffect(() => {
    if (selectedCircle) {
      loadMembers(selectedCircle);
      // Set up auto-refresh every 30 seconds
      const interval = setInterval(() => {
        refreshMembers();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [selectedCircle]);

  useEffect(() => {
    if (selectedCircle) {
      localStorage.setItem("selectedCircle", selectedCircle);
    }
  }, [selectedCircle]);

  const loadCircles = async () => {
    try {
      const circleData = await apiRef.current.getCircles();
      setCircles(circleData);
      const savedCircle = localStorage.getItem("selectedCircle");
      const savedCircleExists =
        savedCircle && circleData.some((c) => c.id === savedCircle);

      if (savedCircleExists) {
        setSelectedCircle(savedCircle);
      } else if (circleData.length > 0) {
        setSelectedCircle(circleData[0].id);
      }
    } catch (error) {
      toast.error("Failed to load circles");
    } finally {
      setLoading(false);
    }
  };

  const loadMembers = async (circleId: string) => {
    setLoading(true);
    try {
      const memberData = await apiRef.current.getCircleMembers(circleId);
      setMembers(memberData);

      const activeCount = memberData.filter(
        (m) => m.status === "Active" && m.location
      ).length;
      toast.success(`Loaded ${activeCount} active members`);
    } catch (error) {
      toast.error("Failed to load members");
    } finally {
      setLoading(false);
    }
  };

  const refreshMembers = async () => {
    if (!selectedCircle || refreshing) return;

    setRefreshing(true);
    try {
      const memberData = await apiRef.current.getCircleMembers(selectedCircle);
      setMembers(memberData);
    } catch (error) {
      console.error("Failed to refresh members:", error);
    } finally {
      setRefreshing(false);
    }
  };

  // Filter only active members with locations
  const activeMembers = members.filter(
    (m) => m.status === "Active" && m.location
  );

  if (loading && circles.length === 0) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading circles...</p>
      </div>
    );
  }

  return (
    <div className="map-container">
      <div className="map-header">
        <div className="header-left">
          <h1 className="map-title">Life360 Tracker</h1>
          <CircleSelector
            circles={circles}
            selectedCircle={selectedCircle}
            onCircleChange={setSelectedCircle}
          />
          <MapStyleSelector currentPath={window.location.pathname} />
        </div>
        <div className="header-right">
          <button
            onClick={refreshMembers}
            disabled={refreshing}
            className="refresh-button"
            title="Refresh member locations"
          >
            {refreshing ? "⟳" : "↻"} Refresh
          </button>
          <button onClick={onLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>

      <div className="map-stats">
        <span className="stat-item">
          <strong>{activeMembers.length}</strong> active members
        </span>
        <span className="stat-item">
          <strong>{members.length - activeMembers.length}</strong> offline
        </span>
        {refreshing && (
          <span className="stat-item refreshing">Updating...</span>
        )}
      </div>

      <div className="map-wrapper">
        {loading ? (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Loading members...</p>
          </div>
        ) : (
          <MapContainer
            center={[39.8283, -98.5795]} // Center of USA
            zoom={4}
            className="leaflet-map"
          >
            <TileLayer
              attribution={tileProvider.attribution}
              url={getTileUrl(tileProvider)}
              maxZoom={tileProvider.maxZoom || 19}
              {...(tileProvider.subdomains && {
                subdomains: tileProvider.subdomains,
              })}
            />

            <MapBounds members={activeMembers} />

            {activeMembers.map((member) => (
              <MemberMarker key={member.id} member={member} />
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  );
};

export default MapView;
