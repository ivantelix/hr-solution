Especificación Técnica: Módulo ai\_core (Motor de IA)
=====================================================

**Contexto:**Este módulo es el "cerebro" central y agnóstico de la plataforma SaaS. Su responsabilidad es orquestar flujos de trabajo multi-agente (usando LangGraph) y gestionar la conexión con diferentes proveedores de LLM (OpenAI, Claude) de forma dinámica por Tenant.

**Arquitectura:**

*   **Agnóstico:** No debe importar modelos de negocio de recruitment (como Candidate). Recibe datos crudos (strings, dicts).
    
*   **Multitenant:** Debe seleccionar el LLM y la API Key basándose en la configuración del Tenant.
    
*   **Pluggable:** Usa el patrón Factory para instanciar LLMs.
    
*   **Observabilidad:** Implementa hooks para monitoreo futuro (Langfuse) sin acoplamiento fuerte.
    

1\. Estructura de Directorios
-----------------------------

Por favor, genera la siguiente estructura de archivos dentro de apps/ai\_core/:

Plaintext

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   apps/ai_core/  ├── __init__.py  ├── apps.py                 # Configuración de la App Django  ├── models/                 # Modelos de Configuración y Logs  │   ├── __init__.py  │   ├── ai_config.py        # Configuración por Tenant (BYOK)  │   └── logs.py             # Auditoría de ejecución  ├── adapters/               # Adaptadores de Infraestructura (LLMs, Monitor)  │   ├── __init__.py  │   ├── llm_factory.py      # Factory para instanciar OpenAI/Claude  │   └── monitoring.py       # Factory para callbacks (Langfuse/LangSmith)  ├── tools/                  # Registro de Herramientas  │   ├── __init__.py  │   └── registry.py         # Decorador y Singleton para registrar tools  ├── workflows/              # Definición de Grafos (LangGraph)  │   ├── __init__.py  │   └── sourcing_graph.py   # Lógica del grafo de Sourcing  └── services/               # Capa de Servicio (Entrypoint)      ├── __init__.py      └── workflow_service.py # Orquestador principal   `

2\. Dependencias (requirements.txt)
-----------------------------------

Asegúrate de instalar las siguientes librerías:

Plaintext

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   langchain  langchain-openai  langchain-anthropic  langgraph  langfuse              # SDK para futuro monitoreo  redis                 # Para persistencia de estado (checkpoints)   `

3\. Implementación de Código
----------------------------

Genera los archivos con el siguiente contenido lógico:

### A. Modelos de Configuración (models/ai\_config.py)

Este modelo permite que cada cliente traiga su propia llave (BYOK) o use la de la plataforma.

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   from django.db import models  from django.conf import settings  # Asumimos que la app 'tenants' ya existe  from apps.tenants.models import Tenant  class TenantAIConfig(models.Model):      class LLMProvider(models.TextChoices):          PLATFORM_DEFAULT = "platform_default", "Default de la Plataforma"          OPENAI = "openai", "OpenAI"          CLAUDE = "claude", "Anthropic (Claude)"      tenant = models.OneToOneField(          Tenant,          on_delete=models.CASCADE,          related_name="ai_config"      )      provider = models.CharField(          max_length=50,          choices=LLMProvider.choices,          default=LLMProvider.PLATFORM_DEFAULT      )      # En producción, usar un campo encriptado (ej. django-fernet-fields)      api_key = models.CharField(max_length=255, blank=True, null=True)      model_name = models.CharField(max_length=100, default="gpt-4-turbo", help_text="Modelo específico a usar")      def __str__(self):          return f"AI Config para {self.tenant}"   `

### B. Factory de LLMs (adapters/llm\_factory.py)

Implementa el patrón Factory para devolver un objeto ChatModel de LangChain configurado.

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   from django.conf import settings  from langchain_openai import ChatOpenAI  from langchain_anthropic import ChatAnthropic  from ..models.ai_config import TenantAIConfig  def get_llm_for_tenant(tenant_config: TenantAIConfig):      """      Devuelve una instancia de LangChain ChatModel configurada      según las preferencias del tenant.      """      api_key = tenant_config.api_key      provider = tenant_config.provider      model_name = tenant_config.model_name      # Lógica de Fallback a las llaves globales de la plataforma      if provider == TenantAIConfig.LLMProvider.PLATFORM_DEFAULT:          # Aquí podrías definir tu lógica de default (ej. usar OpenAI)          provider = TenantAIConfig.LLMProvider.OPENAI          api_key = settings.OPENAI_API_KEY_GLOBAL      # 1. OpenAI      if provider == TenantAIConfig.LLMProvider.OPENAI:          final_key = api_key or settings.OPENAI_API_KEY_GLOBAL          return ChatOpenAI(api_key=final_key, model=model_name, temperature=0)      # 2. Claude      elif provider == TenantAIConfig.LLMProvider.CLAUDE:          final_key = api_key or settings.CLAUDE_API_KEY_GLOBAL          return ChatAnthropic(api_key=final_key, model=model_name, temperature=0)      raise ValueError(f"Proveedor de IA no soportado: {provider}")   `

### C. Adaptador de Monitoreo (adapters/monitoring.py)

