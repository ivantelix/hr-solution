"""
ViewSet para gestión de posts de redes sociales.

Este módulo contiene las vistas para gestionar los posts de redes sociales
asociados a vacantes.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.recruitment.models import VacancySocialPost
from apps.recruitment.serializers import VacancySocialPostSerializer
from apps.recruitment.services import SocialMediaContentGenerator


class SocialPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar posts de redes sociales.

    Endpoints:
    - GET /api/recruitment/social-posts/?vacancy={id} - Lista posts de una vacante
    - GET /api/recruitment/social-posts/{id}/ - Detalle de un post
    - PUT /api/recruitment/social-posts/{id}/ - Editar post
    - POST /api/recruitment/social-posts/{id}/regenerate/ - Regenerar contenido
    - PATCH /api/recruitment/social-posts/{id}/mark-published/ - Marcar como publicado
    """

    serializer_class = VacancySocialPostSerializer
    queryset = VacancySocialPost.objects.all()

    def get_queryset(self):
        """Filtra posts por vacancy_id si se proporciona como query param."""
        queryset = VacancySocialPost.objects.all()
        vacancy_id = self.request.query_params.get("vacancy", None)
        
        if vacancy_id:
            queryset = queryset.filter(vacancy_id=vacancy_id)
        
        return queryset

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """
        Regenera el contenido de un post usando IA.

        POST /api/recruitment/social-posts/{id}/regenerate/
        """
        social_post = self.get_object()

        try:
            generator = SocialMediaContentGenerator()
            updated_post = generator.regenerate_post(social_post)

            serializer = self.get_serializer(updated_post)
            return Response(
                {
                    "message": "Contenido regenerado exitosamente",
                    "post": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Error al regenerar contenido: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["patch"])
    def mark_published(self, request, pk=None):
        """
        Marca un post como publicado manualmente.

        PATCH /api/recruitment/social-posts/{id}/mark-published/
        """
        social_post = self.get_object()

        # Actualizar status y timestamp
        social_post.status = "published"
        social_post.manually_published_at = timezone.now()
        if not social_post.posted_at:
            social_post.posted_at = timezone.now()
        social_post.save(
            update_fields=["status", "manually_published_at", "posted_at", "updated_at"]
        )

        serializer = self.get_serializer(social_post)
        return Response(
            {
                "message": "Post marcado como publicado",
                "post": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
