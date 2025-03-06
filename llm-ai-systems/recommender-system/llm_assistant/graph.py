from typing import List, Any, TypedDict, Literal, Optional
from langgraph.graph import StateGraph

from llm_assistant.agents.code_generation_agent import CodeGenerationAgent
from llm_assistant.agents.context_evaluation_agent import ContextEvaluationAgent
from llm_assistant.agents.query_refinement_agent import QueryRefinementAgent
from llm_assistant.agents.response_generator_agent import ResponseGeneratorAgent


class GraphState(TypedDict):
    user_query: str
    messages: List[Any]
    customer_id: str
    context: str
    context_quality: Literal["unknown", "insufficient", "good"]
    iterations: int
    max_iterations: int
    error_message: Optional[str]
    code: Optional[str]


def build_graph(data):
    code_generation_agent = CodeGenerationAgent(data)

    context_evaluation_agent = ContextEvaluationAgent()

    query_refinement_agent = QueryRefinementAgent()

    response_generator_agent = ResponseGeneratorAgent()

    # Initialize the graph
    workflow = StateGraph(GraphState)

    workflow.add_node("generate_context", code_generation_agent.generate_context)
    workflow.add_node("evaluate_context", context_evaluation_agent.evaluate_context)
    workflow.add_node("refine_query", query_refinement_agent.refine_query)
    workflow.add_node("generate_response", response_generator_agent.generate_response)

    workflow.set_entry_point("generate_context")

    return workflow.compile()