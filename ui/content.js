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
