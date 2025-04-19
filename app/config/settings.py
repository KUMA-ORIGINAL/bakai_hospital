from datetime import timedelta
from pathlib import Path

import environ
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from import_export.formats.base_formats import XLSX

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

SECRET_KEY = env('SECRET_KEY')

DEBUG = bool(env("DEBUG", default=0))

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(" ")

DOMAIN = env("DOMAIN")

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "Accept"]

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    'daphne',
    'modeltranslation',
    'unfold',
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.postgres",

    'rest_framework',
    'drf_spectacular',
    'django_filters',
    'corsheaders',
    "import_export",
    "simple_history",
    'channels',

    'account',
    'services',
    'organizations',
    'transactions',
    'common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
    'config.middleware.LanguageMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / "common/common_static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

OPENAI_API_KEY=env('OPENAI_API_KEY')

PAYMENT_API_TOKEN = env('PAYMENT_API_TOKEN')

LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
    ('ky', 'Kyrgyz'),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en', 'ky')
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('ru',),
    'en': ('ru', 'ky'),
    'ky': ('ru',),
}
MODELTRANSLATION_AUTO_POPULATE = True

EXPORT_FORMATS = [XLSX]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_TRUSTED_ORIGINS = [f"https://{DOMAIN}", f"http://{DOMAIN}"]

AUTH_USER_MODEL = 'account.User'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": ['redis://redis:6379/2'],
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hospital',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SCHEMA_VERSION': '3.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CAMELIZE_NAMES': True,

    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields',
    ],

    'SERVE_PUBLIC': True,
    'SERVE_HTTPS': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "AUTH_HEADER_TYPES": ("Bearer",),
    'UPDATE_LAST_LOGIN': True,
}

DJOSER = {
    # 'SERIALIZERS': {
    #     'user': 'account.serializers.UserSerializer',
    #     'current_user': 'account.serializers.UserSerializer',
    # },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} - {asctime} - {module} - {name} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django_app.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'account': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

UNFOLD = {
    "SITE_TITLE": 'Национальный госпиталь',
    "SITE_HEADER": "Национальный госпиталь",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("icons/icon.svg"),
        "dark": lambda request: static("icons/icon.svg"),
    },
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "LOGIN": {
        "image": lambda request: static("icons/login-bg.webp"),
    },
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "base": {
            "50": "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
          "50": "239 246 255",
          "100": "219 234 254",
          "200": "191 219 254",
          "300": "147 197 253",
          "400": "96 165 250",
          "500": "59 130 246",
          "600": "37 99 235",
          "700": "29 78 216",
          "800": "30 64 175",
          "900": "30 58 138",
          "950": "23 37 84"
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Навигация"),
                "items": [
                    {
                        "title": _("Организация"),
                        "icon": "corporate_fare",
                        "link": reverse_lazy("admin:organizations_organization_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                    {
                        "title": _("Здания"),
                        "icon": "location_city",
                        "link": reverse_lazy("admin:organizations_building_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                    {
                        "title": _("Отделы"),
                        "icon": "account_tree",
                        "link": reverse_lazy("admin:organizations_department_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                    {
                        "title": _("Кабинеты"),
                        "icon": "meeting_room",
                        "link": reverse_lazy("admin:organizations_room_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                ],
            },
            {
                "title": _("Услуги"),
                "separator": True,
                "items": [
                    {
                        "title": _("Услуги"),
                        "icon": "construction",
                        "link": reverse_lazy("admin:services_service_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                    {
                        "title": _("Категории"),
                        "icon": "category",
                        "link": reverse_lazy("admin:services_category_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                ],
            },
            {
                "title": _("Счета для выплат"),
                "separator": True,
                "items": [
                    {
                        "title": _("Счета для выплат"),
                        "icon": "payments",
                        "link": reverse_lazy("admin:services_payoutaccount_changelist"),
                    },
                ],
            },
            {
                "title": _("Транзакции"),
                "separator": True,
                "items": [
                    {
                        "title": _("Транзакции"),
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy("admin:transactions_transaction_changelist"),
                    },
                ],
            },
            {
                "title": _("Пациенты"),
                "separator": True,
                "items": [
                    {
                        "title": _("Пациенты"),
                        "icon": "person",
                        "link": reverse_lazy("admin:account_patient_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_accountant',
                    },
                ],
            },
            {
                "title": _("Пользователи"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:account_user_changelist"),
                        'permission': 'account.admin_permissions.permission_callback_for_doctor_and_accountant',
                    },
                ],
            },
            {
                "title": _("Группы"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Группы"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        'permission': 'account.admin_permissions.permission_callback',
                    },
                ],
            },
        ],
    },
}