from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import permissions
from rest_framework.views import APIView

from domain.Services.base64_service import Base64Service

@extend_schema(
    summary="Recebe um json e retorna em formato string base64",
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
            description="PDF Base64 Document"
        )
    }
)
class Base64Route(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pdf_bytes = Base64Service().execute(
            request.data
        )

        return HttpResponse(
            pdf_bytes,
            content_type="application/pdf"
        )