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
    };
  }

  getData(callback) {
    const projectRequest = ApiClient.get('rest/project/1');
    const profileRequest = ApiClient.get('rest/profile/2');

    axios.all([projectRequest, profileRequest]).then((responses) => {
      const projectResponse = responses[0];
      const profileResponse = responses[1];
      this.data.companyImageLogoUrl = projectResponse.data.logo;
      this.data.avatarImageUrl = profileResponse.data.avatar;

      // todo: replace avata with real image
      this.data.avatarImageUrl = 'https://via.placeholder.com/45';

      this.data.companyTitle = projectResponse.data.name;
      this.data.firstName = profileResponse.data.first_name;
      this.data.lastName = profileResponse.data.last_name;
      this.data.userTitle = 'Developer';
      callback(this.data);
    }).catch(errors => {
      console.log(errors);
    });
  }
}

export {TitlebarData};