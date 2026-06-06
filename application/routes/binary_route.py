from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import permissions
from rest_framework.views import APIView

from domain.Services.binary_service import BinaryService

@extend_schema(
    summary="Recebe um json e retorna em formato binario",
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
            description="PDF Binary Document"
        )
    }
)
class BinaryRoute(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        response_quest = BinaryService().execute(data)

        return HttpResponse(
            response_quest,
            content_type="application/pdf"
        )
