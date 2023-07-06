import React from 'react';
import { useState } from 'react';
import './App.css'; // Assurez-vous d'importer le fichier CSS approprié

const CustomSlider = () => {
  const [value, setvalue] = useState(0);

  const handleChange = (event) => {
    const value = event.target.value;
    setvalue(value)
  }
  return (
    <div className="slider-container">
      <input type="range" className="custom-slider" id="my-slider" min="0" max="1" value={value} step="0.01" onChange={handleChange} />
      <p>{value*100}</p>
    </div>
  );
};

export default CustomSlider;
