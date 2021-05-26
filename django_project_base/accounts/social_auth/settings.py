SOCIAL_AUTH_SETTINGS = (
    {
        "name": "AUTHENTICATION_BACKENDS",
        "default": (
            'social_core.backends.facebook.FacebookOAuth2',
            'social_core.backends.google.GoogleOAuth2',
            'social_core.backends.twitter.TwitterOAuth',
            'social_core.backends.microsoft.MicrosoftOAuth2',
            'social_core.backends.github.GithubOAuth2',
            'social_core.backends.gitlab.GitLabOAuth2',
            # 'social_core.backends.apple.AppleIdAuth', # not fully tested yet
        ),
        "description": "jkhdjkfgshgjkd",
    },
    {
        "name": "SOCIAL_AUTH_REDIRECT_IS_HTTPS",
        "default": False,
        "description": "adfadsfsdf",
    },
    {
        "name": "SOCIAL_AUTH_LOGIN_REDIRECT_URL",
        "default": "/",
        "description": "dfshshdfg",
    },
    {
        "name": "SOCIAL_AUTH_PIPELINE",
        "default": (
            'social_core.pipeline.social_auth.social_details',
            'social_core.pipeline.social_auth.social_uid',
            'social_core.pipeline.social_auth.auth_allowed',
            'social_core.pipeline.social_auth.social_user',
            'social_core.pipeline.user.get_username',
            'social_core.pipeline.social_auth.associate_by_email',
            'social_core.pipeline.user.create_user',
            'social_core.pipeline.social_auth.associate_user',
            'social_core.pipeline.social_auth.load_extra_data',
            'social_core.pipeline.user.user_details',
        ),
        "description": "dfhadfhadfhadf",
    },
)

# SOCIAL_AUTH_FACEBOOK_KEY = '323344492460681'  # App ID
# SOCIAL_AUTH_FACEBOOK_SECRET = 'd61f296bdffa4cff01f3e48092a51805'  # App Secret
# SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_link']  # add this
# SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {  # add this
#     'fields': 'id, name, email, picture.type(large), link'
# }
# SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [  # add this
#     ('name', 'name'),
#     ('email', 'email'),
#     ('picture', 'picture'),
#     ('link', 'profile_url'),
# ]
#
# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '510787478378-afi3ga5m6rj23c9h2sm47563prkk3kd4.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'b0tXbSnBrRL1UvoXpqQLCY3d'
#
# SOCIAL_AUTH_TWITTER_KEY = 'sRjQ9TBGViJ7P9QpkGlkRTTGN'
# SOCIAL_AUTH_TWITTER_SECRET = 'bJKyeeniqMeHTw9ZvTbmCcyLphjTo8y8TFpwWKCHpGTlbcdVJz'
# SOCIAL_AUTH_TWITTER_EXTRA_DATA = [  # add this
#     ('email', 'email'),
# ]
#
# SOCIAL_AUTH_MICROSOFT_GRAPH_KEY = 'c3609cf2-8999-4abd-8f76-90d20c6069ee'
# SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET = '4pkq_9.~EKFGI~N3S1r8ZF78aSV._Vq9_T'
# SOCIAL_AUTH_MICROSOFT_GRAPH_REDIRECT_URL = 'http://localhost:8080/oauth/complete/microsoft-graph/'
#
# SOCIAL_AUTH_GITHUB_KEY = '523b13a70d8ece2a64eb'
# SOCIAL_AUTH_GITHUB_SECRET = '0945595ac7fcfb13ab0039dcc35d21e4cfb62438'
#
# SOCIAL_AUTH_GITLAB_KEY = '8c55f7a7912587ce828ad7cf1ed83590aa5671f056f59b0220335939c3a8b1fa'
# SOCIAL_AUTH_GITLAB_SECRET = '016756b4f2d9c8fe7d7032bc14c8f34c351d05fca27fe06ad642dc5bd77630c9'
#
# SOCIAL_AUTH_APPLE_ID_CLIENT = '...'             # Your client_id com.application.your, aka "Service ID"
# SOCIAL_AUTH_APPLE_ID_TEAM = '...'               # Your Team ID, ie K2232113
# SOCIAL_AUTH_APPLE_ID_KEY = '...'                # Your Key ID, ie Y2P99J3N81K
# SOCIAL_AUTH_APPLE_ID_SECRET = """
# -----BEGIN PRIVATE KEY-----
# MIGTAgE.....
# -----END PRIVATE KEY-----"""
# SOCIAL_AUTH_APPLE_ID_SCOPE = ['email', 'name']
