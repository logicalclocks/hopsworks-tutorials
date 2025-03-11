import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
import streamlit as st


class ContextEvaluatorSchema(BaseModel):
    """Evaluate context quality for answering user queries."""
    quality: str = Field(
        description="The quality of the context data.",
        examples=["good", "insufficient"],
    )

class ContextEvaluationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini-2024-07-18',
            temperature=0,
            api_key=os.environ['OPENAI_API_KEY'],
        )
        self.prompt = self._get_prompt()
        self.chain = self._get_chain()

    
    def _get_system_message(self):
        return (
            "You are an expert at evaluating data context quality for answering user queries.\n"
            "You are given:\n"
            "1. A user's query about their purchase history or preferences\n"
            "2. The context data that was generated to answer the query\n"
            "\n"
            "Your task is to determine if the context provides sufficient information to fully answer the query.\n"
            "Return 'good' if the context is sufficient, or 'insufficient' if more data is needed.\n"
        )


    def _get_human_message(self):
        return (
            "User query: {user_query}\n"
            "Context data: {context}\n"
            "Is this context sufficient to answer the query?\n"
        )
    

    def _get_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_message()),
                ("human", self._get_human_message()),
            ]
        )
    

    def _get_chain(self):
        return self.prompt | self.llm.with_structured_output(ContextEvaluatorSchema)
    

    def evaluate_context(self, state):
        with st.spinner("👨🏻‍⚖️ Evaluating Context..."):
            response = self.chain.invoke({
                "user_query": state["user_query"],
                "context": state["context"],
            })

            context_quality = response["quality"]

            if context_quality == "good":
                next_node = "generate_response"

            elif state["iterations"] >= state["max_iterations"]:
                # We've tried enough times, just generate a response with what we have
                next_node = "generate_response"

            else:
                next_node = "refine_query"

            return Command(
                update={
                    "context_quality": context_quality,
                },
                goto=next_node,
            )