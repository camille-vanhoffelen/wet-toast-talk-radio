let md = window.markdownit({ html: true });
let mdEmoji = window.markdownitEmoji;
md.use(mdEmoji);
const windowContentContainer = document.getElementById("window-content");
const contentMap = new Map();

// https://markdown-it.github.io/

const aboutContent = `
:question: What is __Wet Toast Talk Radio__? :question:

__Wet Toast Talk Radio__ is a 24h non stop __AI__ generated radio. :robot:

It's a __live__ radio, so it's always different and new content is generated every day.

To get started simply click the play button on the radion player and enjoy the show! :notes:

:warning: Radio content may be __explicit__. :warning:

If the audio stops, pls reload the page :)
`;
contentMap.set("about-tab", aboutContent);

const twitchContent = `
Coming soon!
`;
contentMap.set("twitch-tab", twitchContent);

const teamContent = `
This project was built by a team of 2 people:

- __Camille Van Hoffelen__
<a href="https://github.com/camille-vanhoffelen" target="_blank">
  <img alt="Camille's Github" width="20px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/github.svg"/>
</a>
<a href="https://linkedin.com/in/camillevanhoffelen" target="_blank">
  <img alt="Camille's Linkedin" width="20px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg"/>
</a>
- __Raphael Van Hoffelen__
<a href="https://github.com/dskart" target="_blank">
  <img alt="Raphael's Github" width="20px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/github.svg"/>
</a>
<a href="https://www.linkedin.com/in/raphael-van-hoffelen-ba6393137" target="_blank">
  <img alt="Raphael's Linkedin" width="20px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg"/>
</a>
`;
contentMap.set("team-tab", teamContent);

let statsContent = `
- current listeners: 0
- peak listeners: 0
- stream hits: 0
- stream status: offline
`;
contentMap.set("stats-tab", statsContent);

function setWindowContent(contentId) {
  windowContentContainer.innerHTML = md.render(contentMap.get(contentId));
}

let currentTabContainer = document.getElementById("about-tab");
function showContentMenu(containerId) {
  const container = document.getElementById(containerId);
  currentTabContainer.setAttribute("aria-selected", "false");
  container.setAttribute("aria-selected", "true");
  setWindowContent(containerId);
  currentTabContainer = container;
}

showContentMenu("about-tab");

// This is a weird hack to get the stats from Voscast
var script_64a1bc49a2561;
async function getStats() {
  if (script_64a1bc49a2561) {
    document.getElementsByTagName("head")[0].removeChild(script_64a1bc49a2561);
  }
  script_64a1bc49a2561 = document.createElement("script");
  script_64a1bc49a2561.src =
    "https://cdn.voscast.com/stats/display.js?key=4c77e9351768272efcf928eddfd4317d&stats=currentlisteners,songtitle,peaklisteners,streamhits,streamstatus&bid=64a1bc49a2561&action=update";
  document.getElementsByTagName("head")[0].appendChild(script_64a1bc49a2561);
}

let currentSong = "";
function updateStats_64a1bc49a2561(result) {
  const r =
    result[
      "currentlisteners,songtitle,peaklisteners,streamhits,streamstatus"
    ].split(",");
  const listeners = r[0];
  const song = r[1];
  const peakListeners = r[2];
  const streamHits = r[3];
  const streamStatus = r[4] === "1" ? "online" : "offline";
  if (song !== currentSong) {
    currentSong = song;
    console.log("Now playing: " + song);
  }
  statsContent = `
- current listeners: **${listeners}**
- peak listeners: **${peakListeners}**
- stream hits: **${streamHits}**
- stream status: **${streamStatus}**
`;
  contentMap.set("stats-tab", statsContent);
  if (
    document.getElementById("stats-tab").getAttribute("aria-selected") ===
    "true"
  ) {
    showContentMenu("stats-tab");
  }
}

getStats();
setInterval("getStats()", 600000);
