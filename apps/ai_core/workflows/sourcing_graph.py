from typing import TypedDict
import logging

from langgraph.graph import END, StateGraph

from ..services.usage_service import UsageService
from ..models.logs import AgentExecutionLog

logger = logging.getLogger(__name__)

# from langchain_core.messages import SystemMessage, HumanMessage
# from ..tools.registry import ToolRegistry


# Schema del Estado

# Schema del Estado
class AgentState(TypedDict):
    messages: list[str]
    vacancy_id: int
    context: dict
    final_output: dict
    is_qualified: bool  # Nuevo campo para control de flujo


class SourcingWorkflowBuilder:
    def __init__(self, llm, checkpoint_saver=None):
        self.llm = llm
        self.checkpoint_saver = checkpoint_saver

    def build(self):
        agent_configs = {
            "analyst": [],
            "sourcer": ["linkedin_search_tool"],
        }


        workflow = StateGraph(AgentState)

        workflow.add_node(
            "analyst", self._create_node("analyst", agent_configs)
        )
        workflow.add_node(
            "sourcer", self._create_node("sourcer", agent_configs)
        )

        workflow.set_entry_point("analyst")
        
        # Router condicional
        def route_analyst(state):
            if state.get("is_qualified", False):
                return "sourcer"
            return END

        workflow.add_conditional_edges(
            "analyst",
            route_analyst,
            {
                "sourcer": "sourcer",
                END: END
            }
        )
        
        workflow.add_edge("sourcer", END)

        if self.checkpoint_saver:
            return workflow.compile(checkpointer=self.checkpoint_saver)
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
            context = state.get("context", {})
            tenant_id = context.get("tenant_id")
            
            # Lógica Específica del Analista
            if agent_name == "analyst":
                analysis_type = context.get("analysis_type", "FLEXIBLE")
                
                # Responde SOLO un JSON con la estructura:
                # {{'qualified': bool, 'reason': str}}
                system_instruction = (
                    f"Eres un Analista de Reclutamiento. "
                    f"Tu trabajo es verificar los requisitos.\n"
                    f"MODO DE ANÁLISIS: {analysis_type}\n"
                    f"Si el modo es CRITICO, el candidato debe cumplir el "
                    f"100% de las tecnologías.\n"
                    f"Si el modo es FLEXIBLE, sé más permisivo.\n"
                    f"Responde SOLO un JSON con la estructura: "
                    f"{{'qualified': bool, 'reason': str}}"
                )

                # Inyección de mensaje de sistema (simulado en lista)
                # En producción usar SystemMessage real
                messages = [system_instruction] + state.get("messages", [])
            else:
                messages = state.get("messages", [])

            try:
                response = llm_bound.invoke(messages)
                output_content = response.content
                response_metadata = response.response_metadata
                
                # Procesar salida del analista
                if agent_name == "analyst":
                    # Aquí deberíamos parsear el JSON real
                    # Por simplicidad del ejemplo, asumimos que el LLM responde "qualified: True/False"
                    # o un JSON string.
                    # Simulación de parseo:
                    is_qualified = "true" in output_content.lower()
                    # Guardamos en el estado para el router
                    state["is_qualified"] = is_qualified

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

                return {"messages": [output_content], "is_qualified": state.get("is_qualified")}

            except Exception as e:
                logger.error(f"Error en nodo {agent_name}: {str(e)}")
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
