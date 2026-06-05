from django.urls import path
from decouple import config
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import welcome_view, root_view

ENVIRONMENT = config("ENVIRONMENT", default="development")

urlpatterns = [
    path("welcome", welcome_view, name="welcome"),
]

if ENVIRONMENT == "development":
    urlpatterns += [
        path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
else:
    urlpatterns += [
        path("", root_view, name="root"),
    ]
