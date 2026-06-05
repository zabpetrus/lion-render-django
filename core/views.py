from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    summary="Bem-vindo",
    description="Retorna uma mensagem de boas-vindas da API.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "status": {"type": "string"},
                "version": {"type": "string"},
            },
        }
    },
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={"message": "Bem-vindo à API!", "status": "online", "version": "1.0.0"},
            response_only=True,
        )
    ],
)
@api_view(["GET"])
def welcome_view(request):
    return Response(
        {
            "message": "Bem-vindo à API!",
            "status": "online",
            "version": "1.0.0",
        }
    )


@api_view(["GET"])
def root_view(request):
    return Response(
        {
            "message": "API no ar. Acesse /welcome para começar.",
            "docs": "Disponível apenas em ambiente de desenvolvimento.",
        }
    )
