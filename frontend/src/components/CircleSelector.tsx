// CircleSelector.tsx - Circle selector dropdown

import React from 'react';
import { CircleInfo } from '../types';
import './CircleSelector.css';

interface CircleSelectorProps {
  circles: CircleInfo[];
  selectedCircle: string;
  onCircleChange: (circleId: string) => void;
}

const CircleSelector: React.FC<CircleSelectorProps> = ({
  circles,
  selectedCircle,
  onCircleChange,
}) => {
  return (
    <div className="circle-selector">
      <label htmlFor="circle-select" className="circle-label">
        Circle:
      </label>
      <select
        id="circle-select"
        value={selectedCircle}
        onChange={(e) => onCircleChange(e.target.value)}
        className="circle-select"
      >
        {circles.map((circle) => (
          <option key={circle.id} value={circle.id}>
            {circle.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default CircleSelector;