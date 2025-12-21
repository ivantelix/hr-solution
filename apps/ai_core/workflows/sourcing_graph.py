from typing import TypedDict
import logging

from langgraph.graph import END, StateGraph
from langchain_core.messages import BaseMessage

from ..services.usage_service import UsageService
from ..models.logs import AgentExecutionLog

logger = logging.getLogger(__name__)

# from langchain_core.messages import SystemMessage, HumanMessage
# from ..tools.registry import ToolRegistry


# Schema del Estado
class AgentState(TypedDict):
    messages: list[str]  # Simplificado para el ejemplo
    vacancy_id: int
    context: dict
    final_output: dict


class SourcingWorkflowBuilder:
    def __init__(self, llm):
        self.llm = llm

    def build(self):
        # Configuración: Qué herramientas puede usar cada agente
        # Esto evita que el analista intente buscar en linkedin
        agent_configs = {
            "analyst": [],
            "sourcer": ["linkedin_search_tool"],
        }

        workflow = StateGraph(AgentState)

        # Nodos
        workflow.add_node("analyst", self._create_node("analyst", agent_configs))
        workflow.add_node("sourcer", self._create_node("sourcer", agent_configs))

        # Edges
        workflow.set_entry_point("analyst")
        workflow.add_edge("analyst", "sourcer")
        workflow.add_edge("sourcer", END)

        return workflow.compile()

    def _create_node(self, agent_name, configs):
        # 1. Obtener herramientas reales del registro
        # tool_names = configs.get(agent_name, [])

        # Nota: Aquí deberíamos convertir las funciones de python
        # a LangChain Tools
        # tools = [ToolRegistry.get_tool(name) for name in tool_names]

        # 2. Bind tools al LLM (si hay herramientas)
        # if tool_names:
        #     llm_bound = self.llm.bind_tools(tools)
        # else:
        #     llm_bound = self.llm
        
        # Simulamos llm bound para el ejemplo actual
        llm_bound = self.llm

        def node_func(state):
            # Obtener tenant_id del contexto
            context = state.get("context", {})
            tenant_id = context.get("tenant_id")
            
            try:
                # Prompt simple por ahora
                messages = state.get("messages", [])
                
                # Invocación real al LLM
                response = llm_bound.invoke(messages)
                
                # Obtener output y metadata reales
                output_content = response.content
                response_metadata = response.response_metadata
                
                # Registrar éxito
                if tenant_id:
                    UsageService.log_node_execution(
                        tenant_id=tenant_id,
                        workflow_name="sourcing_workflow",
                        node_name=agent_name,
                        input_data={"context": context},
                        output_data={"content": output_content},
                        metadata=response_metadata,
                        status=AgentExecutionLog.STATUS_SUCCESS
                    )

                return {"messages": [output_content]}

            except Exception as e:
                logger.error(f"Error en nodo {agent_name}: {str(e)}")
                # Registrar fallo
                if tenant_id:
                    UsageService.log_node_execution(
                        tenant_id=tenant_id,
                        workflow_name="sourcing_workflow",
                        node_name=agent_name,
                        input_data={"context": context},
                        output_data=None,
                        metadata={},
                        status=AgentExecutionLog.STATUS_FAILED,
                        error=str(e)
                    )
                raise e

        return node_func
