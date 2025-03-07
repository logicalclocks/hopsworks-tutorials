import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
import streamlit as st

class QueryRefinementAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini-2024-07-18',
            temperature=0.2,
            api_key=os.environ['OPENAI_API_KEY'],
        )
        self.prompt = self._get_prompt()
        self.chain = self._get_chain()

    
    def _get_system_message(self):
        return (
            "You are an expert at refining queries to get better data.\n"
            "\n"
            "The previous attempt to get context for a user query was insufficient. Please refine the query to\n"
            "be more specific and targeted, focusing on what data might be missing.\n"
            "Write just a refined query, without any explanation.\n"
            "Important feature descriptions:\n"
            " - interaction_score: Type of interaction: 0 = ignore, 1 = click, 2 = purchase.\n"
            " - sales_channel_id: 1 = online, 2 = offline.\n"
        )
    

    def _get_human_message(self):
        return (
            "Original user query: {user_query}\n"
            "Current context data: {context}\n"
            "What's a better query that would get more complete information?\n"
        )
    

    def _get_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_message()),
                ("human", self._get_human_message()),
            ]
        )
    

    def _get_chain(self):
        return self.prompt | self.llm
    

    def refine_query(self, state):
        with st.spinner("👩🏻‍🔬 Refining Query..."):
            response = self.chain.invoke({
                "user_query": state["user_query"],
                "context": state["context"]
            }).content

            return Command(
                update={
                    "user_query": response
                },
                goto="generate_context",
            )


