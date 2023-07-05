import React from 'react';
import './App.css'

const App = () => {

  const handleClick = async (e) => {
    if (e=='auto')
    {
      window.location.href = '/annotate/auto'
    }
    else if (e=='manual')
    {
      window.location.href = '/annotate/manual'
    }
    
  }

  return (
    <div className='App'>
        <header className="App-header">
          <img className='App-logo-borelli' src="/images/logoBorelli.png"/>
          <h1 className='App-title'>Binary annotation</h1>
          <h3> Choose your annotation mode </h3>
          <div className='App-container-button'>
            <button className='App-button' onClick={e => handleClick('auto')}> Auto </button>
            <button className='App-button' onClick={e => handleClick('manual')}> Manual </button>
          </div>
          <p>Explain something here</p>

        </header>
    </div>
  );
}

export default App;
