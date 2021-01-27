import {apiClient as ApiClient} from '../../apiClient';
import axios from 'axios';
import {Store} from '../../store';

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

  getTitleBarData(callback) {
    const projectPk = Store.get('current-project').id;
    const userPk = Store.get('current-user').id;
    if (!projectPk || !userPk) {
      console.log('No params for data retrieval');
      return;
    }

    const projectRequest = ApiClient.get('dpb-rest/project/' + projectPk);
    const profileRequest = ApiClient.get('dpb-rest/profile/' + userPk);

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
      console.error(errors);
    });
  }

  getProjects(callback) {
    if (!Store.get('current-user')) {
      console.log('No logged in user');
      return;
    }
    ApiClient.get('dpb-rest/project').then(response => {
      callback(response.data);
    }).catch(error => {
      callback([]);
      console.error(error);
    });
  }

  getPermissions(callback) {
    let _permissions = {};
      const permissionPromise = new Promise((resolveCallback) => {
        setTimeout(() => {
          _permissions = {'add-project': true};
          resolveCallback();
        }, 2000);
      });
      permissionPromise.then(() => {
        console.log('pemrissions loaded');
        console.log(_permissions);
        callback(_permissions);
      });
    }
}

export {TitleBarData};