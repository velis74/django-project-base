import {BOOTSTRAP_TEMPLATE_TYPE} from './config';
import {HtmlElementBase} from './htmlElementBase';
import {TitlebarData} from "./titlebarData";
import {apiClient as ApiClient} from "../ajax/apiClient";

class TitleBar extends HtmlElementBase {
  constructor() {
    super();
    this.companyImageLogoUrl = '';
    this.avatarImageUrl = '';
    this.firstName = '';
    this.lastName = '';
    this.userTitle = '';
  }

  static get observedAttributes() {
    return ['template'];
  }

  connectedCallback() {
    let titleBarData = new TitlebarData();
    titleBarData.getData((tData) => {
      this.setAttribute('logo-img-source', tData.companyImageLogoUrl);
      this.setAttribute('title', tData.companyTitle);
      this.setAttribute('profile-first-name', tData.firstName);
      this.setAttribute('profile-title', tData.userTitle);
      this.setAttribute('avatar', tData.avatarImageUrl);

      if (!this.templateType) {
        this.templateType = BOOTSTRAP_TEMPLATE_TYPE;
      }
      if (this.templateType === BOOTSTRAP_TEMPLATE_TYPE) {
        this.innerHTML = this.getBootstrapTemplate();
      }
    });

    ApiClient.get('rest/project').then(response => {
      console.log(response.data);
    });
  }

  render() {
    this.innerHTML = this.getBootstrapTemplate();
  }

  attributeChangedCallback(attrName, oldVal, newVal) {
    console.log(oldVal, newVal);
  }
}

export default TitleBar;