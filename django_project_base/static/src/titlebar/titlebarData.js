import {apiClient as ApiClient} from "../ajax/apiClient";
import axios from "axios";

class TitlebarData {
  constructor() {
    this.data = {
      companyImageLogoUrl: '',
      companyTitle: '',
      avatarImageUrl: '',
      firstName: '',
      lastName: '',
      userTitle: '',
      projects: [],
    };
  }

  getData(callback) {
    const projectRequest = ApiClient.get('rest/project/1');
    const profileRequest = ApiClient.get('rest/profile/2');
    const projectListRequest = ApiClient.get('rest/project');

    axios.all([projectRequest, profileRequest, projectListRequest]).then((responses) => {
      const projectResponse = responses[0];
      const profileResponse = responses[1];
      const projectListResponse = responses[2];
      this.data.companyImageLogoUrl = projectResponse.data.logo;
      this.data.avatarImageUrl = profileResponse.data.avatar;
      this.data.companyTitle = projectResponse.data.name;
      this.data.firstName = profileResponse.data.first_name;
      this.data.lastName = profileResponse.data.last_name;
      this.data.userTitle = 'Developer';
      this.data.projects = projectListResponse.data;
      callback(this.data);
    }).catch(errors => {
      console.log(errors);
    });
  }
}

export {TitlebarData};