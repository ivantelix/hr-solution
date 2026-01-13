"""
Servicio para generación de contenido de redes sociales con IA.

Este módulo contiene la lógica para generar contenido optimizado
para diferentes plataformas sociales usando Gemini LLM.
"""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from apps.recruitment.models import JobVacancy, SocialPlatform, VacancySocialPost

logger = logging.getLogger(__name__)


class SocialMediaContentGenerator:
    """
    Generador de contenido para redes sociales usando IA.

    Utiliza Gemini LLM para crear posts optimizados según la plataforma.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI | None = None):
        """
        Inicializa el generador.

        Args:
            llm: Instancia de LLM. Si es None, crea una nueva con Gemini.
        """
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
        )

    def generate_posts_for_vacancy(
        self, vacancy: JobVacancy, platforms: list[str]
    ) -> list[VacancySocialPost]:
        """
        Genera posts para múltiples plataformas sociales.

        Args:
            vacancy: Vacante para la cual generar contenido.
            platforms: Lista de plataformas (ej: ["linkedin", "twitter"]).

        Returns:
            Lista de VacancySocialPost creados.
        """
        created_posts = []

        for platform in platforms:
            try:
                content = self._generate_content_for_platform(vacancy, platform)
                post = VacancySocialPost.objects.create(
                    vacancy=vacancy,
                    platform=platform,
                    content=content,
                    status="draft",
                )
                created_posts.append(post)
                logger.info(
                    f"Generated {platform} post for vacancy {vacancy.id}"
                )
            except Exception as e:
                logger.error(
                    f"Error generating {platform} post for vacancy {vacancy.id}: {e}"
                )
                # Continuar con las demás plataformas

        return created_posts

    def regenerate_post(self, social_post: VacancySocialPost) -> VacancySocialPost:
        """
        Regenera el contenido de un post existente.

        Args:
            social_post: Post a regenerar.

        Returns:
            Post actualizado con nuevo contenido.
        """
        new_content = self._generate_content_for_platform(
            social_post.vacancy, social_post.platform
        )
        social_post.content = new_content
        social_post.save(update_fields=["content", "updated_at"])

        logger.info(
            f"Regenerated {social_post.platform} post for vacancy {social_post.vacancy.id}"
        )
        return social_post

    def _generate_content_for_platform(
        self, vacancy: JobVacancy, platform: str
    ) -> str:
        """
        Genera contenido específico para una plataforma.

        Args:
            vacancy: Vacante.
            platform: Plataforma (linkedin, twitter, facebook).

        Returns:
            Contenido generado.
        """
        prompt = self._build_prompt(vacancy, platform)

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            return content
        except Exception as e:
            logger.error(f"Error calling LLM for {platform}: {e}")
            # Fallback a template básico
            return self._get_fallback_template(vacancy, platform)

    def _build_prompt(self, vacancy: JobVacancy, platform: str) -> str:
        """
        Construye el prompt específico para cada plataforma.

        Args:
            vacancy: Vacante.
            platform: Plataforma.

        Returns:
            Prompt para el LLM.
        """
        # Datos de la vacante
        vacancy_data = {
            "title": vacancy.title,
            "company": vacancy.tenant.name,
            "description": vacancy.description,
            "requirements": vacancy.requirements,
            "location": vacancy.location or "Remoto",
            "is_remote": vacancy.is_remote,
        }

        # Agregar salario si está disponible
        if vacancy.salary_min and vacancy.salary_max:
            vacancy_data[
                "salary_range"
            ] = f"{vacancy.salary_min}-{vacancy.salary_max} {vacancy.currency}"

        if platform == SocialPlatform.LINKEDIN:
            return self._linkedin_prompt(vacancy_data)
        elif platform == SocialPlatform.TWITTER:
            return self._twitter_prompt(vacancy_data)
        elif platform == SocialPlatform.FACEBOOK:
            return self._facebook_prompt(vacancy_data)
        else:
            return self._generic_prompt(vacancy_data)

    def _linkedin_prompt(self, vacancy_data: dict[str, Any]) -> str:
        """Prompt para LinkedIn - profesional y detallado."""
        return f"""Genera un post profesional para LinkedIn sobre esta oportunidad laboral.

