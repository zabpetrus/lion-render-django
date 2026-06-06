from django.urls import path
from decouple import config
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from application.routes.base64_route import Base64Route
from application.routes.binary_route import BinaryRoute
from application.routes.streaming_route import StreamingRoute
from .views import welcome_view, root_view

ENVIRONMENT = config("ENVIRONMENT", default="development")

urlpatterns = [
    path("welcome", welcome_view, name="welcome"),
    path("base", Base64Route.as_view(), name="base64-pdf" ),
    path("binary", BinaryRoute.as_view(), name="binary-pdf"),
    path("streaming", StreamingRoute.as_view(), name="streaming-pdf"),
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
