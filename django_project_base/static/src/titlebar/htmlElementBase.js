import '@webcomponents/webcomponentsjs/webcomponents-bundle';
import '@webcomponents/webcomponentsjs/custom-elements-es5-adapter.js';
import '@fortawesome/fontawesome-free/css/all.css';


class HtmlElementBase extends HTMLElement {
  constructor() {
    super();
  }

  getBootstrapTemplate() {
    return `
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

    .display-inline {
      display: inline-block;
    }
    
    .logo-image {
      cursor: default;
      max-height: 80px;
      max-width: 80px;
    }
</style>

<nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="nav-item">
      <div class="card">
          <div class="card-body">
              <img src=${this.getAttribute("logo-img-source")}
              class="float-left rounded-circle logo-image" onclick="window.location.href='/'" style="cursor: pointer;">
          </div>
      </div>
    </div>
    <a class="navbar-brand" href="javascript:void(0);" style="cursor: default;"> ${this.getAttribute("title")}</a>
    <div class="nav-item">
      <div class="card">
          <div class="card-body">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="#">Home</a></li>
                    <li class="breadcrumb-item"><a href="#">First Page</a></li>
                    <li class="breadcrumb-item active" aria-current="page">Library</li>
                </ol>
            </nav>
          </div>
      </div>
    </div>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
<!--            this ul serves as placeholder-->
        </ul>
        <div class="nav-item">
            <div>
                <div class="display-inline">
                    <i class="fas fa-th-list fa-2x"></i>
                </div>
                <div class="display-inline">
                    <h6 class="card-title"> Projects</h6>
                </div>
            </div>
        </div>

        <div class="nav-item">
            <div class="card">
                <div class="card-body">
                    <img src="${this.getAttribute('avatar')}" class="float-left rounded-circle">
                    <div class="message">
                        <h6 class="card-title"> ${this.getAttribute('profile-first-name')}</h6>
                        <h7 class="card-subtitle mb-2 text-muted"> ${this.getAttribute('profile-title')}</h7>
                    </div>
                </div>
            </div>
        </div>
    </div>
</nav>
`
  }
}

export {HtmlElementBase};