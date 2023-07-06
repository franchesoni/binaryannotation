import React from 'react';
import { useState, useEffect } from 'react';
import './App.css'

const App = () => {
  const [urlImg, setUrlImg] = useState();
  const [probImg, setProbImg] = useState(0.8);
  const [indexImg, setIndexImg] = useState(0);
  const [fetchUrl, setFetchUrl] = useState(`http://localhost:8000/`);
  const getImage = async () => {
    await fetch(fetchUrl + 'get_next_img')
      .then(response => {
        setIndexImg(response.headers.get('Image_index'))
        var prob = response.headers.get('Prob')
        const roundedProb = Number.parseFloat(prob)
        setProbImg(roundedProb.toFixed(3)*100)
        return response.blob().then(blob => ({ blob, indexImg }));
      })
      .then(({blob}) => {
        setUrlImg(URL.createObjectURL(blob))
      });
  }

  useEffect(() => {
    getImage()
  }, []);

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
