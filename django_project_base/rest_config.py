class AccountBase:
    url = ''
    basename = 'account'


class REST_API_CONFIG:
    class Project:
        url = 'project'
        basename = 'project-base-project'

    class MaintenanceNotification:
        url = 'maintenance-notification'
        basename = 'maintenance-notification'

    class Account(AccountBase):
        class Login(AccountBase):
            pass

        class Logout(AccountBase):
            pass

        class ChangePassword:
            url = 'change-password'
            basename = 'change-password'

        class ResetPassword(AccountBase):
            pass

        class Register(AccountBase):
            pass

        class ResetPasswordLink(AccountBase):
            pass

        class VerifyRegistration(AccountBase):
            pass

    class Profile:
        url = 'profile'
        basename = 'profile-base-project'

    class Impersonate:
        url = 'impersonate'
        basename = 'profile-base-impersonate-user'
