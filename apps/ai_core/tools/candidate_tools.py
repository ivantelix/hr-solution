"""
Herramientas para análisis y procesamiento de candidatos.

Este módulo contiene tools para trabajar con datos de candidatos,
análisis de CVs, matching con vacantes, etc.
"""

from langchain_core.tools import tool

from .registry import ToolRegistry


@ToolRegistry.register("analyze_candidate_fit")
@tool
def analyze_candidate_fit(candidate_profile: dict, job_requirements: dict) -> dict:
    """
    Analiza qué tan bien un candidato encaja con una vacante.

    Args:
        candidate_profile: Perfil del candidato con skills y experiencia
        job_requirements: Requisitos de la vacante

    Returns:
        Dict con score de matching y análisis detallado

    Example:
        >>> result = analyze_candidate_fit(
        ...     candidate_profile={"skills": ["Python", "Django"]},
        ...     job_requirements={"required_skills": ["Python", "FastAPI"]}
        ... )
        >>> print(result["match_score"])
    """
    candidate_skills = {skill.lower() for skill in candidate_profile.get("skills", [])}
    required_skills = {
        skill.lower() for skill in job_requirements.get("required_skills", [])
    }

    # Calcular matching de skills
    matching_skills = candidate_skills.intersection(required_skills)
    match_percentage = (
        len(matching_skills) / len(required_skills) * 100 if required_skills else 0
    )

    # Analizar experiencia
    candidate_years = candidate_profile.get("experience_years", 0)
    required_years = job_requirements.get("min_experience_years", 0)
    experience_match = candidate_years >= required_years

    return {
        "match_score": round(match_percentage, 2),
        "matching_skills": list(matching_skills),
        "missing_skills": list(required_skills - candidate_skills),
        "extra_skills": list(candidate_skills - required_skills),
        "experience_match": experience_match,
        "candidate_years": candidate_years,
        "required_years": required_years,
        "recommendation": (
            "Strong match"
            if match_percentage >= 70
            else "Partial match"
            if match_percentage >= 40
            else "Weak match"
        ),
    }


@ToolRegistry.register("extract_cv_information")
@tool
def extract_cv_information(cv_text: str) -> dict:
    """
    Extrae información estructurada de un CV en texto plano.

    Args:
        cv_text: Texto del CV

    Returns:
        Dict con información extraída (nombre, skills, experiencia, etc.)

    Example:
        >>> info = extract_cv_information(cv_text)
        >>> print(info["skills"])
    """
    # TODO: Implementar con NLP o LLM para extracción real
    # Por ahora, retornamos estructura de ejemplo

    return {
        "name": "Extracted Name",
        "email": "candidate@example.com",
        "phone": "+58 412 1234567",
        "skills": ["Python", "Django", "PostgreSQL"],
        "experience": [
            {
                "company": "Company Name",
                "position": "Developer",
                "duration": "2020-2023",
            }
        ],
        "education": [
            {
                "institution": "University Name",
                "degree": "Computer Science",
                "year": "2019",
            }
        ],
        "languages": ["Spanish", "English"],
    }


@ToolRegistry.register("generate_candidate_summary")
@tool
def generate_candidate_summary(candidate_data: dict) -> str:
    """
    Genera un resumen ejecutivo de un candidato.

    Args:
        candidate_data: Datos completos del candidato

    Returns:
        String con resumen ejecutivo

    Example:
        >>> summary = generate_candidate_summary(candidate_data)
        >>> print(summary)
    """
    name = candidate_data.get("name", "Candidato")
    title = candidate_data.get("title", "Profesional")
    years = candidate_data.get("experience_years", 0)
    skills = candidate_data.get("skills", [])

    summary = f"""
{name} - {title}

Experiencia: {years} años

Habilidades principales:
{", ".join(skills[:5]) if skills else "No especificadas"}

Ubicación: {candidate_data.get("location", "No especificada")}

Perfil: {candidate_data.get("summary", "No disponible")}
    """.strip()

    return summary
