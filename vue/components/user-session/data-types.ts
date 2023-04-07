// todo: find a nicer solution, maybe some model functionality to keep data models metadata
export const PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME = 'slug' as const;
export const PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME = 'id' as const;

export interface UserDataJSON {
  [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: number | string,
  full_name: string,
  email: string,
  username: string,
  avatar: string;
  is_impersonated: boolean;
}

export interface UserData {
  [PROFILE_TABLE_PRIMARY_KEY_PROPERTY_NAME]: number | string,
  fullName: string,
  email: string,
  username: string,
  avatar: string;
}

export interface SessionInterface {
  login(username: string, password: string): undefined;

  logout(): undefined;

  checkLogin(showNotAuthorizedNotice: boolean): undefined;
}

export interface Project {
  [PROJECT_TABLE_PRIMARY_KEY_PROPERTY_NAME]: any;
  logo: string;
  name: string;
}

export interface UserSessionData {
  userData: UserData;
  impersonated: boolean;
  selectedProject: Project;
}
