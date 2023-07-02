const playIconContainer = document.getElementById("play-icon");
const audioPlayerContainer = document.getElementById("audio-player-container");
const volumeSlider = document.getElementById("volume-slider");
let playing = false;
let muteState = "unmute";
const audio = document.querySelector("audio");
audio.crossOrigin = "anonymous";
const outputContainer = document.getElementById("volume-output");

playIconContainer.addEventListener("click", () => {
  if (!playing) {
    audio.play();
    playIconContainer.innerHTML = "Pause &#9208;";
    playing = true;
    if (!analyserInitialized) {
      initAnalyzer();
    }
  } else {
    audio.pause();
    playIconContainer.innerHTML = "Play &#9654;";
    playing = false;
  }
});

const showRangeProgress = (rangeInput) => {
  audioPlayerContainer.style.setProperty(
    "--volume-before-width",
    (rangeInput.value / rangeInput.max) * 100 + "%"
  );
};

volumeSlider.addEventListener("input", (e) => {
  showRangeProgress(e.target);
  const value = e.target.value;
  outputContainer.textContent = value;
  audio.volume = value / 100;
});

// Establish all variables that your Analyser will use
var canvas,
  ctx,
  source,
  context,
  analyser,
  fbcArray,
  bars,
  barX,
  barWidth,
  barHeight,
  analyserInitialized = false;

function initAnalyzer() {
  context = new AudioContext();
  analyser = context.createAnalyser();
  canvas = document.getElementById("analyser_render");
  ctx = canvas.getContext("2d");
  source = context.createMediaElementSource(audio);
  source.connect(analyser);
  analyser.connect(context.destination);
  analyserInitialized = true;
  frameLooper();
}

// frameLooper() animates any style of graphics you wish to the audio frequency
// Looping at the default frame rate that the browser provides(approx. 60 FPS)
function frameLooper() {
  window.requestAnimationFrame(frameLooper);
  fbcArray = new Uint8Array(analyser.frequencyBinCount);
  analyser.getByteFrequencyData(fbcArray);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#014b08";

  const barWidth = 10;
  const space = 1;
  const bars = Math.floor(canvas.width / (barWidth + space));
  let arrayLen = fbcArray.length;

  // We are on a browser that doesn't support analyser
  if (isUint8ArrayEmpty(fbcArray) && playing) {
    if (oldBandValues.length === 0) {
      bands = bars;
      getFFT(oldBandValues);
    }
    getFFT(bandValues);
    fbcArray = generateFrequencyArray();
    arrayLen = fbcArray.length;
  } else {
    // High frequency values are mostly 0
    arrayLen = fbcArray.length - 350;
  }

  for (var i = 0; i < bars; i++) {
    barX = i * (barWidth + space);
    const fbcArrayi = Math.floor(convertRange(i, [0, bars], [0, arrayLen]));
    barHeight = -Math.floor(
      convertRange(fbcArray[fbcArrayi], [0, 255], [0, canvas.height])
    );
    ctx.fillRect(barX, canvas.height, barWidth, barHeight);
  }
}

function convertRange(value, r1, r2) {
  return ((value - r1[0]) * (r2[1] - r2[0])) / (r1[1] - r1[0]) + r2[0];
}

function isUint8ArrayEmpty(arr) {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] !== 0) {
      return false;
    }
  }
  return true;
}

let bandValues = [];
let oldBandValues = [];
let bands = 1;

function generateFrequencyArray() {
  const ret = [];
  for (var i = 0; i < bands; i++) {
    b = calcBand(i);
    b = convertRange(b, [0, 1], [0, 255]);
    ret.push(b);
  }
  return ret;
}

function calcBand(bandNum) {
  var bv = bandValues[bandNum],
    obv = oldBandValues[bandNum];

  if (bv >= obv) obv = bv;
  obv -= 0.01;
  if (obv < 0) obv = 0;

  oldBandValues[bandNum] = obv;
  return obv;
}

function getFFT(band) {
  band = band ? band : bandValues;
  for (var i = 0; i < bands; i++) {
    band[i] = Math.random() * 0.8;
  }
}
