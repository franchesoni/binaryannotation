import { useEffect, useState } from 'react';
import './App.css';
import Slider from './components/slider/index'
import ToggleButton from './components/toggleButton/index'
import {IPAddress, port} from './config';


function App() {
  //=================================================================\\
  //Variable declaration
  const tensorboardPort = (parseInt(port) + 1).toString();
  const [imgPerSec, setImgPerSec] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [annotatedImages, setAnnotatedImages] = useState(0);
  // const [previousIndexImg, setPreviousIndexImg] = useState(0);
  const [previousImgPath, setPreviousImgPath] = useState(0);
  const [imgPath, setImgPath] = useState("");
  const [imgProb, setImgProb] = useState(0);
  const [probImg, setProbImg] = useState(0.8);
  const [imageSrc, setimageSrc] = useState('');
  const [urlImg, setUrlImg] = useState();
  // const [previousUrlImg, setPreviousUrlImg] = useState();
  const [fetchInProgress, setFetchInProgress] = useState(false);
  const [fetchUrl, setFetchUrl] = useState(`http://${IPAddress}:${port}/`);
  const [isKeyPressed, setIsKeyPressed] = useState();
  const [contrastImg, setContrastImg] = useState(1);
  const [brightnessImg, setBrightnessImg] = useState(1);
  const [autoMode, setAutoMode] = useState(false);
  const [annotation, setAnnotation] = useState(false);
  const [autoModeSpeed, setAutoModeSpeed] = useState(1);
  const [numberOfImages, setNumberOfImages] = useState(); 
  const [numberOfTrue, setNumberOfTrue] = useState(0);
  const [numberOfFalse, setNumberOfFalse] = useState(0);
  //=================================================================\\
  //First fetch function to get the next image, just a simple get and  it returns the image's index and the blob\\
  const getImage = async () => {
    await fetch(fetchUrl + 'get_next_img')
      .then(response => {
        setImgPath(response.headers.get('image_path'))
        setImgProb(response.headers.get('prob'))
        const roundedProb = Number.parseFloat(imgProb)
        setProbImg(roundedProb.toFixed(3)*100)
        return response.blob().then(blob => ({ blob, imgPath }));
      })
      .then(({blob}) => {
        setUrlImg(URL.createObjectURL(blob))
      });
  }
  //=================================================================\\
  //Second fetch function to annotate the image (true or false), a simple post where we send the index and the boolean\\
  const annotateImage = async (label, skipped) => {
    if (fetchInProgress) {
      return
    }
    if (label == true && skipped == false) {
      setNumberOfTrue(numberOfTrue + 1)
    }
    else if (label == false && skipped == false) {
      setNumberOfFalse(numberOfFalse + 1)
    }
    setFetchInProgress(true)
    setPreviousImgPath(imgPath)
    // setPreviousUrlImg(urlImg)
    await fetch(fetchUrl + 'add_annotation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        is_positive: label,
        image_path: imgPath,
        is_skipped: skipped
      })
    })
      .then(response => {
        return response.json();
      })
      .then(() => {getImage()})
      .then(() => setAnnotatedImages(annotatedImages + 1))
      .catch(error => console.error('Error:', error))
      .finally(() => setFetchInProgress(false));
  }
  //=================================================================\\
  //Third fetch function to get the number of images to annotate\\
  const getNumberImages = async () => {
    await fetch(fetchUrl + 'count_images')
    .then((response) => {
      if (!response.ok) {
        throw new Error('La requête a échoué.');
      }
      return response.json();
    })
    .then((data) => {
      console.log(data.num_images)
      setNumberOfImages(data.num_images);
      setAnnotatedImages(data.num_images_annotated)
      setNumberOfTrue(data.num_true)
      setNumberOfFalse(data.num_images_annotated - data.num_true)
    })
    .catch((error) => {
      console.log(error.message);
    });
  }
  //=================================================================\\
  //UseEffect activated when the user refresh the page to have the first image and the number of images to annotate\\
  useEffect(() =>{
    getImage() 
    getNumberImages()
  },[]);
  //=================================================================\\
  //UseEffect to change the color of the buttons according to the probability\\
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--probabilityDog', probImg)
    root.style.setProperty('--probabilityCat', 100 - (probImg))
  }, [probImg]);
  //=================================================================\\
  //UseEffect to change the image's source when we fetch a new image\\
  useEffect(() => {
    setimageSrc(urlImg)
  }, [urlImg]);
  //=================================================================\\
  //Simple function to get previous image and index to undo the last annotation\\
  const undoAnnotation = () => {
    if (annotatedImages === 0){
      return
    }
    
    fetch(fetchUrl + 'undo_annotation')
      .then(response => {
        setImgPath(response.headers.get('image_path'))
        return response.blob().then(blob => ({ blob, imgPath}));
      })
      .then(({blob}) => {
        setUrlImg(URL.createObjectURL(blob))
      })
      getNumberImages()
  }
  //=================================================================\\
  //Function to reset the annotations\\
  const resetAnnotations = () => {
    setIsActive(false)
    setSeconds(0)
    setAnnotatedImages(0)
    fetch(fetchUrl + 'reset_everything')
  }
  //=================================================================\\
  //UseEffect to create an event listener on keypress, refreshed every time we change the image\\
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (isKeyPressed) {
        return; // If a key is already pressed, do nothing
      }
  
      setIsKeyPressed(true);

      if (autoMode == false) {
        if (event.key === 'f') {
          setIsActive(true);
          annotateImage(true, false);
        } else if (event.key === 'j') {
          setIsActive(true);
          annotateImage(false, false);
        } else if (event.key === 'r') {
          resetAnnotations();
        } else if (event.code === 'Space') {
          event.preventDefault();
          setIsActive(false);
        } else if (event.key === 'Backspace') {
          undoAnnotation();
        }
      }
      else {
        if (event.code === 'Space') {
          event.preventDefault();
          annotateImage(true, false)
        }
        else if (event.key === 'Backspace') {
          undoAnnotation();
        }
        else if (event.key === 'm') {
          setAutoModeSpeed(0)
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
  //UseEffect to start the timer\\
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
  //Functions to change the contrast and brightness of the image\\
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
  //=================================================================\\
  //Function to switch the mode between auto and manual\\
  const handleModeChange = (event) => {
    setAutoMode(!autoMode)
  }
  //=================================================================\\
  //Function to change the speed of the auto mode\\
  const handleAutoModeSpeedChange = (event) => {
    setAutoModeSpeed(event.target.value)
    };
  //=================================================================\\
  //UseEffect to auto annotate automatically the image each second the user choose\\
  useEffect(() => {
    if (autoModeSpeed == 0) {return}
    if (autoMode == false) {return}
    const interval = setInterval(() => {
      annotateImage(annotation, false)
      setAnnotation(false)
    }, 1000/autoModeSpeed); // 1000 millisecondes = 1 seconde

    return () => {
      clearInterval(interval); // Nettoyage de l'intervalle lors de la suppression du composant
    };
  }, [imgPath, autoMode, annotation, autoModeSpeed]);

  return (
    <div className="App">
      <header className="App-header">
        <img className='App-logo-borelli' src="/images/logoBorelli.png"/>
        <h1 className='App-title'>Binary annotation</h1>
        <h3 className='App-annotated-images'> Annotated images: {annotatedImages} / {numberOfImages}</h3>
        <p className='App-true-false-annotated'> {numberOfTrue} true / {numberOfFalse} false</p>
        <p className='App-cronometer'>{seconds} seconds</p>
        <p className='App-cronometer'>{imgPerSec} img/s</p>
        <p>Probability: {probImg}%</p>
        <ToggleButton value={autoMode} onClick={handleModeChange}></ToggleButton>
        <p>filepath: {imgPath}</p>
        {autoMode && (
          <div>
            <p>Annotation: {String(annotation)}</p>
            <Slider
            label="AutoMode Speed"
            type="range"
            min="0"
            max="5"
            value={autoModeSpeed}
            step="0.1"
            onChange={handleAutoModeSpeedChange}>
            </Slider>
            <p>{autoModeSpeed}</p>
          </div>
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
          onChange={handleContrastChange}>
          </Slider>
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
          <button className='App-dogButton' onClick={() => annotateImage(true, false)}> Dog (positive) <br/> or press F </button>
          <button className='App-catButton' onClick={() => annotateImage(false, false)}> Cat (negative) <br/> or press J </button>
          <button className='App-undoButton' onClick={() => undoAnnotation()}>Undo (or press backspace)</button>
          <button className='App-skipButton' onClick={() => annotateImage(false, true)}>Skip</button>
        </div>
        )}
        <p style={{fontSize:15}}>Press space to pause the timer and r to reset it</p>
        <iframe src={`http://${IPAddress}:${tensorboardPort}/tensorboard`} width='1400' height='600'></iframe>
      </header>
    </div>
  );
}

export default App;
