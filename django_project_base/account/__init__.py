from .constants import ACCOUNT_APP_ID
from .middleware import SessionMiddleware  #noqa

default_app_config = "%s.apps.DjangoProjectBaseAccountsConfig" % ACCOUNT_APP_ID
