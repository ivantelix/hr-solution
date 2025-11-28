"""
Ejemplo completo de uso del módulo AI Core.

Este script demuestra cómo usar el sistema de tools y workflows
en un caso de uso real: sourcing de candidatos.
"""

from apps.ai_core.tools import ToolRegistry
from apps.ai_core.services.workflow_service import start_sourcing_workflow


def ejemplo_1_usar_tool_individual():
    """Ejemplo 1: Usar una tool individual."""
    print("=" * 60)
    print("EJEMPLO 1: Usar una tool individual")
    print("=" * 60)

    # Obtener la tool del registro
    search_tool = ToolRegistry.get_tool("linkedin_search_tool")

    # Invocar la tool
    result = search_tool.invoke({
        "query": "Python Developer Senior",
        "location": "Caracas, Venezuela",
        "max_results": 5
    })

    # Mostrar resultados
    print(f"\nBúsqueda: {result['query']}")
    print(f"Ubicación: {result['location']}")
    print(f"Candidatos encontrados: {result['total_results']}\n")

    for i, profile in enumerate(result['profiles'], 1):
        print(f"{i}. {profile['name']}")
        print(f"   Título: {profile['title']}")
        print(f"   LinkedIn: {profile['linkedin_url']}")
        print(f"   Experiencia: {profile['experience_years']} años")
        print()


def ejemplo_2_analizar_candidato():
    """Ejemplo 2: Analizar fit de un candidato."""
    print("=" * 60)
    print("EJEMPLO 2: Analizar fit de candidato con vacante")
    print("=" * 60)

    # Obtener la tool de análisis
    analyze_tool = ToolRegistry.get_tool("analyze_candidate_fit")

    # Datos del candidato
    candidate = {
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "experience_years": 6
    }

    # Requisitos de la vacante
    job_requirements = {
        "required_skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
        "min_experience_years": 4
    }

    # Analizar
    result = analyze_tool.invoke({
        "candidate_profile": candidate,
        "job_requirements": job_requirements
    })

    # Mostrar resultados
    print(f"\nMatch Score: {result['match_score']}%")
    print(f"Recomendación: {result['recommendation']}")
    print(f"\nSkills que coinciden:")
    for skill in result['matching_skills']:
        print(f"  ✓ {skill}")

    print(f"\nSkills faltantes:")
    for skill in result['missing_skills']:
        print(f"  ✗ {skill}")

    print(f"\nSkills adicionales del candidato:")
    for skill in result['extra_skills']:
        print(f"  + {skill}")

    print(f"\nExperiencia: {result['candidate_years']} años "
          f"(requerido: {result['required_years']})")
    print(f"Cumple experiencia: {'Sí' if result['experience_match'] else 'No'}")


def ejemplo_3_generar_email():
    """Ejemplo 3: Generar email de invitación."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Generar email de invitación a entrevista")
    print("=" * 60)

    # Obtener la tool de generación de email
    email_tool = ToolRegistry.get_tool(
        "generate_interview_invitation_email"
    )

    # Generar email
    email = email_tool.invoke({
        "candidate_name": "Juan Pérez",
        "position": "Senior Python Developer",
        "interview_date": "2025-12-05",
        "interview_time": "10:00 AM",
        "company_name": "Tech Solutions Corp"
    })

    # Mostrar email
    print(f"\nAsunto: {email['subject']}")
    print("\nCuerpo:")
    print("-" * 60)
    print(email['body'])
    print("-" * 60)


def ejemplo_4_workflow_completo():
    """Ejemplo 4: Ejecutar workflow completo de sourcing."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Workflow completo de sourcing")
    print("=" * 60)

    # Datos de la vacante
    job_data = {
        "title": "Senior Python Developer",
        "description": """
        Buscamos un desarrollador Python senior con experiencia
        en Django y FastAPI para liderar proyectos de backend.
        """,
        "requirements": [
            "Python",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "AWS"
        ],
        "location": "Caracas, Venezuela (Remoto)",
        "experience_years": 5
    }

    print("\nVacante:")
    print(f"  Título: {job_data['title']}")
    print(f"  Ubicación: {job_data['location']}")
    print(f"  Experiencia requerida: {job_data['experience_years']} años")
    print(f"  Skills requeridas: {', '.join(job_data['requirements'])}")

    print("\nEjecutando workflow de sourcing...")
    print("(Esto invocaría el workflow real con LangGraph)")

    # En un caso real, ejecutarías:
    # result = start_sourcing_workflow(
    #     tenant_id="tenant-uuid-123",
    #     vacancy_id=456,
    #     job_data=job_data
    # )

    print("\n✓ Workflow completado")
    print("✓ Candidatos encontrados: 5")
    print("✓ Candidatos analizados: 5")
    print("✓ Candidatos recomendados: 3")


def ejemplo_5_listar_tools_disponibles():
    """Ejemplo 5: Listar todas las tools disponibles."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Tools disponibles en el sistema")
    print("=" * 60)

    tools = ToolRegistry._registry.keys()

    print(f"\nTotal de tools registradas: {len(tools)}\n")

    # Agrupar por categoría
    categories = {
        "LinkedIn": [],
        "Candidatos": [],
        "Email": [],
        "Otras": []
    }

    for tool_name in tools:
        if "linkedin" in tool_name:
            categories["LinkedIn"].append(tool_name)
        elif any(x in tool_name for x in ["candidate", "cv", "fit"]):
            categories["Candidatos"].append(tool_name)
        elif "email" in tool_name:
            categories["Email"].append(tool_name)
        else:
            categories["Otras"].append(tool_name)

    for category, tool_list in categories.items():
        if tool_list:
            print(f"{category}:")
            for tool_name in sorted(tool_list):
                print(f"  • {tool_name}")
            print()


def main():
    """Ejecuta todos los ejemplos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "EJEMPLOS DE USO - AI CORE MODULE" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        ejemplo_1_usar_tool_individual()
        ejemplo_2_analizar_candidato()
        ejemplo_3_generar_email()
        ejemplo_4_workflow_completo()
        ejemplo_5_listar_tools_disponibles()

        print("\n" + "=" * 60)
        print("TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Para ejecutar este ejemplo:
    # python -m apps.ai_core.examples.usage_examples
    main()
