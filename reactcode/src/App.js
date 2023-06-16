import { useEffect, useState } from 'react';
import './App.css';
import {IPAddress, port} from './config';

function App() {
  //=================================================================\\
  //Variable declaration
  const [selectedFiles, setSelectefFiles] = useState([]);
  const [image, setImage] = useState();
  const [imgPerSec, setImgPerSec] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [annotatedImages, setAnnotatedImages] = useState(0);
  const [previousIndexImg, setPreviousIndexImg] = useState(0);
  const [indexImg, setIndexImg] = useState(0);
  const [imageSrc, setimageSrc] = useState('');
  const [urlImg, setUrlImg] = useState();
  const [previousUrlImg, setPreviousUrlImg] = useState();
  const [fetchUrl, setFetchUrl] = useState(`http://${IPAddress}:${port}/`);
  //=================================================================\\
  //First fetch function to get the next image, just a simple get and  it returns the image's index and the blob\\
  const getImage = async () => {
    await fetch(fetchUrl + 'get_next_img')
      .then(response => {
        setIndexImg(response.headers.get('Image_index'))
        return response.blob().then(blob => ({ blob, indexImg }));
      })
      .then(({blob}) => {
        setUrlImg(URL.createObjectURL(blob))
      });
  }
  //=================================================================\\
  //UseEffect activated when the user refresh the page to have the first image\\
  useEffect(() =>{
    getImage() 
  },[]);

  //=================================================================\\
  //UseEffect to change the image's source when we fetch a new image\\
  useEffect(() => {
    setimageSrc(urlImg)
  }, [urlImg]);

  //=================================================================\\
  //Second fetch function to annotate the image (true or false), a simple post where we send the index and the boolean\\
  const annotateImage = async (test) => {
    setPreviousIndexImg(indexImg)
    setPreviousUrlImg(urlImg)
    fetch(fetchUrl + 'add_annotation', {
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
      .catch(error => console.error('Error:', error));
    await getImage()
    setAnnotatedImages(annotatedImages + 1)
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
    const handleKeyPress = (event) => {
      if (event.key === 'f') {
        setIsActive(true)
        annotateImage(true)
      }
      if (event.key === 'j') {
        setIsActive(true)
        annotateImage(false)
      }
      if (event.key === 'r') {
        resetAnnotations()
      }
      if (event.code === 'Space') {
        setIsActive(false)
      }
      if (event.key === 'Backspace') {
        undoAnnotation()
      }
    };

    // Écouter l'événement keydown sur l'élément document
    document.addEventListener('keydown', handleKeyPress);

    // Nettoyer l'écouteur d'événement lors du démontage du composant
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [indexImg,previousIndexImg,urlImg,previousUrlImg, annotatedImages]);

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

    if (isActive) {
      interval = setInterval(() => {
        setSeconds((prevSeconds) => prevSeconds + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className="App">
      <header className="App-header">
        <img className='App-logo-borelli' src="/images/logoBorelli.png"/>
        <h1 className='App-title'>Binary annotation</h1>
        <h3 className='App-annotated-images'> Annotated images: {annotatedImages}</h3>
        <p className='App-cronometer'>{seconds} seconds</p>
        <p className='App-cronometer'>{imgPerSec} img/s</p>
        {imageSrc && (
          <div>
            <img className='App-img' src={imageSrc}/>
          </div>
        )}
        <div className='App-container-button'>
          <button className='App-button' onClick={() => annotateImage(true)}> Dog (positive) <br/> or press F </button>
          <button className='App-button' onClick={() => annotateImage(false)}> Cat (negative) <br/> or press J </button>
          <button className='App-button' onClick={() => undoAnnotation()}>Undo (or press backspace)</button>
        </div>
        <p style={{fontSize:15}}>Press space to pause the timer and r to reset it</p>
      </header>
    </div>
  );
}

export default App;
