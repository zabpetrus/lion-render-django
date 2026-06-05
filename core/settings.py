INSTALLED_APPS = [
    "rest_framework",
    "drf_spectacular",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
