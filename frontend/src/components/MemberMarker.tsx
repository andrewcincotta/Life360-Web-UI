// MemberMarker.tsx - Custom marker for members

import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { MemberSummary } from '../types';
import './MemberMarker.css';

interface MemberMarkerProps {
  member: MemberSummary;
}

const MemberMarker: React.FC<MemberMarkerProps> = ({ member }) => {
  if (!member.location) return null;

  // Create custom icon with member avatar
  const createCustomIcon = () => {
    const iconHtml = member.avatar
      ? `<div class="member-marker-icon">
          <img src="${member.avatar}" alt="${member.full_name}" />
          ${member.location?.is_driving ? '<span class="driving-indicator">🚗</span>' : ''}
        </div>`
      : `<div class="member-marker-icon default">
          <span>${member.first_name.charAt(0)}${member.last_name?.charAt(0) || ''}</span>
          ${member.location?.is_driving ? '<span class="driving-indicator">🚗</span>' : ''}
        </div>`;

    return L.divIcon({
      html: iconHtml,
      className: 'member-marker',
      iconSize: [48, 48],
      iconAnchor: [24, 48],
      popupAnchor: [0, -48],
    });
  };

  const formatAddress = () => {
    const { address1, address2 } = member.location!;
    if (address1 && address2) {
      return `${address1}, ${address2}`;
    }
    return address1 || address2 || 'Unknown location';
  };

  const formatTime = () => {
    const timestamp = parseInt(member.location!.timestamp);
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  const batteryClass = () => {
    const battery = member.location?.battery;
    if (!battery) return '';
    if (battery <= 20) return 'battery-low';
    if (battery <= 50) return 'battery-medium';
    return 'battery-high';
  };

  const formatSpeed = () => {
    const speed = member.location?.speed;
    if (speed === undefined || speed === null || speed <= 0) return 'N/A';
    const updatedSpeed = Math.round(speed);
    return `${updatedSpeed} mph`;
  }

  return (
    <Marker
      position={[member.location.latitude, member.location.longitude]}
      icon={createCustomIcon()}
    >
      <Popup className="member-popup">
        <div className="popup-header">
          {member.avatar && (
            <img
              src={member.avatar}
              alt={member.full_name}
              className="popup-avatar"
            />
          )}
          <div>
            <h3 className="popup-name">{member.full_name}</h3>
            <p className="popup-status">{member.status}</p>
          </div>
        </div>

        <div className="popup-content">
          <div className="popup-info">
            <span className="info-label">📍 Location:</span>
            <span className="info-value">
              {member.location.name || formatAddress()}
            </span>
          </div>

          {member.location.battery && (
            <div className="popup-info">
              <span className="info-label">🔋 Battery:</span>
              <span className={`info-value ${batteryClass()}`}>
                {member.location.battery}%
              </span>
            </div>
          )}

          {member.location.is_driving && (
            <div className="popup-info">
              <span className="info-label">🚗 Status:</span>
              <span className="info-value">Driving</span>
            </div>
          )}

          {member.location.speed && (
            <div className="popup-info">
              <span className="info-label">⚡ Speed:</span>
                <span className="info-value">{formatSpeed()}</span>
            </div>
          )}

          <div className="popup-info">
            <span className="info-label">🕒 Updated:</span>
            <span className="info-value">{formatTime()}</span>
          </div>

          {member.phone && (
            <div className="popup-info">
              <span className="info-label">📱 Phone:</span>
              <span className="info-value">
                <a href={`tel:${member.phone}`}>{member.phone}</a>
              </span>
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
};

export default MemberMarker;