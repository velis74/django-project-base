SOCIAL_AUTH_SETTINGS = (
    {
        "name": "AUTHENTICATION_BACKENDS",
        "default": (
            "social_core.backends.facebook.FacebookOAuth2",
            "social_core.backends.google.GoogleOAuth2",
            "social_core.backends.twitter.TwitterOAuth",
            "social_core.backends.microsoft.MicrosoftOAuth2",
            "social_core.backends.github.GithubOAuth2",
            "social_core.backends.gitlab.GitLabOAuth2",
            # 'social_core.backends.apple.AppleIdAuth', # not fully tested yet
        ),
        "description": "Social login authentication backends. Add desired authentication backends to "
        "Django’s AUTHENTICATION_BACKENDS setting.",
    },
    {
        "name": "SOCIAL_AUTH_REDIRECT_IS_HTTPS",
        "default": False,
        "description": "On projects behind a reverse proxy that uses HTTPS, the redirect URIs can have the wrong "
        "schema (http:// instead of https://) if the request lacks the appropriate headers, which might "
        "cause errors during the auth process. To force HTTPS in the "
        "final URIs set this setting to True",
    },
    {
        "name": "SOCIAL_AUTH_LOGIN_REDIRECT_URL",
        "default": "/",
        "description": "Used to redirect the user once the auth process ended successfully. "
        "The value of ?next=/foo is used if it was present",
    },
    {
        "name": "SOCIAL_AUTH_PIPELINE",
        "default": (
            "social_core.pipeline.social_auth.social_details",
            "social_core.pipeline.social_auth.social_uid",
            "social_core.pipeline.social_auth.auth_allowed",
            "social_core.pipeline.social_auth.social_user",
            "social_core.pipeline.user.get_username",
            "social_core.pipeline.social_auth.associate_by_email",
            "social_core.pipeline.user.create_user",
            "social_core.pipeline.social_auth.associate_user",
            "social_core.pipeline.social_auth.load_extra_data",
            "social_core.pipeline.user.user_details",
        ),
        "description": "python-social-auth authentication workflow pipeline. The default pipeline is a mechanism "
        "that creates user instances and gathers basic data from providers.",
    },
)
