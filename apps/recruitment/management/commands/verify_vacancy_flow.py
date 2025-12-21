"""
Comando para verificar el flujo de vacantes y posts sociales.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, TenantMembership
from apps.tenants.models.choices import TenantRole
from apps.recruitment.models import JobVacancy, SocialPlatform, SocialPostStatus
from apps.recruitment.services import JobVacancyService


class Command(BaseCommand):
    help = "Verifica el flujo de vacantes y posts sociales"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando verificación...")

        # 1. Setup Data
        User = get_user_model()
        user, _ = User.objects.get_or_create(username="verify_user", email="verify@example.com")
        tenant, created = Tenant.objects.get_or_create(
            slug="verify-tenant",
            defaults={"name": "Verify Tenant"}
        )
        
        # Ensure membership
        TenantMembership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={"role": TenantRole.ADMIN}
        )
        
        service = JobVacancyService()

        # 2. Create Vacancy
        self.stdout.write("Creando vacante...")
        vacancy = service.create_vacancy(
            tenant_id=str(tenant.id),
            user_id=user.id,
            title="Senior Python Developer",
            description="Great job opportunity",
            requirements="Python, Django, AWS",
            location="Remote"
        )
        self.stdout.write(f"Vacante creada: {vacancy.title} ({vacancy.status})")

        # 3. Generate Previews
        self.stdout.write("Generando previews...")
        posts = service.generate_social_previews(
            vacancy.id, [SocialPlatform.LINKEDIN, SocialPlatform.TWITTER]
        )
        
        if len(posts) != 2:
            self.stdout.write(self.style.ERROR(f"Error: Se esperaban 2 posts, se obtuvieron {len(posts)}"))
            return

        for post in posts:
            self.stdout.write(f"Post generado ({post.platform}): {post.status}")
            if post.status != SocialPostStatus.DRAFT:
                 self.stdout.write(self.style.ERROR("Error: El post debería estar en Borrador"))

        # 4. Publish
        self.stdout.write("Publicando vacante...")
        service.publish_vacancy(vacancy.id)
        
        vacancy.refresh_from_db()
        if vacancy.status != "published": # JobStatus.PUBLISHED
             self.stdout.write(self.style.ERROR(f"Error: Vacante status es {vacancy.status}"))
        
        # Verify posts published
        for post in vacancy.social_posts.all():
            if post.status != SocialPostStatus.PUBLISHED:
                self.stdout.write(self.style.ERROR(f"Error: Post {post.platform} status es {post.status}"))
            else:
                self.stdout.write(f"Post {post.platform} publicado correctamente.")

        self.stdout.write(self.style.SUCCESS("Verificación completada exitosamente."))