Información de la vacante:
- Puesto: {vacancy_data['title']}
- Empresa: {vacancy_data['company']}
- Ubicación: {vacancy_data['location']}
- Descripción: {vacancy_data['description']}
- Requisitos: {vacancy_data['requirements']}
{f"- Rango salarial: {vacancy_data.get('salary_range', 'No especificado')}" if vacancy_data.get('salary_range') else ""}

Instrucciones:
- Usa un tono profesional pero amigable
- Resalta los aspectos más atractivos del puesto
- Incluye 3-5 hashtags relevantes de la industria
- Máximo 3000 caracteres
- Usa emojis profesionales (máximo 3)
- Incluye un call-to-action claro al final
- NO incluyas enlaces ni URLs

Genera SOLO el contenido del post, sin explicaciones adicionales."""

    def _twitter_prompt(self, vacancy_data: dict[str, Any]) -> str:
        """Prompt para Twitter - conciso e impactante."""
        return f"""Crea un tweet atractivo sobre esta oportunidad laboral.

Información de la vacante:
- Puesto: {vacancy_data['title']}
- Empresa: {vacancy_data['company']}
- Ubicación: {vacancy_data['location']}

Instrucciones:
- MÁXIMO 280 caracteres (CRÍTICO)
- Tono dinámico y llamativo
- Incluye 2-3 hashtags relevantes (#hiring, #jobs, etc.)
- Usa 1-2 emojis apropiados
- Debe ser conciso pero informativo
- NO incluyas enlaces

Genera SOLO el tweet, sin explicaciones adicionales."""

    def _facebook_prompt(self, vacancy_data: dict[str, Any]) -> str:
        """Prompt para Facebook - casual y amigable."""
        return f"""Escribe un post casual y amigable para Facebook sobre esta oportunidad laboral.

Información de la vacante:
- Puesto: {vacancy_data['title']}
- Empresa: {vacancy_data['company']}
- Ubicación: {vacancy_data['location']}
- Descripción: {vacancy_data['description']}

Instrucciones:
- Tono casual, amigable y cercano
- Usa emojis apropiados (3-5)
- Resalta los beneficios y aspectos positivos
- Incluye un call-to-action motivador
- Máximo 2000 caracteres
- NO incluyas enlaces ni URLs

Genera SOLO el contenido del post, sin explicaciones adicionales."""

    def _generic_prompt(self, vacancy_data: dict[str, Any]) -> str:
        """Prompt genérico para otras plataformas."""
        return f"""Genera un post sobre esta oportunidad laboral:

Puesto: {vacancy_data['title']}
Empresa: {vacancy_data['company']}
Ubicación: {vacancy_data['location']}
Descripción: {vacancy_data['description']}

Usa un tono profesional y atractivo. Máximo 500 caracteres."""

    def _get_fallback_template(self, vacancy: JobVacancy, platform: str) -> str:
        """
        Template de respaldo si falla el LLM.

        Args:
            vacancy: Vacante.
            platform: Plataforma.

        Returns:
            Contenido básico.
        """
        if platform == SocialPlatform.LINKEDIN:
            return (
                f"🚀 ¡Estamos contratando!\\n\\n"
                f"En {vacancy.tenant.name} buscamos un {vacancy.title} "
                f"para unirse a nuestro equipo.\\n\\n"
                f"{vacancy.description[:200]}...\\n\\n"
                f"📍 {vacancy.location or 'Remoto'}\\n\\n"
                f"#hiring #jobs #{vacancy.title.replace(' ', '')}"
            )
        elif platform == SocialPlatform.TWITTER:
            return (
                f"🌟 Buscamos {vacancy.title} en {vacancy.tenant.name}\\n"
                f"📍 {vacancy.location or 'Remoto'}\\n"
                f"#hiring #jobs"
            )
        elif platform == SocialPlatform.FACEBOOK:
            return (
                f"📢 ¡Nueva oportunidad en {vacancy.tenant.name}!\\n\\n"
                f"Buscamos: {vacancy.title}\\n\\n"
                f"{vacancy.description[:150]}...\\n\\n"
                f"¡Postúlate ahora! 🚀"
            )
        return f"Nueva vacante: {vacancy.title} en {vacancy.tenant.name}"
