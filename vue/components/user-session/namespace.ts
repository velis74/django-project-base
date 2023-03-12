namespace UserSession {
  export interface UserDataJSON {
    id: number | string,
    first_name: string,
    last_name: string,
    email: string,
    username: string,
    avatar: string;
  }

  export interface UserData {
    id: number | string,
    firstName: string,
    lastName: string,
    email: string,
    username: string,
    avatar: string;
  }

  interface SessionInterface {
    login(username: string, password: string): undefined;
    logout(): undefined;
    checkLogin(showNotAuthorizedNotice: boolean): undefined;
  }

  export interface UserSessionData {
    userData: UserData;
    impersonated: boolean;
  }
}
