import React from 'react';
import './slider.css'
const Index = ({label, type, min, max, value, step, onChange}) => {
    return (
        <div >
            <p className='Title'>{label}</p>
            <div className='Container-slider'>
                <input
                    className='custom-slider'
                    type={type}
                    min={min}
                    max={max}
                    value={value}
                    step={step}
                    onChange={onChange}
                />
                
            </div>
            
        </div>
    );
}

export default Index;
