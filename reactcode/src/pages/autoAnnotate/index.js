import React, { useState } from 'react';

const Index = () => {
  const [contrastValue, setContrastValue] = useState(100);
  const [brightnessValue, setBrightnessValue] = useState(100);

  const handleContrastChange = (event) => {
    const value = event.target.value;
    setContrastValue(value);
  };

  const handleBrightnessChange = (event) => {
    const value = event.target.value;
    setBrightnessValue(value);
  };

  return (
    <div>
      <div className="slider-container">
        <label htmlFor="contrast-slider">Contrast:</label>
        <input
          type="range"
          id="contrast-slider"
          min="0"
          max="200"
          value={contrastValue}
          step="1"
          onChange={handleContrastChange}
        />
      </div>
      <div className="slider-container">
        <label htmlFor="brightness-slider">Brightness:</label>
        <input
          type="range"
          id="brightness-slider"
          min="0"
          max="200"
          value={brightnessValue}
          step="1"
          onChange={handleBrightnessChange}
        />
      </div>
      <img
        src="/images/logoBorelli.png"
        alt="Image"
        style={{
          filter: `contrast(${contrastValue}%) brightness(${brightnessValue}%)`,
        }}
      />
    </div>
  );
};

export default Index;