Prepara el terreno para Langfuse sin romper el código actual.

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   import os  from django.conf import settings  from langchain_core.callbacks import StdOutCallbackHandler  # from langfuse.callback import CallbackHandler as LangfuseCallbackHandler  def get_workflow_monitor(trace_name: str, tenant_id: str, session_id: str = None) -> list:      """      Devuelve una lista de Callbacks para monitorear la ejecución.      """      callbacks = []      # 1. Logs de consola en desarrollo      if settings.DEBUG:          callbacks.append(StdOutCallbackHandler())      # 2. Hook para Langfuse (Descomentar en producción)      """      if os.environ.get("LANGFUSE_PUBLIC_KEY"):          langfuse_handler = LangfuseCallbackHandler(              secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),              public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),              host=os.environ.get("LANGFUSE_HOST"),              trace_name=trace_name,              user_id=str(tenant_id),              session_id=session_id          )          callbacks.append(langfuse_handler)      """      return callbacks   `

### D. Registro de Tools (tools/registry.py)

Un sistema simple para registrar funciones de Python como herramientas disponibles.

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   from typing import Callable, Dict  class ToolRegistry:      _registry: Dict[str, Callable] = {}      @classmethod      def register(cls, name: str):          """Decorador para registrar una herramienta."""          def decorator(func):              cls._registry[name] = func              return func          return decorator      @classmethod      def get_tool(cls, name: str, tenant_id: str = None):          """          Obtiene la herramienta y (opcionalmente) inyecta el tenant_id          si la herramienta lo requiere (Currying/Partial).          """          func = cls._registry.get(name)          if not func:              raise ValueError(f"Herramienta '{name}' no registrada en ai_core.")          # Aquí podrías aplicar lógica para inyectar tenant_id automáticamente          # si la función lo espera. Por ahora devolvemos la función cruda          # envuelta en una StructuredTool de LangChain.          return func   `

### E. Constructor del Grafo (workflows/sourcing\_graph.py)

Implementa la lógica de LangGraph con "Tool Scoping" (asignando herramientas específicas por nodo).

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   from typing import TypedDict, List  from langgraph.graph import StateGraph, END  from langchain_core.messages import SystemMessage, HumanMessage  from ..tools.registry import ToolRegistry  # Schema del Estado  class AgentState(TypedDict):      messages: List[str] # Simplificado para el ejemplo      vacancy_id: int      context: dict      final_output: dict  class SourcingWorkflowBuilder:      def __init__(self, llm):          self.llm = llm      def build(self):          # Configuración: Qué herramientas puede usar cada agente          # Esto evita que el analista intente buscar en linkedin          agent_configs = {              "analyst": [],               "sourcer": ["linkedin_search_tool"], # Nombre registrado en registry          }          workflow = StateGraph(AgentState)          # Nodos          workflow.add_node("analyst", self._create_node("analyst", agent_configs))          workflow.add_node("sourcer", self._create_node("sourcer", agent_configs))          # Edges          workflow.set_entry_point("analyst")          workflow.add_edge("analyst", "sourcer")          workflow.add_edge("sourcer", END)          return workflow.compile()      def _create_node(self, agent_name, configs):          # 1. Obtener herramientas reales del registro          tool_names = configs.get(agent_name, [])          # Nota: Aquí deberíamos convertir las funciones de python a LangChain Tools          # tools = [ToolRegistry.get_tool(name) for name in tool_names]          # 2. Bind tools al LLM (si hay herramientas)          if tool_names:              # llm_bound = self.llm.bind_tools(tools)              llm_bound = self.llm # Placeholder hasta tener tools reales          else:              llm_bound = self.llm          def node_func(state):              # Lógica simple de invocación              # prompt = f"Eres un {agent_name}... contexto: {state['context']}"              # response = llm_bound.invoke(...)              return {"messages": [f"Agente {agent_name} ejecutado"]}          return node_func   `

### F. Servicio Principal (services/workflow\_service.py)

El punto de entrada que une todo.

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   from ..models.ai_config import TenantAIConfig  from ..adapters.llm_factory import get_llm_for_tenant  from ..adapters.monitoring import get_workflow_monitor  from ..workflows.sourcing_graph import SourcingWorkflowBuilder  def start_sourcing_workflow(tenant_id: str, vacancy_id: int, job_data: dict):      """      Orquesta la ejecución del workflow.      """      # 1. Obtener Configuración del Tenant      try:          config = TenantAIConfig.objects.get(tenant_id=tenant_id)      except TenantAIConfig.DoesNotExist:          # Crear config default en memoria o lanzar error          raise ValueError("Tenant no tiene configuración de IA")      # 2. Instanciar el LLM correcto (Factory)      llm = get_llm_for_tenant(config)      # 3. Construir el Grafo      builder = SourcingWorkflowBuilder(llm=llm)      app = builder.build()      # 4. Configurar Monitoreo      monitor = get_workflow_monitor(          trace_name=f"Sourcing Vacancy {vacancy_id}",          tenant_id=str(tenant_id)      )      # 5. Estado Inicial      initial_state = {          "vacancy_id": vacancy_id,          "context": job_data,          "messages": []      }      # 6. Ejecutar      result = app.invoke(          initial_state,          config={"callbacks": monitor}      )      return result   `