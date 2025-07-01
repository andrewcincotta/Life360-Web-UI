// MapStyleSelector.tsx - Map style selector component

import React from 'react';
import { tileProviders } from '../mapProviders';
import './MapStyleSelector.css';

interface MapStyleSelectorProps {
  currentPath: string;
}

const MapStyleSelector: React.FC<MapStyleSelectorProps> = ({ currentPath }) => {
  const mapStyles = [
    { path: '/', provider: tileProviders.cartoLight, description: 'Light Street Map' },
    { path: '/dark', provider: tileProviders.cartoDark, description: 'Dark Street Map' },
    { path: '/satellite', provider: tileProviders.mapboxSatellite, description: 'Satellite (Requires Mapbox Token)' },
  ];

  const handleStyleChange = (path: string) => {
    window.location.pathname = path;
  };

  return (
    <div className="map-style-selector">
      <label className="style-label">Map Style:</label>
      <select 
        value={currentPath} 
        onChange={(e) => handleStyleChange(e.target.value)}
        className="style-select"
      >
        {mapStyles.map((style) => (
          <option key={style.path} value={style.path}>
            {style.description}
          </option>
        ))}
      </select>
    </div>
  );
};

export default MapStyleSelector;