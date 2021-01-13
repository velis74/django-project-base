var template = `
<style>
    .card .card-body .message {
        padding-left: 45px;
    }
    
    .card .card-body .message::after {
      clear: both;
    }

    .card .card-body .actions {
      margin-top: 5px;
      background-color: transparent;
      border: none;
    }
    
    .card {
      background-color: transparent;
      border: none;
    }
</style>

<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <a class="navbar-brand" href="#">Company logo</a>


  <div class="collapse navbar-collapse" id="navbarSupportedContent">
    <ul class="navbar-nav mr-auto">
     
      
<!--      <li class="nav-item dropdown">-->
<!--        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">-->
<!--          Dropdown-->
<!--        </a>-->
<!--        <div class="dropdown-menu" aria-labelledby="navbarDropdown">-->
<!--          <a class="dropdown-item" href="#">Action</a>-->
<!--          <a class="dropdown-item" href="#">Another action</a>-->
<!--          <div class="dropdown-divider"></div>-->
<!--          <a class="dropdown-item" href="#">Something else here</a>-->
<!--        </div>-->
<!--      </li>-->
<!--      <li class="nav-item">-->
<!--        <a class="nav-link disabled" href="#">Disabled</a>-->
<!--      </li>-->
    </ul>
<!--    <form class="form-inline my-2 my-lg-0">-->
<!--      <input class="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search">-->
<!--      <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>-->
<!--    </form>-->
    
    <div class="nav-item">
      <div class="card">
        <div class="card-body">
          <img src="http://placehold.it/32x32" class="float-left rounded-circle">
          <div class="message">
            <h6 class="card-title">Name Surnamer</h6>
            <h7 class="card-subtitle mb-2 text-muted">Title</h7>
          </div>
        </div>
      </div>
  </div>
    
  </div>
</nav>
`;

import '@webcomponents/webcomponentsjs/webcomponents-bundle';
import '@webcomponents/webcomponentsjs/custom-elements-es5-adapter.js';

class TitleBar extends HTMLElement {
  constructor() {
    super();
  }

  static get observedAttributes() {
    return ['template'];
  }

  connectedCallback() {
    this.innerHTML = template;
    console.log(this.getAttribute('template'), 99);
  }

  attributeChangedCallback(attrName, oldVal, newVal) {
    console.log(oldVal, newVal);
  }
}
export default TitleBar;