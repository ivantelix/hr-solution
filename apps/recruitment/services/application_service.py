"""
Servicio de aplicación para Application y Candidate.

Este módulo contiene los casos de uso relacionados con postulaciones
y gestión de candidatos.
"""

from django.db import transaction

from apps.recruitment.models import (
    Application,
    CandidateStatus,
)
from apps.recruitment.repositories import (
    ApplicationRepository,
    CandidateRepository,
    JobVacancyRepository,
)
from apps.tenants.repositories import TenantRepository


class ApplicationService:
    """
    Servicio de aplicación para gestión de postulaciones.

    Maneja el flujo completo desde la creación del candidato
    hasta la postulación y cambio de estados.
    """

    def __init__(
        self,
        application_repo: ApplicationRepository | None = None,
        candidate_repo: CandidateRepository | None = None,
        vacancy_repo: JobVacancyRepository | None = None,
        tenant_repo: TenantRepository | None = None,
    ):
        self.application_repo = application_repo or ApplicationRepository()
        self.candidate_repo = candidate_repo or CandidateRepository()
        self.vacancy_repo = vacancy_repo or JobVacancyRepository()
        self.tenant_repo = tenant_repo or TenantRepository()

    @transaction.atomic
    def apply_to_vacancy(
        self, vacancy_id: int, candidate_data: dict, source: str = "website"
    ) -> Application:
        """
        Registra una postulación (crea candidato si no existe).

        Args:
            vacancy_id: ID de la vacante.
            candidate_data: Datos del candidato (email, nombre, etc).
            source: Fuente de la postulación.

        Returns:
            Application: Postulación creada.

        Raises:
            ValueError: Si la vacante no existe o ya postuló.
        """
        vacancy = self.vacancy_repo.get_by_id(vacancy_id)
        if not vacancy:
            raise ValueError("La vacante no existe.")

        tenant_id = str(vacancy.tenant.id)
        email = candidate_data.get("email")

        # Buscar o crear candidato
        candidate = self.candidate_repo.get_by_email(tenant_id, email)
        if not candidate:
            candidate = self.candidate_repo.create(
                tenant=vacancy.tenant, **candidate_data
            )
        else:
            # Actualizar datos si es necesario
            self.candidate_repo.update(candidate, **candidate_data)

        # Verificar si ya postuló
        existing_app = self.application_repo.get_by_candidate_and_vacancy(
            candidate.id, vacancy.id
        )
        if existing_app:
            raise ValueError("El candidato ya postuló a esta vacante.")

        # Crear postulación
        application = self.application_repo.create(
            tenant=vacancy.tenant,
            vacancy=vacancy,
            candidate=candidate,
            source=source,
            status=CandidateStatus.NEW,
        )

        return application

    @transaction.atomic
    def update_status(
        self, application_id: int, new_status: CandidateStatus, notes: str | None = None
    ) -> Application | None:
        """
        Actualiza el estado de una postulación.

        Args:
            application_id: ID de la postulación.
            new_status: Nuevo estado.
            notes: Notas opcionales.

        Returns:
            Application | None: Postulación actualizada.
        """
        application = self.application_repo.get_by_id(application_id)
        if not application:
            return None

        # Actualizar estado
        self.application_repo.update_status(application, new_status)

        # Agregar notas si existen
        if notes:
            current_notes = application.notes or ""
            new_note_entry = f"\n[{new_status}]: {notes}"
            application.notes = current_notes + new_note_entry
            application.save(update_fields=["notes"])

        return application

    def get_vacancy_applications(self, vacancy_id: int) -> list[Application]:
        """Obtiene postulaciones de una vacante."""
        return list(self.application_repo.get_by_vacancy(vacancy_id))
