import { useEffect, useState } from 'react';
import './App.css';
import Slider from './components/slider/index'
import ToggleButton from './components/toggleButton/index'
//import {IPAddress, port} from './config';


function App() {
  //=================================================================\\
  //Variable declaration
  const [port, setPort] = useState();
  const IPAddress = process.env.REACT_APP_IPADDRESS
  const [imgPerSec, setImgPerSec] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [annotatedImages, setAnnotatedImages] = useState(0);
  const [previousIndexImg, setPreviousIndexImg] = useState(0);
  const [indexImg, setIndexImg] = useState(0);
  const [probImg, setProbImg] = useState(0.8);
  const [imageSrc, setimageSrc] = useState('');
  const [urlImg, setUrlImg] = useState();
  const [previousUrlImg, setPreviousUrlImg] = useState();
  const [fetchInProgress, setFetchInProgress] = useState(false);
  const [fetchUrl, setFetchUrl] = useState(`http://localhost:8000/`);
  const [isKeyPressed, setIsKeyPressed] = useState();
  const [contrastImg, setContrastImg] = useState(1);
  const [brightnessImg, setBrightnessImg] = useState(1);
  const [autoMode, setAutoMode] = useState(false);
  const [annotation, setAnnotation] = useState(true);
  //=================================================================\\
  //First fetch function to get the next image, just a simple get and  it returns the image's index and the blob\\
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
  //=================================================================\\
  //UseEffect activated when the user refresh the page to have the first image\\
  useEffect(() =>{
    setPort(process.env.REACT_APP_PORT)
    getImage() 
  },[]);
  useEffect(() => {
    console.log(port)
  }, [port]);
  useEffect(() => {
    console.log('probImg' + probImg)
  }, [probImg]);

  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--probabilityDog',probImg)
    root.style.setProperty('--probabilityCat',100 - (probImg))
  }, [probImg]);
  //=================================================================\\
  //UseEffect to change the image's source when we fetch a new image\\
  useEffect(() => {
    setimageSrc(urlImg)
  }, [urlImg]);

  //=================================================================\\
  //Second fetch function to annotate the image (true or false), a simple post where we send the index and the boolean\\
  const annotateImage = async (test) => {
    if (fetchInProgress) {
      return
    }
    setFetchInProgress(true)
    setPreviousIndexImg(indexImg)
    setPreviousUrlImg(urlImg)
    await fetch(fetchUrl + 'add_annotation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_index: indexImg,
        is_positive: test
      })
    })
      .then(response => {
        //console.log(response);
        return response.json();
      })
      //.then(data => console.log('Response body:', data))
      .then(() => {getImage()})
      .then(() => setAnnotatedImages(annotatedImages + 1))
      .catch(error => console.error('Error:', error))
      .finally(() => setFetchInProgress(false));
    // await getImage()
  }

  //=================================================================\\
  //Simple function to get previous image and index\\
  const undoAnnotation = () => {
    if (annotatedImages === 0){
      return
    }
    setAnnotatedImages(annotatedImages-1)
    fetch(fetchUrl + 'undo_annotation')
      .then(response => {
        setIndexImg(response.headers.get('Image_index'))
        return response.blob().then(blob => ({ blob, indexImg }));
      })
      .then(({blob}) => {
        setUrlImg(URL.createObjectURL(blob))
      })
  }

  //=================================================================\\
  //UseEffect to create an event listener on keypress, refreshed every time we change the image\\
  const resetAnnotations = () => {
    setIsActive(false)
    setSeconds(0)
    setAnnotatedImages(0)
    fetch(fetchUrl + 'reset_annotation')
  }
  //=================================================================\\
  //UseEffect to create an event listener on keypress, refreshed every time we change the image\\
  useEffect(() => {
    const handleKeyDown = (event) => {
      console.log(event.key)
      if (isKeyPressed) {
        return; // Si une touche est déjà enfoncée, ne rien faire
      }
  
      setIsKeyPressed(true); // Marquer qu'une touche est enfoncée
  
      // Votre logique existante pour gérer les touches individuelles
      if (autoMode == false) {
        if (event.key === 'f') {
          setIsActive(true);
          annotateImage(true);
        } else if (event.key === 'j') {
          setIsActive(true);
          annotateImage(false);
        } else if (event.key === 'r') {
          resetAnnotations();
        } else if (event.code === 'Space') {
          setIsActive(false);
        } else if (event.key === 'Backspace') {
          undoAnnotation();
        }
      }
      else {
        if (event.key === 'm') {
          setAnnotation(!annotation)
        }
      }
      
    };
  
    const handleKeyUp = () => {
      setIsKeyPressed(false); // Marquer qu'aucune touche n'est enfoncée
    };
  
    // Écouter les événements keydown et keyup sur l'élément document
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
  
    // Nettoyer les écouteurs d'événements lors du démontage du composant
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [isKeyPressed, setIsKeyPressed, setIsActive, annotateImage, resetAnnotations, undoAnnotation, autoMode]);
  

  //=================================================================\\
  //UseEffect to calculate the number of images per second and display it\\
  useEffect(() => {
    var imgperseconds
    var roundedImgPerSec
    if (seconds !== 0) {
      imgperseconds=(annotatedImages/seconds)
      roundedImgPerSec= imgperseconds.toFixed(3)
      setImgPerSec(roundedImgPerSec)
    }
    else {
      setImgPerSec(0)
    }
  }, [seconds]);

  //=================================================================\\
  //UseEffect to start a timer\\
  useEffect(() => {
    let interval = null;
    console.log('annotation: ' + annotation)
    if (isActive) {
      interval = setInterval(() => {
        setSeconds((prevSeconds) => prevSeconds + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive]);


  //=================================================================\\
  const handleContrastChange = (event) => {
    const root = document.documentElement;
    const value = event.target.value;
    root.style.setProperty('--contrastImg',value)
    setContrastImg(value)
    };

  const handleBrightnessChange = (event) => {
    const root = document.documentElement;
    const value = event.target.value;
    root.style.setProperty('--brightnessImg',value)
    setBrightnessImg(value);
    };

  const handleModeChange = (event) => {
    setAutoMode(!autoMode)
  }

  useEffect(() => {
    if (autoMode == false) {return}
    const interval = setInterval(() => {
      console.log('Annotation: ' + String(annotation))
      annotateImage(annotation)
    }, 1000); // 1000 millisecondes = 1 seconde

    return () => {
      clearInterval(interval); // Nettoyage de l'intervalle lors de la suppression du composant
    };
  }, [indexImg, autoMode, annotation]);

  return (
    <div className="App">
      <header className="App-header">
        <img className='App-logo-borelli' src="/images/logoBorelli.png"/>
        <h1 className='App-title'>Binary annotation</h1>
        <h3 className='App-annotated-images'> Annotated images: {annotatedImages}</h3>
        <p className='App-cronometer'>{seconds} seconds</p>
        <p className='App-cronometer'>{imgPerSec} img/s</p>
        <p>Probability: {probImg}%</p>
        <ToggleButton value={autoMode} onClick={handleModeChange}></ToggleButton>

        {autoMode && (
          <p>Annotation: {String(annotation)}</p>
        )}
        
        
        {imageSrc && (
          <div style={{display:'flex', alignItems:'center', justifyContent: 'space-between'}}>
            <img className="image previous" alt="Previous Image" src={imageSrc}/>
            <img className='image main' src={imageSrc}/>
            <img className="image next" src={imageSrc} alt="Next Image"/>
          </div>
        )}
        <div className='App-container-sliders'>
          <Slider
          label="Contrast"
          type="range"
          min="0"
          max="3"
          value={contrastImg}
          step='0.01'
          onChange={handleContrastChange}
          ></Slider>
          <Slider 
          label="Brightness"
          type="range"
          min="0"
          max="2"
          value={brightnessImg}
          step='0.01'
          onChange={handleBrightnessChange}>
          </Slider>
        </div>
        {!autoMode && (
          <div className='App-container-button'>
          <button className='App-dogButton' onClick={() => annotateImage(true)}> Dog (positive) <br/> or press F </button>
          <button className='App-catButton' onClick={() => annotateImage(false)}> Cat (negative) <br/> or press J </button>
          <button className='App-undoButton' onClick={() => undoAnnotation()}>Undo (or press backspace)</button>
        </div>
        )}
        
        <p style={{fontSize:15}}>Press space to pause the timer and r to reset it</p>
        <iframe src={`http://${IPAddress}:6066`} width='1400' height='600'></iframe>
      </header>
    </div>
  );
}

export default App;
