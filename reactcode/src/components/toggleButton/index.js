import React from 'react';
import { useState } from 'react';
import './toggleButton.css'

const Index = ({value, onClick}) => {
  const [isOn, setIsOn] = useState(value);

  const handleClick = () => {
    const newState = !isOn;
    setIsOn(newState);
    onClick(newState);
  };

  return (
    <div>
      <span>Manual</span>
      <div
        className={`toggle-button ${isOn ? 'on' : 'off'}`}
        onClick={handleClick}
      >
      </div>
      <span>Auto</span>
    </div>
    
  );
}

export default Index;
