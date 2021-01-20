import {apiClient as ApiClient} from '../../ajax/apiClient';
import axios from 'axios';
import {Store} from "../../store";

class TitleBarData {
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
    const projectPk = Store.get('current-project');
    const userPk = Store.get('current-user');
    if (!projectPk || !userPk) {
      alert('Title bar missing configuration'); // jshint ignore:line
      return;
    }

    const projectRequest = ApiClient.get('rest/project/' + projectPk);
    const profileRequest = ApiClient.get('rest/profile/' + userPk);

    return axios.all([projectRequest, profileRequest]).then((responses) => {
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
      console.error(errors);
    });
  }

  getProjects(callback) {
    ApiClient.get('rest/project').then(response => {
      callback(response.data);
    }).catch(error => {
      callback([]);
      console.error(error);
    });
  }
}

export {TitleBarData};