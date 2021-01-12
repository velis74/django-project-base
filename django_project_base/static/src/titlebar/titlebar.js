class TitleBar extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.innerHTML = `
<header class="title-bar">
<title-bar-button>jhkdjhghjkdgjkd</title-bar-button>
<title-bar-button>ooppooo</title-bar-button>
<title-bar-button>iiioioiioio</title-bar-button>
</header>
`;
  }
}

window.customElements.define('title-bar', TitleBar);