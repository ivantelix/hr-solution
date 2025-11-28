from typing import TypedDict, List
from langgraph.graph import StateGraph, END
# from langchain_core.messages import SystemMessage, HumanMessage
# from ..tools.registry import ToolRegistry


# Schema del Estado
class AgentState(TypedDict):
    messages: List[str] # Simplificado para el ejemplo
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
        workflow.add_node(
            "analyst", self._create_node("analyst", agent_configs)
        )
        workflow.add_node(
            "sourcer", self._create_node("sourcer", agent_configs)
        )

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

        def node_func(state):
            # Lógica simple de invocación
            # prompt = f"Eres un {agent_name}... contexto: {state['context']}"
            # response = self.llm.invoke(...)
            return {"messages": [f"Agente {agent_name} ejecutado"]}

        return node_func
