"""
Herramientas para comunicación por email.

Este módulo contiene tools para envío de emails a candidatos,
generación de templates, etc.
"""

from typing import Dict, Optional
from langchain_core.tools import tool
from .registry import ToolRegistry


@ToolRegistry.register("send_candidate_email")
@tool
def send_candidate_email(
    to_email: str,
    subject: str,
    body: str,
    tenant_id: str
) -> Dict:
    """
    Envía un email a un candidato.

    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        body: Cuerpo del email
        tenant_id: ID del tenant (para configuración de email)

    Returns:
        Dict con resultado del envío

    Example:
        >>> result = send_candidate_email(
        ...     to_email="candidate@example.com",
        ...     subject="Interview Invitation",
        ...     body="We would like to invite you...",
        ...     tenant_id="tenant-123"
        ... )
        >>> print(result["success"])
    """
    # TODO: Implementar integración real con servicio de email
    # (SendGrid, AWS SES, etc.)

    # Simulación de envío exitoso
    return {
        "success": True,
        "message_id": "msg_123456789",
        "to": to_email,
        "subject": subject,
        "sent_at": "2025-11-27T22:00:00Z",
    }


@ToolRegistry.register("generate_interview_invitation_email")
@tool
def generate_interview_invitation_email(
    candidate_name: str,
    position: str,
    interview_date: str,
    interview_time: str,
    company_name: str
) -> Dict:
    """
    Genera un email de invitación a entrevista.

    Args:
        candidate_name: Nombre del candidato
        position: Posición para la que se le invita
        interview_date: Fecha de la entrevista
        interview_time: Hora de la entrevista
        company_name: Nombre de la empresa

    Returns:
        Dict con subject y body del email

    Example:
        >>> email = generate_interview_invitation_email(
        ...     candidate_name="Juan Pérez",
        ...     position="Python Developer",
        ...     interview_date="2025-12-01",
        ...     interview_time="10:00 AM",
        ...     company_name="Tech Corp"
        ... )
        >>> print(email["subject"])
    """
    subject = f"Invitación a Entrevista - {position} en {company_name}"

    body = f"""
Estimado/a {candidate_name},

Nos complace informarle que ha sido seleccionado/a para una entrevista
para la posición de {position} en {company_name}.

Detalles de la entrevista:
- Fecha: {interview_date}
- Hora: {interview_time}
- Modalidad: Virtual (enlace será enviado próximamente)

Por favor, confirme su asistencia respondiendo a este correo.

Quedamos atentos a su confirmación.

Saludos cordiales,
Equipo de Reclutamiento
{company_name}
    """.strip()

    return {
        "subject": subject,
        "body": body,
    }


@ToolRegistry.register("generate_rejection_email")
@tool
def generate_rejection_email(
    candidate_name: str,
    position: str,
    company_name: str,
    personalized_feedback: Optional[str] = None
) -> Dict:
    """
    Genera un email de rechazo cordial.

    Args:
        candidate_name: Nombre del candidato
        position: Posición a la que aplicó
        company_name: Nombre de la empresa
        personalized_feedback: Feedback personalizado (opcional)

    Returns:
        Dict con subject y body del email

    Example:
        >>> email = generate_rejection_email(
        ...     candidate_name="María García",
        ...     position="Backend Developer",
        ...     company_name="Tech Corp"
        ... )
        >>> print(email["body"])
    """
    subject = f"Proceso de Selección - {position}"

    feedback_section = ""
    if personalized_feedback:
        feedback_section = f"\n\n{personalized_feedback}\n"

    body = f"""
Estimado/a {candidate_name},

Agradecemos sinceramente su interés en la posición de {position}
en {company_name} y el tiempo dedicado al proceso de selección.
{feedback_section}
Después de una cuidadosa evaluación, hemos decidido continuar con
otros candidatos cuyo perfil se ajusta más específicamente a las
necesidades actuales del puesto.

Valoramos mucho su experiencia y habilidades, y nos gustaría
mantener su perfil en nuestra base de datos para futuras
oportunidades que puedan ser de su interés.

Le deseamos mucho éxito en su búsqueda profesional.

Saludos cordiales,
Equipo de Reclutamiento
{company_name}
    """.strip()

    return {
        "subject": subject,
        "body": body,
    }
