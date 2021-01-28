import {apiClient as ApiClient} from '../../apiClient';
import {Store} from '../../store';

class TitleBarData {
  constructor() {
    this.projectData = {
      companyImageLogoUrl: '',
      companyTitle: '',
    };
    this.userProfileData = {
      avatarImageUrl: '',
      firstName: '',
      lastName: '',
      userTitle: '',
    };
  }

  getTitleBarData(callback) {
    const projectPk = Store.get('current-project').id;
    if (!projectPk) {
      console.log('No params for titlebar data retrieval');
      return;
    }
    ApiClient.get('dpb-rest/project/' + projectPk).then(projectResponse => {
      this.projectData.companyImageLogoUrl = projectResponse.data.logo;
      this.projectData.companyTitle = projectResponse.data.name;
      callback(this.projectData);
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

  getUserProfileData(callback) {
    const userPk = Store.get('current-user').id;
    if (!userPk) {
      console.log('No params for user profile data retrieval');
      return;
    }
    ApiClient.get('dpb-rest/profile/' + userPk).then(profileResponse => {
      this.userProfileData.avatarImageUrl = profileResponse.data.avatar;
      // todo: replace avata with real image
      this.userProfileData.avatarImageUrl = 'https://via.placeholder.com/45';
      this.userProfileData.firstName = profileResponse.data.first_name;
      this.userProfileData.lastName = profileResponse.data.last_name;
      this.userProfileData.userTitle = 'Developer';
      callback(this.userProfileData);
    }).catch(errors => {
      console.error(errors);
    });
  }
}

export {TitleBarData};