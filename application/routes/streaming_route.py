from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from domain.Services.streaming_service import StreamingService


@extend_schema(
    summary="Recebe um json e retorna em formato streaming",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string"
                },
                "content": {
                    "type": "string"
                }
            },
            "required": [
                "title",
                "content"
            ]
        }
    },

    examples=[
        OpenApiExample(
            "example",
            value={
                "title": "Docs",
                "content": "Hello"
            }
        )
    ],

    responses={
        200: OpenApiResponse(
            description="PDF Streaming Document",
        )
    }
)

class StreamingRoute(APIView):
    permission_classes = (IsAuthenticated, permissions.AllowAny)

    def post(self, request, *args, **kwargs):
        data = request.data
        response_info = StreamingService().execute(data)

        return HttpResponse(
            response_info,
            content_type="application/pdf"
        )
